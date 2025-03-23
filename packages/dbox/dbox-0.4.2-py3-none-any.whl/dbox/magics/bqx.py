from __future__ import print_function

import logging
import shlex
from typing import List, Optional

import duckdb
import IPython
import polars as pl
import pyarrow as pa
from google.cloud import bigquery
from humanfriendly import format_size
from IPython.core.interactiveshell import InteractiveShell
from IPython.core.magic_arguments import MagicArgumentParser
from pydantic import BaseModel, ConfigDict, Field, field_validator

from dbox.ctx import use_key, use_type
from dbox.templater import to_template
from dbox.utils.bigquery.downloader import BigQueryDownloader
from dbox.utils.bigquery.tracker import ProgressTracker, TqdmTracker

log = logging.getLogger(__name__)

count = 0
bqlparser = MagicArgumentParser()
bqlparser.add_argument("--max-rows", "-n", type=int, default=None)
bqlparser.add_argument("--copy", "-c", action="store_true", default=False)

DEFAULT_PROGRESS_TRACKER = TqdmTracker(tqdm_type="std")


class MagicsContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    dest_table: Optional[str] = None

    project: Optional[str] = None
    dataset: Optional[str] = None
    max_rows: Optional[int] = None
    filter: Optional[str] = None
    exclude_fields: Optional[List[str]] = Field(default=None)
    exclude_tagged_columns: bool = False
    include_fields: Optional[List[str]] = None
    # query
    dry_run: bool = False
    max_gbs: Optional[int] = 20

    # copy
    max_rows_copy: int = 2 << 10

    @field_validator("exclude_fields", "include_fields", mode="before")
    @classmethod
    def to_list(cls, v: str):
        if v is None:
            return None
        return [e.strip() for e in v.split(",")]

    @field_validator("dry_run", "exclude_tagged_columns", mode="before")
    @classmethod
    def to_bool(cls, v: str):
        if v is None:
            return False
        if isinstance(v, bool):
            return v
        return v.lower() in ("true", "yes", "1")

    def update(self, **kwargs):
        data = self.model_dump()
        for k in kwargs:
            if k not in data:
                raise ValueError(f"Unknown directive: {k}")
        data.update(kwargs)
        return MagicsContext(**data)

    def run_query(self, sql_query: str, return_arrow=False):  # noqa: C901
        # a query
        bqjob = None
        bqclient = use_type(bigquery.Client)
        query_lowercase = sql_query.lower()
        if " " not in query_lowercase.strip():
            # must be a table reference
            table = bqclient.get_table(sql_query.strip())

        else:
            # a sql query
            config = bigquery.QueryJobConfig()
            config.dry_run = self.dry_run
            query_parameters = use_key("bqx_query_parameters", None)
            if query_parameters:
                config.query_parameters = query_parameters
            config.maximum_bytes_billed = self.max_gbs * 2**30
            try:
                bqjob = bqclient.query(sql_query, job_config=config)
                bqjob.result()
            except Exception as e:
                log.error("Query failed: %s", e)
                return

            log.info(
                "Query: [%s] - total billed %s - total processed %s - %s",
                bqjob.job_id,
                format_size(bqjob.total_bytes_billed),
                format_size(bqjob.total_bytes_processed),
                bqjob.project,
            )
            if self.dry_run:
                log.info("Dry run query completed.")
                return None
            table = bqjob.destination

        if self.max_rows is None:
            if use_key("bqx_max_rows", None, tpe=int) is not None:
                max_rows = use_key("bqx_max_rows", tpe=int)
            else:
                max_rows = 2 << 10

        else:
            max_rows = self.max_rows
        # download the table
        table: bigquery.Table = bqclient.get_table(table)
        if table.num_rows > max_rows:
            log.warning("Table has %d rows, downloading only %d rows.", table.num_rows, max_rows)

        def select_fields(fields: List[bigquery.SchemaField]):
            if self.include_fields:
                return [e.name for e in fields if e.name in self.include_fields]
            if self.exclude_fields:
                return [e.name for e in fields if e.name not in self.exclude_fields]
            if self.exclude_tagged_columns:
                return [e.name for e in fields if not e.policy_tags]
            return [e.name for e in fields]

        tracker = use_type(ProgressTracker, DEFAULT_PROGRESS_TRACKER)
        bqdownloader = BigQueryDownloader(bqclient=bqclient, tracker=tracker)
        arrow_table = bqdownloader.download_table(
            table,
            max_rows=max_rows,
            row_restriction=self.filter,
            select_fields=select_fields,
        )
        if return_arrow:
            return arrow_table
        arrow_table = pa.Table.from_batches(
            arrow_table.to_batches(), schema=pa.schema([field.remove_metadata() for field in arrow_table.schema])
        )
        df = pl.from_arrow(arrow_table)
        return df, bqjob


def bqx_magic(line, content: str):  # noqa: C901
    ctx = MagicsContext()
    global count  # noqa: PLW0603
    count += 1

    args = vars(bqlparser.parse_args(shlex.split(line)))
    if args["max_rows"] is not None:
        ctx.max_rows = int(args["max_rows"])

    ipy: InteractiveShell = IPython.get_ipython()
    directives = {}
    query_lines = []
    for line in content.splitlines():
        if line.strip().startswith("--") or line.strip().startswith("###"):
            continue  # ignore comment
        if line.strip().startswith("#") and "=" in line:
            k, v = line.strip().lstrip("# ").split("=", 1)
            k, v = k.strip(), v.strip()
            k = k.replace("-", "_")
            directives[k] = v
        else:
            query_lines.append(line)
    sql_query = "\n".join(query_lines)

    # aliases
    for k, v in {
        "exclude": "exclude_fields",
        "include": "include_fields",
        "dest": "dest_table",
        "n": "max_rows",
        "dry-run": "dry_run",
        "no-tagged": "exclude_tagged_columns",
        "max-gbs": "max_gbs",
    }.items():
        if k in directives:
            directives[v] = directives.pop(k)
    log.debug("Using directives: %s", directives)
    ctx = ctx.update(**directives)
    # sql_gen_ctx = use_type(SqlGenContext, default=DEFAULT_SQL_GEN_CONTEXT)
    sql_query = to_template(sql_query).render(ipy.ns_table["user_global"]).strip()
    log.debug("Using context: %s", ctx)
    ret = ctx.run_query(sql_query)
    if ret is None:
        return None
    else:
        df, bqjob = ret
    result_name = "b%d" % count
    bqjob_name = "bq%d" % count
    ipy.push({result_name: df, bqjob_name: bqjob})
    log.info("Stored result into %s.", result_name)
    if args["copy"]:
        df.slice(0, ctx.max_rows_copy).write_clipboard(separator=",")
    duckdb_conn = use_type(duckdb.DuckDBPyConnection, None)
    if duckdb_conn is not None:
        duckdb_conn.sql(f"CREATE OR REPLACE TEMP TABLE {result_name} AS SELECT * FROM df")
        if ctx.dest_table:
            ipy.push({ctx.dest_table: df})
            duckdb_conn.sql(f"CREATE OR REPLACE TABLE {ctx.dest_table} AS SELECT * FROM df")
        duck_relation = duckdb_conn.table(result_name)
        return duck_relation
    return df
