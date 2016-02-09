import pytest


def pytest_addoption(parser):
    # Delete / Create server buckets between each test
    parser.addoption("--reset",
                     action="store_true",
                     dest="reset",
                     default=False,
                     help="Delete data before test")

    parser.addoption("--mode",
                     action="store",
                     type="string",
                     dest="mode",
                     default=None,
                     help="Mode of running test ('distributed_index or channel_cache')")

# http://pytest.org/dev/example/simple.html#making-test-result-information-available-in-fixtures
@pytest.mark.tryfirst
def pytest_runtest_makereport(item, call, __multicall__):
    # execute all other hooks to obtain the report object
    rep = __multicall__.execute()

    # set an report attribute for each phase of a call, which can
    # be "setup", "call", "teardown"
    setattr(item, "rep_" + rep.when, rep)
    return rep
