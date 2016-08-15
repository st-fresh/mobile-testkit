import sys
import subprocess
import os
import time

from optparse import OptionParser

from keywords.constants import RESULTS_DIR
from keywords.ClusterKeywords import ClusterKeywords

def create_users(target, num_writers, num_channels, num_channels_per_doc):

    start = time.time()

    clients = str(num_writers)

    # POST _user + POST + _session = num_writers * 2 requests
    num_requests = (num_writers * 2)
    num_request = str(num_requests)

    print("*** LOCUST ***")
    print("clients: {}".format(clients))
    print("num_request: {}\n".format(num_request))

    print("*** Starting statsd ***")
    print("Starting Server on :8125 ...\n")

    print("*** Setting up environment ***\n")

    # Set needed environment variables
    os.environ["LOCUST_NUM_CLIENTS"] = str(clients)
    os.environ["LOCUST_NUM_CHANNELS"] = str(num_channels)
    os.environ["LOCUST_NUM_CHANNELS_PER_DOC"] = str(num_channels_per_doc)

    scenario = "UserCreation.py"

    print("*** Running Locust: {} ***".format(scenario))
    print("Environment:")
    print("LOCUST_NUM_CHANNELS: {}".format(os.environ["LOCUST_NUM_CHANNELS"]))
    print("LOCUST_NUM_CHANNELS_PER_DOC: {}".format(os.environ["LOCUST_NUM_CHANNELS_PER_DOC"]))

    results_path = "{}/perf/syncgateway/UserCreation.txt".format(RESULTS_DIR)

    with open(results_path, "w") as f:
        locust_proc = subprocess.Popen(
            [
                "locust",
                "--no-web",
                "--loglevel", "INFO",
                "--only-summary",
                "--host", target,
                "--clients", clients,
                "--hatch-rate", "50",
                "--num-request", num_request,
                "-f", "testsuites/syncgateway/performance/locust/scenarios/{}".format(scenario)
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

        for line in iter(locust_proc.stdout.readline, ''):
            sys.stdout.write(line)
            f.write(line)

    print("*** Tearing down environment ***\n")

    # Parse Values
    with open(results_path) as f:
        output = f.read()
        print(output)

    # Clean up environment variables
    del os.environ["LOCUST_NUM_CLIENTS"]
    del os.environ["LOCUST_NUM_CHANNELS"]
    del os.environ["LOCUST_NUM_CHANNELS_PER_DOC"]

    user_creation_time = time.time() - start
    print("User creation took: {}s".format(user_creation_time))

def validate_opts(target, num_writers, num_channels, num_channels_per_doc):

    assert target is not None, "Make sure you have defined a sync_gateway target for locust, ex. ('http://192.168.33.11')"
    assert num_writers >= 0, "'num_writers' should be >= 0"
    assert num_channels >= 0, "'num_channels' should be >= 0"
    assert num_channels_per_doc >= 0, "'num_channels_per_doc' should be >= 0"

    if num_channels_per_doc > num_channels:
        raise ValueError("'num_channels_per_doc' cannot exceed the number of 'num_channels'")

    # Make sure all channels are used
    # Ex. 100 writers, 10 channels, 10 writers with 10 channel
    assert num_writers % num_channels == 0, "'num_writers' should be a multiple of 'num_channels'"
    assert num_channels % num_channels_per_doc == 0, "'num_channels' should be a multiple of 'num_channels_per_doc'"

if __name__ == "__main__":
    usage = """usage: UserCreationRunner.py
    --target=http://192.168.33.11
    --num-writers=1000
    --num-channels=100
    --num-channels-per-doc=1

    Create 0-99 channels for total dataset. Each doc is assigned 1 channel in
    this range.
    """

    cluster = ClusterKeywords()
    cluster.reset_cluster("resources/sync_gateway_configs/performance/sync_gateway_default_performance_cc.json")

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

    arg_parameters = sys.argv[1:]

    (opts, args) = parser.parse_args(arg_parameters)



    validate_opts(
        target=opts.target,
        num_writers=opts.num_writers,
        num_channels=opts.num_channels,
        num_channels_per_doc=opts.num_channels_per_doc
    )

    create_users(
        target=opts.target,
        num_writers=opts.num_writers,
        num_channels=opts.num_channels,
        num_channels_per_doc=opts.num_channels_per_doc
    )

