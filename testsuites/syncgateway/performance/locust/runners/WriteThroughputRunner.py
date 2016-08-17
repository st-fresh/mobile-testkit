import sys
import time
import os

from optparse import OptionParser

from keywords.ClusterKeywords import ClusterKeywords

from UserCreationRunner import create_users
from locust_runner import run_locust_scenario

def write_docs(target, num_writers, total_docs, doc_size):

    clients = str(num_writers)

    # number of POST _session +
    # number of GET _user for channels +
    # number of PUT docs
    num_request = str((num_writers * 2) + total_docs)

    print("*** LOCUST ***")
    print("clients: {}".format(clients))
    print("num_request: {}\n".format(num_request))

    print("*** Starting statsd ***")
    print("Starting Server on :8125 ...\n")

    print("*** Setting up environment ***\n")

    # Set needed environment variables
    os.environ["LOCUST_DOC_SIZE"] = str(doc_size)
    os.environ["LOCUST_NUM_WRITES_PER_USER"] = str(total_docs / num_writers)

    scenario = "WriteThroughput"

    print("*** Running Locust: {} ***".format(scenario))
    print("Environment:")
    print("LOCUST_DOC_SIZE: {}".format(os.environ["LOCUST_DOC_SIZE"]))
    print("LOCUST_NUM_WRITES_PER_USER: {}".format(os.environ["LOCUST_NUM_WRITES_PER_USER"]))

    start = time.time()

    run_locust_scenario(
        name=scenario,
        target=target,
        clients=clients,
    )

    doc_add_time = time.time() - start
    print("Doc add took: {}s".format(doc_add_time))

    print("*** Tearing down environment ***\n")
    del os.environ["LOCUST_DOC_SIZE"]
    del os.environ["LOCUST_NUM_WRITES_PER_USER"]

    # This is arbirary at the moment until we define KPIs
    assert doc_add_time < 120, "Doc adds took longer than expected"


def validate_opts(target, num_writers, num_channels, num_channels_per_doc, total_docs, doc_size):

    assert target is not None, "Make sure you have defined a sync_gateway target for locust, ex. ('http://192.168.33.11')"
    assert num_writers >= 0, "'num_writers' should be >= 0"
    assert total_docs >= num_writers, "'total_docs' must be greater than or equal to 'num_writers'"
    assert total_docs % num_writers == 0, "'total_docs' should be a multiple of 'num_writers'"
    assert num_channels >= 0, "'num_channels' should be >= 0"
    assert num_channels_per_doc >= 0, "'num_channels_per_doc' should be >= 0"
    assert total_docs >= 0, "'total_docs' should be >= 0"
    assert doc_size >= 0, "'doc_size' should be >= 0"

    if num_channels_per_doc > num_channels:
        raise ValueError("'num_channels_per_doc' cannot exceed the number of 'num_channels'")

    # Make sure all channels are used
    # Ex. 100 writers, 10 channels, 10 writers with 10 channel
    assert num_writers % num_channels == 0, "'num_writers' should be a multiple of 'num_channels'"
    assert num_channels % num_channels_per_doc == 0, "'num_channels' should be a multiple of 'num_channels_per_doc'"

    # TODO: Make sure distribution of channels is equal
    # Ex. 20 writers, 10 channels, 2 channels per doc
    # Make sure sets 1-5 are equally represented in test case

if __name__ == "__main__":
    usage = """usage: WriteThoughputRunner.py
    --target=http://192.168.33.11
    --num-writers=1000
    --num-channels=100
    --num-channels-per-doc=1
    --total-docs=10000
    --doc-size=4000

    Create 0-99 channels for total dataset. Each doc is assigned 1 channel in
    this range.
    """

    parser = OptionParser(usage=usage)

    parser.add_option("", "--target",
                      action="store", type="string", dest="target", default=None,
                      help="target to point locust at")

    parser.add_option("", "--num-writers",
                      action="store", type="int", dest="num_writers",
                      help="number of writers")

    parser.add_option("", "--num-channels",
                      action="store", type="int", dest="num_channels",
                      help="number of channels that docs ")

    parser.add_option("", "--num-channels-per-doc",
                      action="store", type="int", dest="num_channels_per_doc",
                      help="number of channels that docs ")

    parser.add_option("", "--total-docs",
                      action="store", type="int", dest="total_docs",
                      help="total number of docs to write")

    parser.add_option("", "--doc-size",
                      action="store", type="int", dest="doc_size",
                      help="size of each doc")

    arg_parameters = sys.argv[1:]

    (opts, args) = parser.parse_args(arg_parameters)

    print("*** Write Thoughput ***")
    print("num_writers: {}".format(opts.num_writers))
    print("num_channels: {}".format(opts.num_channels))
    print("num_channels_per_doc: {}".format(opts.num_channels_per_doc))
    print("total_docs: {}".format(opts.total_docs))
    print("doc_size: {}\n".format(opts.doc_size))

    validate_opts(
        target=opts.target,
        num_writers=opts.num_writers,
        num_channels=opts.num_channels,
        num_channels_per_doc=opts.num_channels_per_doc,
        total_docs=opts.total_docs,
        doc_size=opts.doc_size
    )

    cluster = ClusterKeywords()
    config = "resources/sync_gateway_configs/performance/sync_gateway_default_performance_cc.json"
    print("*** Resetting Cluster with {} ***".format(config))
    cluster.reset_cluster(config)

    # Create users / session and store info in tmp file
    create_users(
        target=opts.target,
        user_prefix="user",
        num_writers=opts.num_writers,
        num_channels=opts.num_channels,
        num_channels_per_doc=opts.num_channels_per_doc
    )

    # Write docs using the provided users
    write_docs(
        target=opts.target,
        num_writers=opts.num_writers,
        total_docs=opts.total_docs,
        doc_size=opts.doc_size
    )
