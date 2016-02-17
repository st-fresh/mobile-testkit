#!/usr/bin/env python

import logging
import os
import pytest
import shutil
import sys
from optparse import OptionParser

import lib.settings
import functional_tests.plugins
from lib.constants import RunMode

log = logging.getLogger(lib.settings.LOGGER)


if __name__ == "__main__":
    usage = """
    usage: ./test.py
    usage: ./test.py -t test_name
    usage: ./test.py -t test_name -r 10
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

    print(opts)

    plugins = [functional_tests.plugins]

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

    # Delete / Create results/
    if os.path.isdir("results"):
        shutil.rmtree("results/")
    os.makedirs("results")

    if opts.test:
        if opts.mode is None:
            print("Make sure you specify a mode to run (ex. -m CC)")
            sys.exit(1)
        # Target individual test with optional repeat
        log.info("Running individual test(s) matching the pattern {}".format(opts.test))
        count = 0
        while count < opts.repeat:

            pytest.main('-s --junit-xml=results/{}-{}.xml --mode={} -k "{} and {} and not RESET" --collect-only'.format(opts.test, count, opts.mode, opts.test, opts.mode), plugins=plugins)
            status = pytest.main('-s --junit-xml=results/{}-{}.xml --mode={} -k "{} and {} and not RESET"'.format(opts.test, count, opts.mode, opts.test, opts.mode), plugins=plugins)
            pytest.main('-s --junit-xml=results/{}-{}.xml --reset --mode={} -k "{} and {} and RESET" --collect-only'.format(opts.test, count, opts.mode, opts.test, opts.mode), plugins=plugins)
            status = pytest.main('-s --junit-xml=results/{}-{}.xml --reset --mode={} -k "{} and {} and RESET"'.format(opts.test, count, opts.mode, opts.test, opts.mode), plugins=plugins)

            if opts.repeat > 1 and status != 0:
                # Break loop in first failure if repeating
                break
            count += 1
        sys.exit(0)

    if opts.mode == RunMode.all_clean:
        log.info("RUNNING ALL tests with reset!")
        # Run all tests with data reset between each test
        status = pytest.main('-s --junit-xml=results/di-no-reset.xml --reset  --mode="DI" -k "DI and not RESET"', plugins=plugins)
        assert(status == 0)
        status = pytest.main('-s --junit-xml=results/cc-no-reset.xml --reset --mode="CC" -k "CC and not RESET"', plugins=plugins)
        assert(status == 0)
        status = pytest.main('-s --junit-xml=results/di-reset.xml --reset --mode="DI" -k "DI and RESET"', plugins=plugins)
        assert(status == 0)
        status = pytest.main('-s --junit-xml=results/cc-reset.xml --reset --mode="CC" -k "CC and RESET"', plugins=plugins)
        assert(status == 0)
    else:
        # Individual filters
        if opts.mode == RunMode.distributed_index:
            log.info("Running DI tests")
            status = pytest.main('-s --junit-xml=results/di-no-reset.xml --mode=DI -k "DI and not RESET"', plugins=plugins)
            assert(status == 0)
        elif opts.mode == RunMode.channel_cache:
            log.info("Running CC tests")
            pytest.main('-s --junit-xml=results/cc-no-reset.xml --mode="CC" -k "CC and not RESET" --collect-only', plugins=plugins)
            status = pytest.main('-s --junit-xml=results/cc-no-reset.xml --mode="CC" -k "CC and not RESET"', plugins=plugins)
            assert(status == 0)
        elif opts.mode == RunMode.reset:
            log.info("Running DI tests")
            status = pytest.main('-s --junit-xml=results/di-reset.xml --reset --mode="DI" -k "DI and RESET"', plugins=plugins)
            assert(status == 0)
            status = pytest.main('-s --junit-xml=results/cc-reset.xml --reset --mode="CC" -k "CC and RESET"', plugins=plugins)
            assert(status == 0)
        else:
            log.info("RUNNING ALL tests!")
            # Run all tests without reset except where declared in tag
            status = pytest.main('-s --junit-xml=results/di-no-reset.xml --mode="DI" -k "DI and not RESET"', plugins=plugins)
            assert(status == 0)
            status = pytest.main('-s --junit-xml=results/cc-no-reset.xml --mode="CC" -k "CC and not RESET"', plugins=plugins)
            assert(status == 0)
            status = pytest.main('-s --junit-xml=results/di-reset.xml --reset --mode="DI" -k "DI and RESET"', plugins=plugins)
            assert(status == 0)
            status = pytest.main('-s --junit-xml=results/cc-reset.xml --reset --mode="CC" -k "CC and RESET"', plugins=plugins)
            assert(status == 0)
