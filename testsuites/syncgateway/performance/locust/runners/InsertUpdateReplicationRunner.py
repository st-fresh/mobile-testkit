import sys
import time
import os

from optparse import OptionParser

from keywords.ClusterKeywords import ClusterKeywords

from UserCreationRunner import create_users
from locust_runner import run_locust_scenario

def insert_update_replication(target, num_pushers, pusher_user_prefix, num_pullers, puller_user_prefix, total_docs, doc_size):

    print("*** LOCUST ***")
    print("Number of pushers: {}".format(num_pushers))
    print("Number of pullers: {}".format(num_pullers))

    print("*** Starting statsd ***")
    print("Starting Server on :8125 ...\n")

    print("*** Setting up environment ***\n")

    # Set needed environment variables
    os.environ["LOCUST_NUM_PUSHERS"] = str(num_pushers)
    os.environ["LOCUST_PUSHER_USER_PREFIX"] = pusher_user_prefix
    os.environ["LOCUST_NUM_PULLERS"] = str(num_pullers)
    os.environ["LOCUST_PULLER_USER_PREFIX"] = puller_user_prefix
    os.environ["LOCUST_DOC_SIZE"] = str(doc_size)
    os.environ["LOCUST_NUM_WRITES_PER_USER"] = str(total_docs / num_pushers)

    scenario = "InsertUpdateReplication"

    print("*** Running Locust: {} ***".format(scenario))
    print("Environment:")
    print("LOCUST_NUM_PUSHERS: {}".format(os.environ["LOCUST_NUM_PUSHERS"]))
    print("LOCUST_NUM_PULLERS: {}".format(os.environ["LOCUST_NUM_PULLERS"]))
    print("LOCUST_DOC_SIZE: {}".format(os.environ["LOCUST_DOC_SIZE"]))
    print("LOCUST_NUM_WRITES_PER_USER: {}".format(os.environ["LOCUST_NUM_WRITES_PER_USER"]))

    start = time.time()

    run_locust_scenario(
        name=scenario,
        target=target,
        clients=str(num_pushers + num_pushers),
    )

    doc_add_time = time.time() - start
    print("Doc add took: {}s".format(doc_add_time))

    print("*** Tearing down environment ***\n")
    del os.environ["LOCUST_NUM_PUSHERS"]
    del os.environ["LOCUST_PUSHER_USER_PREFIX"]
    del os.environ["LOCUST_NUM_PULLERS"]
    del os.environ["LOCUST_PULLER_USER_PREFIX"]
    del os.environ["LOCUST_DOC_SIZE"]
    del os.environ["LOCUST_NUM_WRITES_PER_USER"]

    # This is arbirary at the moment until we define KPIs
    assert doc_add_time < 120, "Doc adds took longer than expected"


def validate_opts(target, num_pushers, num_pullers, total_docs, doc_size):

    assert target is not None, "Make sure you have defined a sync_gateway target for locust, ex. ('http://192.168.33.11')"
    assert num_pullers >= 0, "'num_pushers' should be >= 0"
    assert num_pushers >= 0, "'num_pullers' should be >= 0"
    assert num_pushers == num_pullers, "'num_pushers' should be equal to 'num_pullers'"
    assert total_docs >= num_pushers, "'total_docs' must be greater than or equal to 'num_pushers'"
    assert total_docs % num_pushers == 0, "'total_docs' should be a multiple of 'num_pushers'"
    assert total_docs >= 0, "'total_docs' should be >= 0"
    assert doc_size >= 0, "'doc_size' should be >= 0"


if __name__ == "__main__":
    usage = """usage: InsertUpdateReplication.py
    --target=http://192.168.33.11
    --num-pushers=100
    --num-pullers=100
    --total-docs=1000
    --doc-size=1024

    Create 0-99 channels for total dataset. Each doc is assigned 1 channel in
    this range.
    """

    parser = OptionParser(usage=usage)

    parser.add_option("", "--target",
                      action="store", type="string", dest="target", default=None,
                      help="target to point locust at")

    parser.add_option("", "--num-pushers",
                      action="store", type="int", dest="num_pushers",
                      help="number of doc pushers")

    parser.add_option("", "--num-pullers",
                      action="store", type="int", dest="num_pullers",
                      help="number of doc pullers")

    parser.add_option("", "--total-docs",
                      action="store", type="int", dest="total_docs",
                      help="total number of docs to write")

    parser.add_option("", "--doc-size",
                      action="store", type="int", dest="doc_size",
                      help="total number of docs to write")

    arg_parameters = sys.argv[1:]

    (opts, args) = parser.parse_args(arg_parameters)

    print("*** Write Thoughput ***")
    print("num_pushers: {}".format(opts.num_pushers))
    print("num_pullers: {}".format(opts.num_pullers))
    print("total_docs: {}".format(opts.total_docs))
    print("doc_size: {}\n".format(opts.doc_size))

    validate_opts(
        target=opts.target,
        num_pushers=opts.num_pushers,
        num_pullers=opts.num_pullers,
        total_docs=opts.total_docs,
        doc_size=opts.doc_size
    )

    cluster = ClusterKeywords()
    config = "resources/sync_gateway_configs/performance/sync_gateway_default_performance_cc.json"
    print("*** Resetting Cluster with {} ***".format(config))
    cluster.reset_cluster(config)

    pusher_user_prefix = "pusher"
    puller_user_prefix = "puller"

    # Create pushers
    create_users(
        target=opts.target,
        user_prefix=pusher_user_prefix,
        num_writers=opts.num_pushers,
        num_channels=opts.num_pushers,
        num_channels_per_doc=1
    )

    # Create pullers
    create_users(
        target=opts.target,
        user_prefix=puller_user_prefix,
        num_writers=opts.num_pullers,
        num_channels=opts.num_pullers,
        num_channels_per_doc=1
    )

    # Run scenario
    insert_update_replication(
        target=opts.target,
        num_pushers=opts.num_pushers,
        pusher_user_prefix=pusher_user_prefix,
        puller_user_prefix=puller_user_prefix,
        num_pullers=opts.num_pullers,
        total_docs=opts.total_docs,
        doc_size=opts.doc_size
    )
