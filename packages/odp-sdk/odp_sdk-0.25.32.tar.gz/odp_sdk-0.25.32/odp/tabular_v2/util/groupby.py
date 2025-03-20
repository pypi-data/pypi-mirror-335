import logging
from typing import Dict, Iterable, Iterator, Union

import pandas as pd
import pyarrow as pa
from pandas.core.groupby import DataFrameGroupBy


# EXPERIMENTAL
def group_by(
    iter: Iterable[pa.RecordBatch],
    group_by: str,
    agg: Dict[str, Union[list, str]],
):
    fields = set(agg.keys())
    fields.add(group_by)
    cum = None
    for b in iter:
        d = b.select(fields).to_pandas()
        cum = d if cum is None else pd.concat([cum, d])
        g: DataFrameGroupBy = cum.groupby(group_by)
        logging.info("group %s", g.agg(agg))


def test_group_by():
    schema = pa.schema(
        [
            pa.field("id", pa.string()),
            pa.field("cat", pa.string()),
            pa.field("temp", pa.float64()),
            pa.field("visits", pa.int64()),
        ]
    )
    d1 = [
        {"id": "001", "cat": "A", "temp": 21.0, "visits": 3},
        {"id": "002", "cat": "A", "temp": 23.0, "visits": 7},
        {"id": "003", "cat": "B", "temp": 22.0, "visits": 5},
        {"id": "004", "cat": "B", "temp": 24.0, "visits": 9},
    ]
    d2 = [
        {"id": "005", "cat": "A", "temp": 25.0, "visits": 1},
        {"id": "006", "cat": "A", "temp": 27.0, "visits": 2},
        {"id": "007", "cat": "B", "temp": 26.0, "visits": 4},
        {"id": "008", "cat": "B", "temp": 28.0, "visits": 6},
    ]

    def gen() -> Iterator[pa.RecordBatch]:
        yield pa.RecordBatch.from_pylist(d1, schema=schema)
        yield pa.RecordBatch.from_pylist(d2, schema=schema)

    group_by(gen(), "cat", {"temp": ["min", "max", "mean", "count"], "visits": "sum"})
