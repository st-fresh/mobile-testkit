#!/usr/bin/env python

import logging
import os
import pytest
import sys
from optparse import OptionParser

import lib.settings
from lib.constants import RunMode

log = logging.getLogger(lib.settings.LOGGER)


class RunOptions:

    def __init__(self, id, mode, reset_data):
        self.id = id,
        self.mode = mode
        self.reset_data = reset_data

    def validate(self):
        if self.mode not in ["CC", "DI", "RS", "ALL"]:
            raise ValueError("The only supported modes are 'CC', 'DI', 'RS', and 'ALL'")


if __name__ == "__main__":
    usage = """
    usage: ./test.py
    usage: ./test.py -t test_samplefile.py
    usage: ./test.py -t test_samplefile.py::test_test1 -r 10
    usage: ./test.py -m DI
    usage: ./test.py -m CC
    usage: ./test.py -m ALL
    usage: ./test.py -m ALLCLEAN
    """

    parser = OptionParser(usage=usage)

    parser.add_option("-t",
                      "--test",
                      action="store",
                      type="string",
                      dest="test",
                      default=None,
                      help="test or fixture to run")

    parser.add_option("-r",
                      "--repeat",
                      action="store",
                      type="int",
                      dest="repeat",
                      default=1,
                      help="repeat number of times (only works with -t)")

    parser.add_option("-m",
                      "--mode",
                      action="store",
                      dest="mode",
                      default=None,
                      help="Run tests in channel cache configuration")

    (opts, args) = parser.parse_args(sys.argv[1:])

    # Delete sg logs in /tmp
    # filelist = [f for f in os.listdir("/tmp") if f.endswith(".zip") or f.endswith("sglogs")]
    # for f in filelist:
    #     if os.path.isfile("/tmp/" + f):
    #         os.remove("/tmp/" + f)
    #     else:
    #         shutil.rmtree("/tmp/" + f)

    # Delete test-framework.log
    if os.path.isfile("test-framework.log"):
        os.remove("test-framework.log")

    if opts.test:
        # Target individual test with optional repeat
        count = 0
        while count < opts.repeat:
            status = pytest.main('-s --junit-xml=results.xml --mode="DI" {}'.format(opts.test))
            if status != 0:
                break
            status = pytest.main('-s --junit-xml=results.xml --mode="CC" {}'.format(opts.test))
            if status != 0:
                break
            count += 1
        sys.exit(0)

    if opts.mode == RunMode.all_clean:
        log.info("RUNNING ALL tests with reset!")
        # Run all tests with data reset between each test
        status = pytest.main('-s --junit-xml=results.xml --reset  --mode="DI" -k "DI and not RESET"')
        assert(status == 0)
        status = pytest.main('-s --junit-xml=results.xml --reset --mode="CC" -k "CC and not RESET"')
        assert(status == 0)
        status = pytest.main('-s --junit-xml=results.xml --reset --mode="DI" -k "DI and RESET"')
        assert(status == 0)
        status = pytest.main('-s --junit-xml=results.xml --reset --mode="CC" -k "CC and RESET"')
        assert(status == 0)
    else:
        # Individual filters
        if opts.mode == RunMode.distributed_index:
            log.info("Running DI tests")
            status = pytest.main('-s --junit-xml=results.xml --mode="DI" -k "DI and not RESET"')
            assert(status == 0)
        elif opts.mode == RunMode.channel_cache:
            log.info("Running DI tests")
            status = pytest.main('-s --junit-xml=results.xml --mode="CC" -k "CC and not RESET"')
            assert(status == 0)
        elif opts.mode == RunMode.reset:
            log.info("Running DI tests")
            status = pytest.main('-s --junit-xml=results.xml --reset --mode="DI" -k "DI and RESET"')
            assert(status == 0)
            status = pytest.main('-s --junit-xml=results.xml --reset --mode="CC" -k "CC and RESET"')
            assert(status == 0)
        else:
            log.info("RUNNING ALL tests!")
            # Run all tests without reset except where declared in tag
            status = pytest.main('-s --junit-xml=results.xml --mode="DI" -k "DI and not RESET"')
            assert(status == 0)
            status = pytest.main('-s --junit-xml=results.xml --mode="CC" -k "CC and not RESET"')
            assert(status == 0)
            status = pytest.main('-s --junit-xml=results.xml --reset --mode="DI" -k "DI and RESET"')
            assert(status == 0)
            status = pytest.main('-s --junit-xml=results.xml --reset --mode="CC" -k "CC and RESET"')
            assert(status == 0)
