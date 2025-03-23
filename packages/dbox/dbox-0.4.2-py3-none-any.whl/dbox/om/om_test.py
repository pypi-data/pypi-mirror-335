import logging
from decimal import Decimal
from typing import Annotated, List, Optional

import pytest

from .ctx import SqlContext
from .model import DModel, Omt
from .sql import Delete
from .utils import fetch_all, get_one, paginate, to_nested

log = logging.getLogger(__name__)


def to_db_binary(value: str):
    if isinstance(value, bytes):
        return value
    return value.encode("utf8")


class MoonLocation(DModel):
    __tablename__ = "moon_location"
    id: Annotated[Optional[int], Omt(pk=True)] = None

    name: Annotated[Optional[str], Omt()] = None
    lat: Optional[Decimal] = None
    lng: Optional[Decimal] = None

    moon_id: Annotated[Optional[int], Omt(foreign_key=True)] = None
    moon: Annotated[Optional["Moon"], Omt(reference_data=True)] = None

    sun_id: Annotated[Optional[int], Omt(foreign_key=True)] = None
    sun: Annotated[Optional["Sun"], Omt(reference_data=True)] = None

    @classmethod
    def select(cls, ctx):
        from .sql import join_models

        return join_models(
            cls,
            (Moon, "moon_location.moon_id = moon.id"),
            (Sun, "moon_location.sun_id = sun.id"),
            (Galaxy, "moon.galaxy_id = galaxy.id"),
        )

    @classmethod
    def bind(cls, data):
        from .utils import to_nested

        data = to_nested(data)
        if moon := data.pop("moon", None):
            moon = Moon(**moon)
            if galaxy := data.pop("galaxy", None):
                galaxy = Galaxy(**galaxy)
                moon.galaxy = galaxy
        if sun := data.get("sun", None):
            sun = Sun(**sun)
        moon_location = MoonLocation(**data)
        moon_location.moon = moon
        moon_location.sun = sun
        return moon_location

    @classmethod
    def dml(cls):
        return """
        CREATE TABLE IF NOT EXISTS moon_location (
            id SERIAL PRIMARY KEY,
            name TEXT,
            lat DECIMAL,
            lng DECIMAL,
            moon_id INT REFERENCES moon(id),
            sun_id INT REFERENCES sun(id)
        )
        """


class Sun(DModel):
    __tablename__ = "sun"
    id: Annotated[Optional[int], Omt(pk=True)] = None

    description: Annotated[Optional[str], Omt()] = None

    @classmethod
    def dml(cls):
        return """
        CREATE TABLE IF NOT EXISTS sun (
            id SERIAL PRIMARY KEY,
            description TEXT
        )
        """


class Moon(DModel):
    __tablename__ = "moon"
    id: Annotated[Optional[int], Omt(pk=True)] = None

    name: Annotated[Optional[str], Omt()] = None
    images: Annotated[Optional[List[str]], Omt()] = None
    galaxy_id: Annotated[Optional[int], Omt(foreign_key=True)] = None
    galaxy: Annotated[Optional["Galaxy"], Omt(reference_data=True)] = None

    @classmethod
    def select(cls, ctx=None):
        from .sql import join_models

        return join_models(cls, (Galaxy, "moon.galaxy_id = galaxy.id"))

    @classmethod
    def bind(cls, data):
        from .utils import to_nested

        data = to_nested(data)
        if galaxy := data.pop("galaxy", None):
            galaxy = Galaxy(**galaxy)
        moon = Moon(**data)
        moon.galaxy = galaxy
        return moon

    @classmethod
    def dml(cls):
        return """
        CREATE TABLE IF NOT EXISTS moon (
            id SERIAL PRIMARY KEY,
            name TEXT,
            images TEXT[],
            galaxy_id INT REFERENCES galaxy(id)
        )
        """


class Galaxy(DModel):
    __tablename__ = "galaxy"
    id: Annotated[Optional[int], Omt(pk=True)] = None

    name: Annotated[Optional[str], Omt()] = None
    distance: Optional[int] = None

    @classmethod
    def dml(cls):
        return """
        CREATE TABLE IF NOT EXISTS galaxy (
            id SERIAL PRIMARY KEY,
            name TEXT,
            distance INT
        )
        """


@pytest.fixture(autouse=True, scope="session")
async def prepare_db(ctx: SqlContext):
    from psycopg_pool import AsyncConnectionPool

    async with ctx.use_db() as cur:
        await cur.execute(Galaxy.dml())
        await cur.execute(Moon.dml())
        await cur.execute(Sun.dml())
        await cur.execute(MoonLocation.dml())
    log.info("DB tables created")


@pytest.mark.asyncio
async def test_prepare_db(prepare_db):
    await prepare_db
    # assert 1 == 2


def test_bind():
    flat = {
        "moon_location.id": 1672,
        "moon_location.moon_id": 1,
        "moon.id": 123,
        "moon.name": "hello",
        "moon.images": ["a", "b"],
        "moon.galaxy.id": 0,
    }
    moon_location = MoonLocation.bind(flat)
    print(moon_location)


def test_to_nested():
    flat = {
        "id": 1672,
        "moon_id": 1,
        "moon.id": 123,
        "moon.name": "hello",
        "moon.images": ["a", "b"],
        "moon.galaxy.id": 0,
    }
    nested = to_nested(flat)
    assert nested == {
        "id": 1672,
        "moon_id": 1,
        "moon": {"id": 123, "name": "hello", "images": ["a", "b"], "galaxy": {"id": 0}},
    }


def test_create_nested_model(ctx):
    data1 = {
        "id": 1672,
        "moon_id": 1,
        "moon": {"id": 123, "name": "hello", "images": ["a", "b"], "galaxy": {"id": 0}},
    }
    location1 = MoonLocation(**data1)
    print(location1)
    data2 = {
        "id": 1672,
        "moon_id": 1,
        "moon.id": 123,
        "moon.name": "hello",
        "moon.images": ["a", "b"],
        "moon.galaxy.id": 0,
    }
    location2 = MoonLocation.bind(data2)
    assert location1 == location2


def test_create_empty():
    model = Moon()
    assert model.id is None


def test_db_get_create_fields():
    create_fields = Moon.db_get_create_fields()
    print(create_fields)
    assert {"name", "images"} <= set(create_fields)


def db_get_insert_or_update_row(ctx):
    model = Moon()
    model.name = "hello"
    model.images = ["a", "b"]
    row = model.db_get_insert_or_update_row(ctx, ["id", "name", "images"])
    assert row == {"id": None, "name": b"hello", "images": ["a", "b"]}


# def test_db_get_insert_stmt(ctx):
#     stmt = Moon.db_get_insert_stmt(ctx)
#     print(stmt)


def test_db_get_update_fields():
    update_fields = Moon.client_update_fields()
    print(update_fields)
    assert {"name", "images"} <= set(update_fields)
    assert "id" not in update_fields


# def test_serializer(ctx: OmContext):
#     images_field = Moon.om_metadata()["images"]
#     assert ctx.serialize(images_field, None) is None
#     assert ctx.serialize(images_field, ["a", "b"]) == ["a", "b"]

#     name_field = Moon.om_metadata()["name"]
#     assert ctx.serialize(name_field, "hello") == b"hello"
#     assert ctx.serialize(name_field, None) is None

#     instance = Moon(images=["a", "b"])
#     assert instance.images == ["a", "b"]


def test_db_get_update_stmt(ctx):
    stmt = Moon.db_get_update_stmt(ctx, ["name", "images"])
    print(stmt)


def test_patch(ctx):
    model = Moon()
    model.id = 123
    model.name = "hello"
    model.images = ["a", "b"]
    model.instance_update(ctx, {"name": "world"}, update_mask=["name"])
    print(model)

    stmt = model.db_get_update_stmt(ctx, ["name"])
    print(stmt)

    model.instance_update(ctx, {"name": "world", "id": 125}, update_mask=["name", "id"])
    assert model.id == 125
    print(model)


@pytest.mark.asyncio
async def test_utils(ctx: SqlContext):
    async with ctx.use_db():
        moon = await get_one(Moon, ctx=ctx, pk=1111)
        assert moon is None

        # delete moons
        await ctx.run_query(query=Delete(model=MoonLocation).to_sql(), params={"pk": 1}, exec=True)
        await ctx.run_query(query=Delete(model=Moon).to_sql(), params={"pk": 1}, exec=True)
        await ctx.run_query(query=Delete(model=Galaxy).to_sql(), params={"pk": 1}, exec=True)

        galaxy = Galaxy(id=1, name="milky way", distance=1000)
        await galaxy.db_create(ctx, set_pk=True)

        moon = Moon(id=1, name="hello", images=["a", "b"])
        moon.galaxy_id = galaxy.id
        moon.galaxy = galaxy
        await moon.db_create(ctx, set_pk=True)

        moon_back = await get_one(Moon, ctx=ctx, pk=1)
        assert moon_back == moon

        location = MoonLocation(id=1, name="foot on the moon", moon_id=1)
        location.moon = moon
        await location.db_create(ctx, set_pk=True)
        await ctx.commit()

        location_back = await get_one(MoonLocation, ctx=ctx, pk=1)
        assert location_back == location

        res = await paginate(MoonLocation, ctx=ctx, limit=10, conditions=['"id" = 1'], include_total=True, page=1)
        print(res)

        locations = await fetch_all(MoonLocation, ctx=ctx)
        print(locations)
