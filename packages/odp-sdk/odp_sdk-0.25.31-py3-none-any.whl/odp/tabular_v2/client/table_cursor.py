import logging
import time
from typing import Callable, Iterator

import pandas as pd
import pyarrow as pa


class CursorException(Exception):
    """Raised when the client is required to connect again with the given cursor to fetch more data"""

    def __init__(self, cursor: str):
        self.cursor = cursor


class Cursor:
    """
    A Cursor, which reads data from a scanner and allow the user to iterate over in different flavors
    It internally uses a scanner to get the data, and perform multiple requests if a cursor is returned

    it's created by the Table.select() method
    """

    def __init__(
        self,
        scanner: Callable[[str], Iterator[pd.DataFrame]],
        schema: pa.Schema,
    ):
        self.scanner = scanner
        self.schema = schema

    def batches(self) -> Iterator[pa.RecordBatch]:
        """
        Allow the client to iterate over pyarrow Record Batches:

            for batch in tab.select().batches():
                print(batch.num_rows)
        """
        for df in self.dataframes():
            yield pa.RecordBatch.from_pandas(df, schema=self.schema)

    def dataframes(self) -> Iterator[pd.DataFrame]:
        """
        Allow the client to iterate over pandas DataFrames:

            for batch in tab.select().dataframes():
                print(len(batch))
        """
        t0 = time.perf_counter()
        cursor = ""
        ct = 0
        rows = 0
        while True:
            try:
                for df in self.scanner(cursor):
                    ct += 1
                    rows += len(df)
                    yield df
            except CursorException as e:
                cursor = e.cursor
                continue  # FIXME: Should not be raised?
            break
        logging.info("got %d batches with %d rows in %.2fs", ct, rows, time.perf_counter() - t0)

    def rows(self) -> Iterator[dict]:
        """
        Allow the client to iterate over each rows as a python dictionary:

            for row in tab.select().rows():
                print(row)
        """
        for df in self.dataframes():
            for row in df.to_dict(orient="records"):
                yield row

    def pages(self, size: int = 0) -> Iterator[list[dict]]:
        """
        Allow the client to iterate over pages of data, where each page is a list of python dictionaries.

            for page in tab.select().pages(1_000):
                print(len(page))

        If no size is specified, it will make a page for each chunk of data retrieved from the server
        """
        if size < 1:  # page based on what we get
            for df in self.dataframes():
                yield df.to_dict(orient="records")
            return

        # page based on page_size
        buf: list[dict] = []
        for df in self.dataframes():
            buf.extend(df.to_dict(orient="records"))
            while len(buf) >= size:
                yield buf[:size]
                buf = buf[size:]
        if len(buf) > 0:
            yield buf
