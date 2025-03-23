import logging
import queue
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Generator, List, Optional, Union

import pyarrow
from google.cloud import bigquery, bigquery_storage
from google.cloud.bigquery import _pandas_helpers
from google.cloud.bigquery_storage_v1.types import DataFormat, ReadSession

from .tracker import ProgressTracker, TqdmTracker

log = logging.getLogger(__name__)


class BigQueryDownloader:
    def __init__(
        self,
        bqclient: bigquery.Client,
        bqstorage: bigquery_storage.BigQueryReadClient = None,
        tracker: ProgressTracker = None,
    ) -> None:
        self.bqclient = bqclient
        self.bqstorage = bqstorage or bqclient._ensure_bqstorage_client()
        self.project = bqclient.project
        assert self.project, "project of bqclient must be set"
        self.tracker = tracker or TqdmTracker()

    def stream_table(
        self,
        table: Union[bigquery.TableReference, bigquery.Table, str],
        selected_fields: List[str] = None,
        row_restriction: str = None,
    ) -> Generator[pyarrow.RecordBatch, None, None]:
        if not isinstance(table, bigquery.Table):
            table = self.bqclient.get_table(table)
        selected_fields = selected_fields if selected_fields else [e.name for e in table.schema]
        project_id = table.project
        dataset_id = table.dataset_id
        table_id = table.table_id
        table_path = f"projects/{project_id}/datasets/{dataset_id}/tables/{table_id}"

        # Select columns to read with read options. If no read options are
        # specified, the whole table is read.
        read_options = ReadSession.TableReadOptions(
            selected_fields=selected_fields,
            row_restriction=row_restriction,
        )

        parent = "projects/{}".format(self.project)

        requested_session = ReadSession(
            table=table_path,
            # Avro is also supported, but the Arrow data format is optimized to
            # work well with column-oriented data structures such as pandas
            # DataFrames.
            data_format=DataFormat.ARROW,
            read_options=read_options,
        )
        log.debug("creating read session")
        read_session = self.bqstorage.create_read_session(
            parent=parent,
            read_session=requested_session,
            max_stream_count=10,
        )
        log.debug("created read session with total %s streams", len(read_session.streams))
        num_streams = len(read_session.streams)

        if num_streams > 0:
            stream = download_read_session(read_session, self.bqstorage)
            yield from stream
            stream.close()

    def download_table(
        self,
        table: Union[bigquery.TableReference, bigquery.Table, str],
        *,
        max_rows: int = None,
        select_fields: Optional[Callable[[List[bigquery.SchemaField]], List[str]]] = None,
        row_restriction: str = None,
        # exclude_fields: Optional[List[str]] = None,
        # exclude_tagged_columns: bool = True,
    ) -> pyarrow.Table:
        if not isinstance(table, bigquery.Table):
            table = self.bqclient.get_table(table)

        log.debug("Downloading table %s with filter %s", table.full_table_id, row_restriction)
        if select_fields is None:
            selected_fields = [e.name for e in table.schema]
        else:
            selected_fields = select_fields(table.schema)
            # if exclude_fields:
            #     selected_fields = [f for f in selected_fields if f not in exclude_fields]
            # if exclude_tagged_columns:
            #     tagged_columns = {e.name for e in table.schema if e.policy_tags}
            #     if tagged_columns:
            #         log.info("excluding tagged columns: %s", tagged_columns)
            #     selected_fields = [f for f in selected_fields if f not in tagged_columns]

        stream = self.stream_table(
            table=table,
            selected_fields=selected_fields,
            row_restriction=row_restriction,
        )
        num_rows = min(table.num_rows, max_rows or table.num_rows)

        if num_rows < table.num_rows:
            log.debug("Downloading %s rows (total rows: %s).", num_rows, table.num_rows)
        else:
            log.debug("Downloading %s rows.", table.num_rows)

        self.tracker.start(total=num_rows)
        record_batches = []
        downloaded = 0
        for record_batch in stream:
            record_batches.append(record_batch)
            downloaded += record_batch.num_rows
            self.tracker.update_progress(downloaded)
            if downloaded >= num_rows:
                break

        # Indicate that the download has finished.
        self.tracker.done()

        if record_batches and self.bqstorage is not None:
            # arrow_schema = _pandas_helpers.bq_to_arrow_schema(
            #     [field for field in table.schema if field.name in selected_fields]
            # )  # ???
            return pyarrow.Table.from_batches(record_batches)
        else:
            # No records (not record_batches), use schema based on BigQuery schema
            # **or**
            # we used the REST API (bqstorage_client is None),
            # which doesn't add arrow extension metadata, so we let
            # `bq_to_arrow_schema` do it.
            arrow_schema = _pandas_helpers.bq_to_arrow_schema(table.schema)
            return pyarrow.Table.from_batches(record_batches, schema=arrow_schema)


def download_read_session(  # noqa: C901
    session: ReadSession, bqstorage_client: bigquery_storage.BigQueryReadClient
) -> Generator[pyarrow.RecordBatch, None, None]:
    _PROGRESS_INTERVAL = 0.2  # Maximum time between download status checks, in seconds.  # noqa: N806
    streams = session.streams
    total_streams = len(streams)

    class _DownloadState(object):
        """Flag to indicate that a thread should exit early."""

        def __init__(self):
            # No need for a lock because reading/replacing a variable is defined to
            # be an atomic operation in the Python language definition (enforced by
            # the global interpreter lock).
            self.done = False

    def _nowait(futures):
        """Separate finished and unfinished threads, much like
        :func:`concurrent.futures.wait`, but don't wait.
        """
        done = []
        not_done = []
        for future in futures:
            if future.done():
                done.append(future)
            else:
                not_done.append(future)
        return done, not_done

    # Use _DownloadState to notify worker threads when to quit.
    # See: https://stackoverflow.com/a/29237343/101923
    download_state = _DownloadState()

    # Create a queue to collect frames as they are created in each thread.
    #
    # The queue needs to be bounded by default, because if the user code processes the
    # fetched result pages too slowly, while at the same time new pages are rapidly being
    # fetched from the server, the queue can grow to the point where the process runs
    # out of memory.
    max_queue_size = 10000  # len(streams)

    worker_queue = queue.Queue(maxsize=max_queue_size)

    def download(stream):
        reader = bqstorage_client.read_rows(stream.name)

        # Parse all Arrow blocks and create a dataframe.
        for message in reader.rows().pages:
            if download_state.done:
                return
            record_batch = message.to_arrow()
            worker_queue.put(record_batch)

    with ThreadPoolExecutor(max_workers=total_streams) as pool:
        try:
            # Manually submit jobs and wait for download to complete rather
            # than using pool.map because pool.map continues running in the
            # background even if there is an exception on the main thread.
            # See: https://github.com/googleapis/google-cloud-python/pull/7698
            not_done = [pool.submit(download, stream) for stream in streams]

            while not_done:
                # Don't block on the worker threads. For performance reasons,
                # we want to block on the queue's get method, instead. This
                # prevents the queue from filling up, because the main thread
                # has smaller gaps in time between calls to the queue's get
                # method. For a detailed explaination, see:
                # https://friendliness.dev/2019/06/18/python-nowait/
                done, not_done = _nowait(not_done)
                for future in done:
                    # Call result() on any finished threads to raise any
                    # exceptions encountered.
                    future.result()

                try:
                    frame: pyarrow.RecordBatch = worker_queue.get(timeout=_PROGRESS_INTERVAL)
                    yield frame
                except queue.Empty:  # pragma: NO COVER
                    continue

            # Return any remaining values after the workers finished.
            while True:  # pragma: NO COVER
                try:
                    frame = worker_queue.get_nowait()
                    yield frame
                except queue.Empty:  # pragma: NO COVER
                    break
        finally:
            # No need for a lock because reading/replacing a variable is
            # defined to be an atomic operation in the Python language
            # definition (enforced by the global interpreter lock).
            download_state.done = True

            # Shutdown all background threads, now that they should know to
            # exit early.
            pool.shutdown(wait=True)
