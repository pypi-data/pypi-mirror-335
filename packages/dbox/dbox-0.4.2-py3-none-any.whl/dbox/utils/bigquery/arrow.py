import logging

import pandas as pd
import pyarrow as pa

log = logging.getLogger(__name__)


def arrow_table_to_dataframe(table: pa.Table) -> pd.DataFrame:
    "Convert an arrow table from bigquery storage client to an pandas DataFrame"
    data = {}
    schema = table.schema
    no_nested = all(_is_primitive_type(f.type) for f in schema)
    if no_nested:
        # just call to_pandas as it may have some optimizations
        # https://arrow.apache.org/docs/python/pandas.html#reducing-memory-use-in-table-to-pandas
        return table.to_pandas(split_blocks=True, self_destruct=True, timestamp_as_object=True)

    fields = []
    for name in reversed(schema.names):
        fields.append(([], schema.field(name), table))

    while fields:
        path, field, container = fields.pop()
        fname, ftype = field.name, field.type
        full_path = [*path, fname]
        _full_path = ".".join(full_path)
        if _is_primitive_type(ftype):
            array = _get_data(container, fname)
            data[_full_path] = array.to_pandas(timestamp_as_object=pa.types.is_timestamp(ftype))
        elif pa.types.is_struct(ftype):
            for field in reversed(ftype):
                fields.append((full_path, field, _get_data(container, fname)))
        else:
            data[_full_path] = _get_data(container, fname)
    return pd.DataFrame(data)


def _get_data(container, col):
    if isinstance(container, pa.Table):
        return container[container.column_names.index(col)]
    if isinstance(container, pa.ChunkedArray):
        return pa.chunked_array([e.field(col) for e in container.chunks])
    raise ValueError


def _is_primitive_type(itype):
    if pa.types.is_struct(itype) or pa.types.is_list(itype):
        return False
    return True
