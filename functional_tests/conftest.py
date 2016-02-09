import pytest


def pytest_addoption(parser):
    # run all tests with *_di.json configurations
    parser.addoption("--ac",
                     action="store_true",
                     dest="run_sg_accel_tests",
                     default=False,
                     help="Run tests with sg_accel configured")

    # run all tests with *_cc.json configurations
    parser.addoption("--mode",
                     action="store",
                     dest="mode",
                     default="channel_cache",
                     help="Run tests in channel cache configuration")

    # run all tests with *_cc.json configurations
    parser.addoption("--rs",
                     action="store_true",
                     dest="run_reset_tests",
                     default=False,
                     help="Run tests with RESET in configuration name")

    # Delete / Create server buckets between each test
    parser.addoption("--reset-data",
                     action="store_true",
                     dest="run_all_tests_with_reset",
                     default=False,
                     help="Run all tests and reset data between each test")

# http://pytest.org/dev/example/simple.html#making-test-result-information-available-in-fixtures
@pytest.mark.tryfirst
def pytest_runtest_makereport(item, call, __multicall__):
    # execute all other hooks to obtain the report object
    rep = __multicall__.execute()

    # set an report attribute for each phase of a call, which can
    # be "setup", "call", "teardown"
    setattr(item, "rep_" + rep.when, rep)
    return rep
