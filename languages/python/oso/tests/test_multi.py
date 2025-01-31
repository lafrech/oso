import random
import time
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures

from oso import Oso, OsoError

ITERS = 100


class X:
    def __init__(self, x):
        self.x = x

    def __eq__(self, other):
        return self.x == other.x


def r():
    return random.randint(0, 5)


def exhaust(i):
    try:
        for _ in i:
            pass
    except OsoError:
        pass


def torch_oso(oso):
    for i in range(ITERS):
        x = X(r())
        y = X(r())
        exhaust(oso.query_rule("equal", x, y))
        time.sleep(random.random() * 0.01)

        exhaust(oso.query_rule("equal", r(), r()))

        exhaust(oso.query_rule("equal", 1))
        time.sleep(random.random() * 0.01)

        exhaust(oso.query_rule("equal", r(), str(r())))


def test_multi():
    oso = Oso()
    oso.load_str("equal(x, y) if x == y;")

    tp = ThreadPoolExecutor(max_workers=8)

    futures = []
    for _ in range(32):
        futures.append(tp.submit(torch_oso, oso))

    for i, future in enumerate(concurrent.futures.as_completed(futures)):
        future.result()

    # If we got here none of these crashed.
    assert True
