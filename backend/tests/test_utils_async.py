import asyncio


def test_run_cpu_bound():
    import app.utils as utils

    def small_work(x):
        return x * 2

    res = asyncio.get_event_loop().run_until_complete(utils.run_cpu_bound(small_work, 3))
    assert res == 6
