from typing import Optional

import pandas as pd
import pyarrow as pa
import shapely
from shapely import GEOSException

from odp.tabular_v2.bsquare.query import _QueryContext
from odp.tabular_v2.util import exp


def convert_schema_inward(outer_schema: pa.Schema) -> pa.Schema:
    out = []
    for name in outer_schema.names:
        f = outer_schema.field(name)
        if f.metadata and b"isGeometry" in f.metadata:
            meta = f.metadata
            if b"index" in meta:
                new_meta = meta.copy()
                del new_meta[b"index"]
                f = f.with_metadata(new_meta)
            out.append(f)
            out.append(pa.field(name + ".x", pa.float64(), True, metadata=meta))
            out.append(pa.field(name + ".y", pa.float64(), True, metadata=meta))
            out.append(pa.field(name + ".q", pa.float64(), True, metadata=meta))
        else:
            out.append(f)
    return pa.schema(out)


# convert the inner_schema to outer_schema
def convert_schema_outward(inner_schema: pa.Schema) -> pa.Schema:
    geo_indexes = set()

    def is_subfield(schema: pa.Schema, f: pa.Field) -> bool:
        if "." not in f.name:
            return False
        left, right = f.name.rsplit(".", 1)
        if right not in ["x", "y", "q"]:
            return False
        if left not in schema.names:
            return False
        if schema.field(left).metadata and b"isGeometry" not in schema.field(left).metadata:
            return False
        if f.metadata and b"index" in f.metadata:
            geo_indexes.add(left)
        return True

    # create a new schema with only the fields that are not subfields
    fields = []
    for names in inner_schema.names:
        f = inner_schema.field(names)
        if not is_subfield(inner_schema, f):
            fields.append(f)

    # add back the "index" to the main field (which was removed when creating the subfields)
    for i, f in enumerate(fields):
        if f.name in geo_indexes:
            meta = f.metadata
            meta[b"index"] = b"1"
            fields[i] = f.with_metadata(meta)
    return pa.schema(fields)


# convert outer query to inner query using bsquare in .x, .y and .q
def convert_query(outer_schema: pa.Schema, outer_query: Optional[exp.Op]) -> Optional[exp.Op]:
    if outer_query is None:
        return None

    geo_fields = []
    for f in outer_schema:
        if f.metadata and b"isGeometry" in f.metadata:
            geo_fields.append(f.name)

    return _QueryContext(geo_fields).convert(outer_query)


def decode(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for name in df.columns:
        if name.endswith(".x") or name.endswith(".y") or name.endswith(".q"):
            df.drop(columns=[name], inplace=True)
    return df


def encode(df: pd.DataFrame, outer_schema: pa.Schema) -> pd.DataFrame:
    # logging.info("bsquare encoding %d rows", b.num_rows)
    geo_names = []
    for name in outer_schema.names:
        f = outer_schema.field(name)
        if f.metadata and b"isGeometry" in f.metadata:
            geo_names.append(name)

    df = df.copy()

    # we encode rows by rows to made it simple to create multiple columns
    def _encode(row):
        for name in geo_names:
            if name in row and row[name] is not None:
                val = row[name]
                if isinstance(val, str):
                    try:
                        val = shapely.from_wkt(val)
                    except GEOSException as e:
                        raise ValueError(f"Invalid geo format: {val}") from e
                elif isinstance(val, bytes):
                    val = shapely.from_wkb(val)
                else:
                    raise ValueError(f"Unsupported type: {type(val)}")
                min_x, min_y, max_x, max_y = val.bounds
                row[name + ".x"] = (min_x + max_x) / 2
                row[name + ".y"] = (min_y + max_y) / 2
                row[name + ".q"] = max(max_x - min_x, max_y - min_y) / 2
            else:
                row[name + ".x"] = None
                row[name + ".y"] = None
                row[name + ".q"] = None
        return row

    for geo_name in geo_names:
        df[geo_name + ".x"] = None
        df[geo_name + ".y"] = None
        df[geo_name + ".q"] = None
    return df.apply(func=_encode, axis=1)


class BSquare:
    geometry_fields = ["{col_name}.x", "{col_name}.y", "{col_name}.q"]  # add complexity and confuse the user

    def __init__(self, inner_schema: Optional[pa.Schema] = None):
        assert not "good"
        self._inner_schema = inner_schema
        self._geo_fields = []  # FIXME do this earlier, then cash on it

    # def _select_filter(self, outer_query: Op | None, schema: pa.Schema | None, cursor: str)
    # -> Iterator[pa.RecordBatch]:
    #    if outer_query is None or outer_query == Scalar.from_py(None):  # FIXME(oha): Scalar(null) is not None
    #        for b in self.inner.select(None, schema, cursor):
    #            yield b
    #        return

    #    geo_fields = []
    #    if schema is None:
    #        schema = BSquare.external_schema(self.inner_schema)
    #    for f in schema:
    #        if f.metadata and b"isGeometry" in f.metadata:
    #            geo_fields.append(f.name)

    #    inner_query = _QueryContext(geo_fields).convert(outer_query)

    #    for b in self.inner.select(
    #        inner_query, self.inner_schema, cursor
    #    ):  # FIXME(oha): expand schema with geo subfields or bigcol will fail
    #        if b.num_rows == 0:
    #            yield b
    #        else:
    #            for b in pa.Table.from_batches([b], schema=b.schema).filter(outer_query.pyarrow()).to_batches():
    #                yield b

    # @staticmethod
    # def external_schema(inner_schema: pa.Schema) -> pa.Schema:
    #    geo_indexes = set()

    #    def is_subfield(schema: pa.Schema, f: pa.Field) -> bool:
    #        if "." not in f.name:
    #            return False
    #        left, right = f.name.rsplit(".", 2)
    #        if left not in schema.names:
    #            return False
    #        if schema.field(left).metadata and b"isGeometry" not in schema.field(left).metadata:
    #            return False
    #        if f.metadata and b"index" in f.metadata:
    #            geo_indexes.add(left)
    #        return True

    #    fields = []
    #    for names in inner_schema.names:
    #        f = inner_schema.field(names)
    #        if not is_subfield(inner_schema, f):
    #            fields.append(f)

    #    for i, f in enumerate(fields):
    #        if f.name in geo_indexes:
    #            meta = f.metadata
    #            meta[b"index"] = b"1"
    #            fields[i] = f.with_metadata(meta)
    #    return pa.schema(fields)

    # def select(self, query: Op | None, schema: pa.Schema | None | List[str], cursor: str) -> Iterator[pa.RecordBatch]:
    #    if schema is not None:
    #        if isinstance(schema, list):
    #            s = self.inner_schema
    #            schema = pa.schema([s.field(n) for n in schema])
    #        for x in self._select_filter(query, schema, cursor):
    #            yield x
    #        return

    #    for b in self._select_filter(query, None, cursor):
    #        if schema is None:
    #            self._inner_schema = b.schema
    #            schema = BSquare.external_schema(self._inner_schema)
    #        b = b.select(schema.names)
    #        yield b

    # def insert(self, batch: pa.RecordBatch):
    #    # NOTE(oha): we trust the batch has the right metadata and types

    #    # expand the schema
    #    fields = []
    #    geo_names = []
    #    for f in batch.schema:
    #        if f.metadata and b"isGeometry" in f.metadata:
    #            geo_names.append(f.name)
    #            meta = f.metadata
    #            if b"index" in f.metadata:
    #                meta_copy = meta.copy()
    #                del meta_copy[b"index"]
    #                f = f.with_metadata(meta_copy)  # remove the index
    #            fields.append(f)
    #            del meta[b"isGeometry"]
    #            # TODO(oha): how to tell if there is a .z?
    #            for geometry_field in self.geometry_fields:
    #                field_name = geometry_field.format(col_name=f.name)
    #                if field_name not in batch.schema.names:
    #                    fields.append(
    #                        pa.field(geometry_field.format(col_name=f.name), pa.float64(), True, metadata=meta)
    #                    )
    #        else:
    #            fields.append(f)

    #    if not geo_names:
    #        return self.inner.insert(batch)

    #    inner_schema = pa.schema(fields)
    #    if batch.num_rows == 0:
    #        return self.inner.insert(pa.RecordBatch.from_pylist([], inner_schema))

    #    d: pd.DataFrame = batch.to_pandas()
    #    del batch  # free memory, if possible

    #    # we encode rows by rows to made it simple to create multiple columns
    #    def _encode(row):
    #        for name in geo_names:
    #            if name in row and row[name] is not None:
    #                geo = GeometryBbox.from_python_object(row[name])
    #                for geo_field, col_value in zip(self.geometry_fields, geo.get_coordinates()):
    #                    row[geo_field.format(col_name=name)] = col_value
    #                row[name] = geo.wkt
    #            else:
    #                for geo_field in self.geometry_fields:
    #                    row[str(geo_field.format(col_name=name))] = None
    #        return row

    #    for geo_name in geo_names:
    #        for geo_field in self.geometry_fields:
    #            # must add columns first, will be filled by _encode later
    #            d[geo_field.format(col_name=geo_name)] = None
    #    d = d.apply(func=_encode, axis=1)
    #    inner_batch = pa.RecordBatch.from_pandas(d, schema=inner_schema)
    #    del d

    #    return self.inner.insert(inner_batch)

    # def delete(self, query: Op, schema: pa.Schema):
    #    return self.inner.delete(query, schema)
