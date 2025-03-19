import time


def rate_limit_iterator(iterator, iters_per_second: float, start: float | None = None):
    start = start or time.time()
    for i, it in enumerate(iterator):
        yield it
        time.sleep(max(0, (i / iters_per_second) - (time.time() - start)))
