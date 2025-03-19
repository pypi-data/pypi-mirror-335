import io
import logging
from typing import TYPE_CHECKING, Dict, Iterator, List, Optional, Union

import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc

from odp.tabular_v2 import big, bsquare
from odp.tabular_v2.client import Client
from odp.tabular_v2.util import exp, vars_to_json

if TYPE_CHECKING:
    from odp.tabular_v2.client import Cursor


class Table:
    def __init__(self, client: Client, table_id: str):
        self._id = table_id
        self._client = client
        self._inner_schema: Optional[pa.Schema] = None
        self._outer_schema: Optional[pa.Schema] = None
        self._tx = None
        try:
            self._fetch_schema()
        except FileNotFoundError:
            pass  # ktable does not exist yet

        self._bigcol = big.RemoteBigCol(
            self._bigcol_upload,
            self._bigcol_download,
            "/tmp/cache_big/",  # FIXME
        )

    def _fetch_schema(self):
        if self._inner_schema:
            return
        empty = list(self._select(inner_query=exp.parse('"fetch" == "schema"')))
        assert len(empty) == 1
        assert empty[0].num_rows == 0
        self._inner_schema = empty[0].schema
        mid = big.convert_schema_outward(self._inner_schema)
        self._outer_schema = bsquare.convert_schema_outward(mid)

    def drop(self):
        """
        drop the table data and schema
        this operation is irreversible
        @return:
        """
        try:
            res = self._client._request(
                path="/api/table/v2/drop",
                params={
                    "table_id": self._id,
                },
            ).json()
            logging.info("dropped %s: %s", self._id, res)
        except FileNotFoundError:
            logging.info("table %s does not exist", self._id)

    def _validate_parquet_schema(self, schema: pa.Schema):
        compatible_types = {
            pa.types.is_integer,
            pa.types.is_floating,
            pa.types.is_boolean,
            pa.types.is_string,
            pa.types.is_binary,
            pa.types.is_date,
            pa.types.is_timestamp,
            pa.types.is_decimal,
            pa.types.is_time,
        }
        for field in schema:
            if not any(check_function(field.type) for check_function in compatible_types):
                raise ValueError(f"Incompatible type for parquet detected: {field.name} ({field.type})")

    def create(self, schema: pa.Schema):
        """
        set the table schema using the given pyarrow schema
        fields might contains metadata which will be used internally:
        * index: the field should be used to partition the data
        * isGeometry: the field is a geometry (wkt for string, wkb for binary)
        @param schema: pyarrow.Schema
        @raise FileExistsError if the schema is already set
        @return:
        """
        self._validate_parquet_schema(schema)
        self._outer_schema = schema
        schema = bsquare.convert_schema_inward(schema)
        self._inner_schema = big.convert_schema_inward(schema)
        buf = io.BytesIO()
        w = pa.ipc.RecordBatchStreamWriter(buf, self._inner_schema)
        w.write_batch(pa.RecordBatch.from_pylist([], schema=self._inner_schema))
        w.close()

        self._client._request(
            path="/api/table/v2/create",
            params={
                "table_id": self._id,
            },
            data=buf.getvalue(),
        ).json()

    def _bigcol_upload(self, bid: str, data: bytes):
        self._client._request(
            path="/api/table/v2/big_upload",
            params={"table_id": self._id, "big_id": bid},
            data=data,
        )

    def _bigcol_download(self, big_id: str) -> bytes:
        return self._client._request(
            path="/api/table/v2/big_download",
            params={"table_id": self._id, "big_id": big_id},
        ).all()

    # def aggregate_h3(
    #    self, geometry: shapely.Geometry, resolution: int = 0, query: Union[exp.Op, str, None] = None
    # ) -> dict:
    #    """
    #    experimental
    #    aggregate data using h3 hexagons withing the given geometry
    #    compute the minimal resolution to have at least 200 hexagons
    #    """
    #    import h3

    #    pol = json.loads(shapely.to_geojson(geometry))
    #    hexes = h3.polyfill(pol, resolution)
    #    if resolution == 0:
    #        for resolution in range(1, 15):
    #            hexes = h3.polyfill(pol, resolution)
    #            if len(hexes) >= 20:
    #                logging.info("using res %d (will give %d hexagons)", resolution, len(hexes))
    #                break

    #    if len(hexes) > 10_0000:
    #        raise ValueError(f"too many hexagons: {len(hexes)}, please use a lower resolution")

    #    hpol = h3.h3_set_to_multi_polygon(hexes, geo_json=True)[0]
    #    pols = shapely.polygons(hpol)
    #    bounds = pols[0].bounds

    #    geo_query = exp.parse(f"lat > {bounds[1]} and lat < {bounds[3]} and lon > {bounds[0]} and lon < {bounds[2]}")
    #    logging.info("geo_query: %s", geo_query)
    #    if query:
    #        if isinstance(query, str):
    #            query = exp.parse(query)
    #        query = exp.BinOp(
    #            left=query,  # TODO: do we need to wrap it in a parenthesis?
    #            op="and",
    #            right=geo_query,
    #        )
    #    else:
    #        query = geo_query

    #    out = {}
    #    for row in self.aggregate(by="h3(%d)" % resolution, query=query):
    #        hid = row["__aggr"]
    #        del row["__aggr"]
    #        if hid in hexes:
    #            out[hid] = row
    #    return out

    def aggregate(
        self,
        by: str,
        query: Union[exp.Op, str, None] = None,
        aggr: Union[dict, None] = None,
        timeout: float = 30.0,
        vars: Union[dict, list, None] = None,
    ) -> pd.DataFrame:
        """
        aggregate the data after the optional `query` filter
        the paramater `by` is used to determine the key for the aggregation, and can be an expression.
        the optional `aggr` specify which fields need to be aggregated, and how
        If not specified, the fields with metadata "aggr" will be used
        a single DataFrame will be returned, with the index set to the key used for aggregation
        """
        if isinstance(query, str):
            query = exp.parse(query)  # NOTE(oha): we don't do the bsquare and bigcol waltz, but neither the server :(

        if aggr is None:
            aggr = {}
            for field in self._outer_schema:
                if field.metadata and b"aggr" in field.metadata:
                    aggr[field.name] = field.metadata[b"aggr"].decode()

        tot_func = {}
        for field, a_type in aggr.items():
            if a_type == "mean" or a_type == "avg":
                tot_func[field + "_sum"] = "sum"
                tot_func[field + "_count"] = "sum"
            elif a_type == "sum":
                tot_func[field + "_sum"] = "sum"
            elif a_type == "min":
                tot_func[field + "_min"] = "min"
            elif a_type == "max":
                tot_func[field + "_max"] = "max"
            elif a_type == "count":
                tot_func[field + "_count"] = "sum"
            else:
                raise ValueError(f"unknown aggregation type: {a_type}")

        total: Union[pd.DataFrame, None] = None
        for b in self._select(type="aggregate", by=by, inner_query=query, timeout=timeout, aggr=aggr, vars=vars):
            df: pd.DataFrame = b.to_pandas()
            # logging.warning("PARTIAL:\n%s", df)
            if total is None:
                total = df
            else:
                total = pd.concat([total, df], ignore_index=True)
                total = total.groupby("").agg(tot_func).reset_index()
        if total is None:
            return pd.DataFrame()

        for field, a_type in aggr.items():
            logging.info("field: %s, type: %s", field, a_type)
            if a_type == "mean" or a_type == "avg":
                total[field] = total[field + "_sum"] / total[field + "_count"]
                total.drop(columns=[field + "_sum", field + "_count"], inplace=True)
            elif a_type in "sum":
                total[field] = total[field + "_sum"]
                total.drop(columns=[field + "_sum"], inplace=True)
            elif a_type == "min":
                total[field] = total[field + "_min"]
                total.drop(columns=[field + "_min"], inplace=True)
            elif a_type == "max":
                total[field] = total[field + "_max"]
                total.drop(columns=[field + "_max"], inplace=True)
            elif a_type == "count":
                total[field] = total[field + "_count"]
                total.drop(columns=[field + "_count"], inplace=True)
            else:
                raise ValueError(f"unknown aggregation type: {a_type}")

        total = total.set_index("")
        # logging.info("TOTAL:\n%s", total)
        return total

    def _query_cursor(
        self,
        query: Union[exp.Op, str, None] = None,
        cols: Optional[List[str]] = None,
        vars: Union[dict, list, None] = None,
        stream_ttl: float = 30.0,
        type: str = "select",
        tx_id: str = "",
    ) -> "Cursor":
        if isinstance(query, str):
            query = exp.parse(query)
        elif isinstance(query, pc.Expression):
            query = exp.parse(str(query))
        if query:
            query.bind(vars)
            if cols:
                logging.info("cols: %s", cols)
                inner_cols = set(cols)  # add filtering columns
                for op in query.all():
                    if isinstance(op, exp.Field):
                        inner_cols.add(str(op))
                inner_cols = list(inner_cols)
            else:
                inner_cols = None
            query.bind(vars)

            logging.info("outer query: %s", query)
            inner_query = bsquare.convert_query(self._outer_schema, query)
            logging.info("bsquare query: %s", inner_query)
            inner_query = big.inner_exp(self._inner_schema, inner_query)
            logging.info("bigcol query: %s", inner_query)
        else:
            inner_cols = list(cols) if cols else None
            inner_query = None

        # expand the list to include the refs, if not empty
        if inner_cols:
            refs = []
            for col in inner_cols:
                f = self._outer_schema.field(col)
                if f.metadata and b"big" in f.metadata:
                    refs.append(col + ".ref")
            logging.info("inner_cols: %s, refs: %s", inner_cols, refs)
            inner_cols.extend(refs)

        def scanner(scanner_cursor: str) -> Iterator[pd.DataFrame]:
            logging.info("selecting with cursor %s: %s", scanner_cursor, inner_query)
            for b in self._select(
                tx=tx_id,
                type=type,
                inner_query=inner_query,
                cols=inner_cols,
                vars=vars,
                cursor=scanner_cursor,
                timeout=stream_ttl,
            ):
                # logging.info("got %d rows, decoding...", b.num_rows)

                # repackage into small batches because bigcol can use lots of memory
                tab = pa.Table.from_batches([b], schema=b.schema)
                del b
                for b in tab.to_batches(max_chunksize=2_000):
                    df = b.to_pandas()
                    df = self._bigcol.decode(df)
                    df = bsquare.decode(df)
                    if query:
                        df = df[query.pandas(df, self._outer_schema)]
                    if cols:
                        df = df[cols]
                    yield df

        from odp.tabular_v2.client import Cursor

        schema = self._outer_schema
        if cols:
            schema = pa.schema([schema.field(col) for col in cols])
        return Cursor(scanner=scanner, schema=schema)

    def select(
        self,
        query: Union[exp.Op, str, None] = None,
        cols: Optional[List[str]] = None,
        vars: Union[dict, list, None] = None,
        timeout: float = 30.0,
    ) -> "Cursor":
        """
        fetch data from the underling table

        for row in tab.select("age > 18").rows():
            print(row)

        you can use bind variables, especially if you need to use date/time objects:

        for row in tab.select("age > $age", vars={"age": 18}).rows():
            print(row)

        and limits which columns you want to retrieve:

        for row in tab.select("age > 18", cols=["name", "age"]).rows():
            print(row)

        The object returned is a cursor, which can be scanned by rows, batches, pages, pandas dataframes, etc.

        you can check the documentation of the Cursor for more information
        """
        return self._query_cursor(query, cols, vars, timeout, "select")

    def __enter__(self):
        if self._inner_schema is None:
            raise FileNotFoundError("table does not exist, create() it first")

        if self._tx:
            raise ValueError("already in a transaction")

        res = self._client._request(
            path="/api/table/v2/begin",
            params={
                "table_id": self._id,
            },
        ).json()
        from odp.tabular_v2.client.table_tx import Transaction

        buf = big.Buffer(self._bigcol).with_inner_schema(self._inner_schema)
        self._tx = Transaction(self, res["tx_id"], buf)
        return self._tx

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            logging.warning("aborting transaction %s", self._tx._id)
            # try:
            #    self._client._request(
            #        path="/api/table/v2/rollback",
            #        params={
            #            "table_id": self._id,
            #            "tx_id": self._tx._id,
            #        },
            #    )
            # except Exception as e:
            #    logging.error("ignored: rollback failed: %s", e)
        else:
            self._tx.flush()
            self._tx._big_buf.flush()  # flush the bigcol buffer
            self._client._request(
                path="/api/table/v2/commit",
                params={
                    "table_id": self._id,
                    "tx_id": self._tx._id,
                },
            )
        self._tx = None

    def schema(self) -> pa.Schema:
        """
        return the schema of the table, or None if the schema is not set
        """
        return self._outer_schema

    # used as a filter in Cursor, encode in tx
    def _decode(self, b: pa.RecordBatch) -> pa.RecordBatch:
        b = self._bigcol.decode(b)  # convert to panda first, then do the magic
        b = bsquare.decode(b)
        return b

    def _select(
        self,
        tx: str = "",
        type: str = "select",
        inner_query: Optional[exp.Op] = None,
        aggr: Optional[dict] = None,
        cols: Optional[List[str]] = None,
        vars: Union[Dict, List, None] = None,
        by: Optional[str] = None,
        cursor: str = "",
        timeout: float = 30.0,
    ) -> Iterator[pa.RecordBatch]:
        # t0 = time.perf_counter()
        initialized = False
        while not initialized or cursor:
            # do while - run at least once
            initialized = True
            res = self._client._request(
                path="/api/table/v2/" + type,
                params={
                    "table_id": self._id,
                    "tx_id": tx,
                },
                data={
                    "query": str(inner_query) if inner_query else None,
                    "cols": cols,
                    "cursor": cursor,
                    "aggr": aggr,
                    "by": by,
                    "vars": vars_to_json(vars),
                    "timeout": timeout,
                },
            )
            reader = res.reader()
            r = pa.ipc.RecordBatchStreamReader(reader)
            for bm in r.iter_batches_with_custom_metadata():
                if bm.custom_metadata and b"error" in bm.custom_metadata:
                    raise Exception("server error: %s" % bm.custom_metadata[b"error"].decode())

                if bm.custom_metadata and b"cursor" in bm.custom_metadata:
                    cursor = bm.custom_metadata[b"cursor"].decode()
                    logging.warning("response is partially processed with cursor %s", cursor)
                else:
                    # logging.info("no cursor received on table client, setting to empty")
                    cursor = None

                # logging.info("got batch with %d rows", bm.batch.num_rows)
                yield bm.batch

    def _insert_batch(
        self,
        data: pa.RecordBatch,
        tx: str = "",
    ):
        assert self._inner_schema
        buf = io.BytesIO()
        w = pa.ipc.RecordBatchStreamWriter(buf, self._inner_schema)
        w.write_batch(data)
        w.close()

        self._client._request(
            path="/api/table/v2/insert",
            params={
                "table_id": self._id,
                "tx_id": tx,
            },
            data=buf.getvalue(),
        ).json()
