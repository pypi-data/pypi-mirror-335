import logging
from functools import cache
from pathlib import Path
from typing import (
    Any,
    ClassVar,
    Dict,
    List,
    Optional,
)

from pydantic import BaseModel, ValidationInfo, field_validator

from .ctx import SqlContext, use_sql_context
from .meta import Omt

parent_dir = Path(__file__).parent
log = logging.getLogger(__name__)


class DModel(BaseModel):
    """Base model for resource-oriented API."""

    __tablename__: ClassVar[str]

    @classmethod
    def get_fqtn(cls) -> str:
        ctx = use_sql_context()
        return ctx.get_fqtn(cls.__tablename__)

    @classmethod
    def self_fields(cls):
        return [f for f, om in cls.om_metadata().items() if not om.reference_data]

    @classmethod
    def select(cls, ctx: SqlContext):
        from .sql import DModelRelation

        return DModelRelation(model=cls).to_sql()

    @classmethod
    def bind(cls, data: Dict[str, Any]):
        return cls(**data)

    @field_validator("*", mode="before")
    @classmethod
    def om_preprocess(cls, value, info: ValidationInfo):
        if value is None:
            return None
        return value

    # protobuf message
    @classmethod
    def create_proto_message_cls(cls):
        if cls.__proto_cls__ is not None:
            return cls.__proto_cls__
        import proto
        from proto.message import MessageMeta

        cls.__proto_cls__ = MessageMeta(cls.__name__, (proto.Message,), {})
        return cls.__proto_cls__

    # end of protobuf message

    @classmethod
    @cache
    def om_metadata(cls) -> Dict[str, Omt]:
        ret = {}
        for name, field in cls.model_fields.items():
            # get first om metadata
            # annot = get_args(field.annotation)
            for a in field.metadata:
                if isinstance(a, Omt):
                    a.info = field
                    ret[name] = a
                    break
            else:
                om = Omt()
                om.info = field
                ret[name] = om
        return ret

    @classmethod
    def client_create_fields(cls):
        """Available to be provided by client."""
        insert_fields = []
        for name, field in cls.om_metadata().items():
            if (
                field.server_generated or field.reference_data or field.system_column or field.pk
                # or field.foreign_key
            ):
                continue
            else:
                insert_fields.append(name)
        return insert_fields

    @classmethod
    @cache
    def db_get_create_fields(cls):
        """Fields that can be inserted into database."""
        insert_fields = []
        for name, field in cls.om_metadata().items():
            if field.server_generated or field.reference_data:
                continue
            else:
                insert_fields.append(name)
        return insert_fields

    @classmethod
    def db_get_insert_stmt(cls, ctx: SqlContext, fields: List[str]):
        from .sql import InsertBlock

        return InsertBlock(model=cls, columns=fields, pk_col=cls.pk_col()).to_sql()

    def db_get_insert_or_update_row(self, ctx: SqlContext, columns: List[str]):
        data = {}
        for name in columns:
            field_info = self.om_metadata()[name]
            data[name] = ctx.serialize(field_info, getattr(self, name))
        return data

    async def db_create(self, ctx: SqlContext = None, set_pk: bool = False):
        # we create the instance
        # we set some system fields
        # we insert the instance to db
        # stmt = self.db_get_insert_stmt(ctx)
        ctx = ctx or use_sql_context()
        db_create_fields = self.db_get_create_fields()
        if not set_pk:
            # pk col must not be set
            assert getattr(self, self.pk_col()) is None
            db_create_fields = [e for e in db_create_fields if e != self.pk_col()]
        stmt = self.db_get_insert_stmt(ctx, db_create_fields)
        data = self.db_get_insert_or_update_row(ctx, db_create_fields)
        log.debug("Data: %s", data)
        log.debug("Stmt: %s", stmt)
        await ctx.cursor.execute(stmt, data)
        if not set_pk:
            # get the id and set it TODO: get all generated fields
            pk = self.pk_col()
            row = await ctx.cursor.fetchone()
            log.debug("Row: %s", row)
            newpk = row[pk]
            setattr(self, pk, newpk)

        return self

    @classmethod
    @cache
    def pk_col(cls):
        for name, field in cls.om_metadata().items():
            if field and field.pk:
                return name
        return "id"

    @classmethod
    @cache
    def client_update_fields(cls):
        """Fields that can be updated in database. All fields are updatable except for server-generated, reference-data, pk."""
        update_fields = []
        for name, field in cls.om_metadata().items():
            if field is None:
                update_fields.append(name)
            else:
                if field.server_generated or field.reference_data or field.pk:
                    continue
                else:
                    update_fields.append(name)
        return update_fields

    @classmethod
    def instance_create(cls, data: Dict[str, Any], ctx: Optional[SqlContext] = None):
        # take only fields in cls.get_create_fields()
        instance_data = {k: v for k, v in data.items() if k in cls.client_create_fields()}
        instance = cls(**instance_data)
        return instance

    def instance_update(
        self, ctx: SqlContext, partial: Dict[str, Any], update_mask: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        # we loaded the instance from db
        # we apply the partial data to the instance
        empty_instance = self.__class__(**partial)
        update_mask = update_mask or self.client_update_fields()
        # filter out fields that are not updatable
        # update_mask = [e for e in update_mask if e in self.client_update_fields()]
        changes = {}
        for k in update_mask:
            newval = getattr(empty_instance, k)
            if getattr(self, k) != newval:
                changes[k] = newval
                setattr(self, k, newval)
        return changes

    @classmethod
    def db_get_update_stmt(cls, ctx: SqlContext, columns: List[str]):
        assert columns
        from .sql import UpdateBlock

        return UpdateBlock(model=cls, columns=columns, pk_col=cls.pk_col()).to_sql()

    async def db_update(self, ctx: SqlContext, columns: List[str]):
        # we loaded the instance from db or somewhere
        # we modify some fields
        # we update the fields to db
        stmt = self.db_get_update_stmt(ctx, columns)
        data = self.db_get_insert_or_update_row(ctx, columns)
        pk_col = self.pk_col()
        pk = getattr(self, pk_col)
        data["pk_col"] = pk
        await ctx.cursor.execute(stmt, data)
