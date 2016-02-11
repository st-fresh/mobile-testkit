import sys
import os
from optparse import OptionParser

from lib.cluster import Cluster
from lib.constants import RunMode
from functional_tests.fixtures import TestRunOptions

if __name__ == "__main__":
    usage = """usage: reset_cluster.py
    --conf=<name-of-conf>
    """

    parser = OptionParser(usage=usage)

    parser.add_option("", "--conf",
                      action="store", type="string", dest="conf", default=None,
                      help="name of configuration in conf/ to reset cluster with")

    arg_parameters = sys.argv[1:]

    (opts, args) = parser.parse_args(arg_parameters)

    cluster = Cluster()
    if opts.conf.endswith("_cc.json"):
        run_mode = RunMode.channel_cache
    else:
        run_mode = RunMode.distributed_index

    print("Reseting cluster with the conf: {}, Detected {} mode".format(opts.conf, run_mode))
    cluster.reset(opts.conf, TestRunOptions("Provision", True, run_mode))


