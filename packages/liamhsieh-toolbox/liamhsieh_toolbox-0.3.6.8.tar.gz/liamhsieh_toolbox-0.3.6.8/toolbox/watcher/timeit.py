import datetime as dt
from typing import (
    Callable,
)

def timeit(method: Callable) -> Callable:
    def time_and_run(obj, *args, **kw):
        ts = dt.datetime.now()
        result = method(obj, *args, **kw)
        te = dt.datetime.now()

        query_name = None
        if method.__name__ == 'pull_predefined_query':
            query_name = args[0]

        record = {
            'code': query_name or method.__name__,
            'start_time': ts,
            'end_time': te,
            'run time(sec)': (te - ts).total_seconds(),
        }
        if hasattr(obj,"watcher"):
            obj.watcher["run_time"] = record
        else:
            watcher = {}
            setattr(obj,"watcher",watcher)
            obj.watcher["run_time"] = record
        return result

    return time_and_run