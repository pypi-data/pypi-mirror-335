import logging
import re
from functools import cached_property
from urllib.parse import urljoin

import bs4
import duckdb
import httpx
import polars as pl
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.v18.services.services.google_ads_field_service import GoogleAdsFieldServiceClient
from google.ads.googleads.v18.services.services.google_ads_service import GoogleAdsServiceClient
from google.ads.googleads.v18.services.types import google_ads_field_service, google_ads_service
from google.auth.credentials import Credentials, TokenState
from google.auth.transport.requests import Request
from google.protobuf.json_format import MessageToDict
from httpx import Auth
from pydantic import BaseModel

invalid_name_pt = re.compile(r"[^a-zA-Z0-9_]+")
log = logging.getLogger(__name__)


class GaqlResource(BaseModel):
    resource_type: str
    description: str


class GAdsStore:
    META_RESOURCE_TABLE = "meta_resource"
    META_RESOURCE_FIELD_TABLE = "meta_resource_field"

    def __init__(self, db: duckdb.DuckDBPyConnection, *, schema: str = "main"):
        self.db = db
        self.schema = schema
        self.db.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
        self.db.execute(f"USE {schema}")

    def initialize(self):
        self.db.execute(f"""
            create table if not exists {self.META_RESOURCE_TABLE} (
                resource_type VARCHAR,
                description VARCHAR,
                primary key (resource_type)
            )
        """)
        self.db.execute(f"""
            create table if not exists {self.META_RESOURCE_FIELD_TABLE} (
                resource_type VARCHAR,
                field_name VARCHAR,
                field_description VARCHAR,
                category VARCHAR,
                data_type VARCHAR,
                type_url VARCHAR,
                filterable BOOLEAN,
                selectable BOOLEAN,
                sortable BOOLEAN,
                repeated BOOLEAN,
                primary key (resource_type, field_name)
            )
        """)

    def insert(self, name: str, df: pl.DataFrame, drop: bool = False):
        # drop any struct columns that has no fields
        if drop:
            self.db.execute(f"CREATE OR REPLACE TABLE {name} AS SELECT * FROM df")
        else:
            columns = df.columns
            self.db.execute(f"INSERT OR REPLACE INTO {name} ({', '.join(columns)}) SELECT {', '.join(columns)} FROM df")

    def query(self, sql: str, params: object = None):
        return self.db.sql(sql, params=params)

    def relation(self, name: str):
        return self.db.sql(f"SELECT * FROM {name}")

    def iter_rows(self, *, sql: str = None, table: str = None):
        if table is not None:
            sql = f"SELECT * FROM {table}"
        return self.db.sql(sql).pl().iter_rows(named=True)

    def exists(self, table: str):
        try:
            self.db.sql(f"SELECT 1 FROM {table}").fetchall()
            return True
        except duckdb.CatalogException:
            return False


class GAdsMetaClient:
    # META_RESOURCE_TABLE = "meta_resource"
    # META_RESOURCE_FIELD_TABLE = "meta_resource_field"

    def __init__(
        self,
        *,
        customer_id: str = None,
        credentials: Credentials = None,
        developer_token: str = None,
    ):
        super().__init__()
        self.base_url = "https://googleads.googleapis.com/v18/"
        self.customer_id = customer_id
        self._bare_client = httpx.AsyncClient()

        class GoogleAdsAuth(Auth):
            def auth_flow(self, request: httpx.Request):
                if credentials.token_state is not TokenState.FRESH:
                    log.warning("Token is not fresh, refreshing")
                    grequest = Request()
                    credentials.refresh(grequest)
                request.headers["Authorization"] = f"Bearer {credentials.token}"
                yield request

        self._ads_rest = httpx.AsyncClient(auth=GoogleAdsAuth(), headers={"developer-token": developer_token})
        self._ads_grpc = GoogleAdsClient(credentials=credentials, developer_token=developer_token, version="v18")
        self._ads_search_service: GoogleAdsServiceClient = self._ads_grpc.get_service("GoogleAdsService")
        self._ads_fields_service: GoogleAdsFieldServiceClient = self._ads_grpc.get_service("GoogleAdsFieldService")

    async def make_request(self, method: str, path: str, **kwargs):
        url = urljoin(self.base_url, path)
        res = await self._ads_rest.request(method, url, **kwargs)
        if res.status_code >= 400:
            log.error("Status code: %s", res.status_code)
            log.error("Response: %s", res.text)
        res.raise_for_status()
        return res

    async def search_stream_rest(self, query: str):
        path = f"customers/{self.customer_id}/googleAds:searchStream"
        res = await self.make_request("POST", path, json={"query": query})
        res_json = res.json()
        if not res_json:
            return []
        field_mask = res_json[0]["fieldMask"]
        request_id = res_json[0]["requestId"]
        log.debug("Field mask: %s", field_mask)
        log.debug("Request ID: %s", request_id)
        final_data = []
        for chunk in res_json:
            data = chunk["results"]
            final_data.extend(data)
        return final_data

    async def search_stream_grpc(self, query: str):
        for response in self._ads_search_service.search_stream(customer_id=str(self.customer_id), query=query):
            for row in response.results:
                row: google_ads_service.GoogleAdsRow
                yield row

    async def _bare_get(self, url: str) -> str:
        res = await self._bare_client.get(url)
        res.raise_for_status()
        return res.text

    async def _get_soup(self, url: str) -> bs4.BeautifulSoup:
        html = await self._bare_get(url)
        return bs4.BeautifulSoup(html, "lxml")

    # async def upsert_resources(self):
    #     resources = list(await self.fetch_resources())
    #     self.tool.insert(self.META_RESOURCE_TABLE, pl.DataFrame(resources), drop=True)

    # @property
    # def resources(self):
    #     return self.tool.relation(self.META_RESOURCE_TABLE)

    # @property
    # def resource_fields(self):
    #     return self.tool.relation(self.META_RESOURCE_FIELD_TABLE)

    async def fetch_table_grpc(self, resource_type: str):
        field_names: list[str] = self.fields_for_resource(resource_type)
        query = f"select {', '.join(field_names)} from {resource_type}"
        results = []
        async for row in self.search_stream_grpc(query):
            result = getattr(row, resource_type)
            result = MessageToDict(result, always_print_fields_with_no_presence=True, preserving_proto_field_name=True)
            # flatten nested dicts
            flattened_result = {}
            for k in result:
                if isinstance(result[k], dict) and False:
                    flattened_result.update(result[k])
                else:
                    flattened_result[k] = result[k]
            results.append(flattened_result)
        if not results:
            return None
        return pl.from_dicts(results, infer_schema_length=None)

    async def fetch_table_rest(self, resource_type: str):
        """Deprecated"""
        field_names: list[str] = self.fields_for_resource(resource_type)
        query = f"select {', '.join(field_names)} from {resource_type}"
        results = await self.search_stream_rest(query)
        for r in results:
            _remove_non(r)
        results = [r for r in results if r]
        return results

    def grpc_fetch_resource_fields(self):
        query = "select name, selectable, filterable, sortable, type_url, is_repeated, data_type, enum_values, segments, metrics, attribute_resources, selectable_with, category"
        request = google_ads_field_service.SearchGoogleAdsFieldsRequest(
            query=query,
        )
        res = self._ads_fields_service.search_google_ads_fields(request)
        fields = []
        for page in res.pages:
            for field in page.results:
                fields.append(
                    MessageToDict(field, always_print_fields_with_no_presence=True, preserving_proto_field_name=True)
                )
        return fields

    @cached_property
    def resource_fields(self):
        return self.grpc_fetch_resource_fields()

    @cached_property
    def resources(self) -> list[str]:
        return [f["name"] for f in self.resource_fields if f["category"] == "RESOURCE"]

    def fields_for_resource(self, resource_type: str) -> list[str]:
        return [
            f["name"]
            for f in self.resource_fields
            if f["resource_name"].startswith(f"googleAdsFields/{resource_type}.")
            and f["selectable"]
            and f["category"] == "ATTRIBUTE"
        ]

    async def fetch_resource_fields(self, resource_type: str):
        """Deprecated"""
        url = f"https://developers.google.com/google-ads/api/fields/v18/{resource_type}"
        soup = await self._get_soup(url)
        fields = []
        for tr in soup.select("tbody.list")[-1]:
            if not tr.name == "tr":
                continue
            table = tr.select_one("table")
            name = table.select_one("th").text.strip()
            attrs = {"field_name": name}
            for str in table.select("tr")[1:]:
                tds = str.select("td")
                k = tds[0].text.strip().lower()
                v = tds[1].text.strip()
                if k == "data type":
                    if "enum" in v.lower():
                        v = "ENUM"
                if v.lower() == "true":
                    v = True
                elif v.lower() == "false":
                    v = False
                # normalize name
                k = invalid_name_pt.sub("_", k)
                attrs[k] = v
            fields.append(attrs)
        schema = {
            "field_name": pl.Utf8,
            "field_description": pl.Utf8,
            "category": pl.Utf8,
            "data_type": pl.Utf8,
            "type_url": pl.Utf8,
            "filterable": pl.Boolean,
            "sortable": pl.Boolean,
            "selectable": pl.Boolean,
            "repeated": pl.Boolean,
        }
        return pl.from_dicts(fields, schema=schema, infer_schema_length=None)

    async def fetch_resources(self):
        """Deprecated"""
        url = "https://developers.google.com/google-ads/api/fields/v18/overview"
        soup = await self._get_soup(url)
        resources = []
        for idx, tr in enumerate(soup.select("table tr")):
            if idx == 0:
                continue
            tds = tr.select("td")
            resource_type = tds[0].text.strip()
            description = tds[1].text.strip()
            resource = {"resource_type": resource_type, "description": description}
            resources.append(resource)
        df = pl.from_dicts(resources, schema={"resource_type": pl.Utf8, "description": pl.Utf8})
        return df


def _convert_name(text: str):
    if "_" not in text:
        return text
    segments = text.split("_")
    return "".join([s.title() if idx > 0 else s for idx, s in enumerate(segments)])


def _remove_non(d: dict):
    if not isinstance(d, dict):
        return
    for k in list(d.keys()):
        v = d[k]
        if isinstance(v, dict):
            if not v:
                del d[k]
            else:
                _remove_non(v)
        elif isinstance(v, list) and v:
            for e in v:
                _remove_non(e)
        else:
            pass


if __name__ == "__main__":
    from dbox.env import GOOGLE_ADS_DEVELOPER_TOKEN
    from dbox.google.auth import read_user_credentials
    from dbox.logging.colored import setup_colored_logging

    setup_colored_logging()

    google_credentials = read_user_credentials("leuduan@gmail.com.json")
    # customer_id = 7172700878  # Duan Org
    customer_id = 6470097593  # Sai Gon Xanh
    duck_conn = duckdb.connect("fun_gads.db")
    store = GAdsStore(duck_conn, schema="main")
    gaclient = GAdsMetaClient(
        customer_id=customer_id, developer_token=GOOGLE_ADS_DEVELOPER_TOKEN, credentials=google_credentials
    )

    async def main():
        fields = gaclient.grpc_fetch_resource_fields()
        store.insert("gads_field", pl.DataFrame(fields), drop=True)

        for resource in gaclient.resources:
            try:
                df = await gaclient.fetch_table_grpc(resource)
                if df is not None:
                    store.insert(resource, df, drop=True)
                else:
                    log.warning("No data for resource: %s", resource)
            except KeyboardInterrupt:
                raise
            except BaseException:
                log.exception("Error fetching resource: %s", resource)

    import asyncio

    asyncio.run(main())
