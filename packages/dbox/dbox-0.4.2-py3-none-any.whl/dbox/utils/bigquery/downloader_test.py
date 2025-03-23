import polars as pl
import pytest
from google.cloud import bigquery

from .downloader import BigQueryDownloader

pytest.skip("skip", allow_module_level=True)


@pytest.fixture(scope="module")
def downloader(bqclient):
    return BigQueryDownloader(bqclient)


@pytest.fixture(scope="module")
def table():
    return bigquery.TableReference.from_string("vix-one.temp_sg.treatments")


# BIGNUMERIC (32 bytes) is not supported by polars
def select_fields(schema):
    return [field.name for field in schema if field.field_type not in "BIGNUMERIC"]


def test_basic(downloader: BigQueryDownloader, table: bigquery.TableReference):
    data = downloader.download_table(
        table,
        max_rows=100,
        select_fields=select_fields,
    )
    df = pl.from_arrow(data)
    print(df.head())


def test_filter_fields(downloader: BigQueryDownloader, table: bigquery.TableReference):
    data = downloader.download_table(
        table,
        max_rows=100,
        select_fields=select_fields,
        row_restriction="FinalStage > 1",
    )
    df = pl.from_arrow(data)
    print(df.head())
