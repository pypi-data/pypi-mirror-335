from concurrent.futures import Future
from concurrent.futures.thread import ThreadPoolExecutor

pool = ThreadPoolExecutor(4)  # this is a mix of CPU and waiting for CDF...


# TODO(oha): can we remove this?
class Group:
    """
    Create a context of futures that will be awaited on exit
    this prevents the risk of missing an exception in a future
    """

    def __init__(self):
        self.futures = []

    def submit(self, fn, *args, **kwargs) -> Future:
        """submit a new task to the pool"""
        f = pool.submit(fn, *args, **kwargs)
        self.futures.append(f)
        return f

    def results(self) -> list:
        """early return the results of all futures submitted so far"""
        out = [f.result() for f in self.futures]
        self.futures = []
        return out

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.results()
