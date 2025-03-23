import asyncio

import pytest

from .client import GAdsMetaClient

pytest.skip("skip", allow_module_level=True)


@pytest.fixture(scope="module")
def loop():
    return asyncio.get_event_loop()


@pytest.fixture(scope="module")
def client(gads_developer_token, google_credentials):
    return GAdsMetaClient(customer_id=6470097593, developer_token=gads_developer_token, credentials=google_credentials)


def test_fetch_resources(client: GAdsMetaClient, loop: asyncio.AbstractEventLoop):
    df = loop.run_until_complete(client.fetch_resources())
    assert len(df) > 0
    print(df)


def test_fetch_resource_fields(client: GAdsMetaClient, loop: asyncio.AbstractEventLoop):
    df = loop.run_until_complete(client.fetch_resource_fields("product_link"))
    assert len(df) > 0
    print(df)


# def test_fetch_data_rest(client: GAdsMetaClient, loop: asyncio.AbstractEventLoop):
#     df = loop.run_until_complete(client.fetch_table_rest("campaign"))
#     df = client.tool.query("select * from campaign")
#     print(df)


def test_fetch_table_grpc(client: GAdsMetaClient, loop: asyncio.AbstractEventLoop):
    df = loop.run_until_complete(client.fetch_table_grpc("ad"))
    # df = client.tool.query("select * from campaign")
    print(df)


# def test_fetch_all_tables(client: GAdsMetaClient, loop: asyncio.AbstractEventLoop):
#     loop.run_until_complete(client.fetch_all_tables(force=1))


# def test_upsert_resource_fields(client: GAdsMetaClient):
#     asyncio.run(client.upsert_resource_fields())


def test_rest_search_stream(client: GAdsMetaClient, loop: asyncio.AbstractEventLoop):
    res = loop.run_until_complete(client.search_stream_rest("SELECT campaign.id, campaign.name FROM campaign"))
    assert isinstance(res, list)
    print(res)


def test_grpc_fetch_resource_fields(client: GAdsMetaClient):
    client.grpc_fetch_resource_fields()
    ad_field_names = client.fields_for_resource("ad")
    assert len(ad_field_names) > 0
    print(ad_field_names)
    campaign_field_names = client.fields_for_resource("campaign")
    assert len(campaign_field_names) > 0
    print(campaign_field_names)
