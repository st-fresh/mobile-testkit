import sys
import subprocess
import os

from optparse import OptionParser

def validate_opts(num_writers, num_channels, num_channels_per_doc, total_docs, doc_size):

    assert num_writers >= 0, "'num_writers' should be >= 0"
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
    --num-writers=1000
    --num-channels=100
    --num-channels-per-doc=1
    --total-docs=10000
    --doc-size=4000

    Create 0-99 channels for total dataset. Each doc is assigned 1 channel in
    this range.
    """

    parser = OptionParser(usage=usage)

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
        num_writers=opts.num_writers,
        num_channels=opts.num_channels,
        num_channels_per_doc=opts.num_channels_per_doc,
        total_docs=opts.total_docs,
        doc_size=opts.doc_size
    )

    clients = str(opts.num_writers)

    # POST _user + POST + _session = opts.num_writers * 2 requests
    # POST docs = total_docs requests
    num_requests = (opts.num_writers * 2) + opts.total_docs
    num_request = str(num_requests)

    print("*** LOCUST ***")
    print("clients: {}".format(clients))
    print("num_request: {}\n".format(num_request))

    print("*** Starting statsd ***")
    print("Starting Server on :8125 ...\n")

    print("*** Setting up environment ***\n")

    # Set needed environment variables
    os.environ["LOCUST_NUM_CHANNELS"] = str(opts.num_channels)
    os.environ["LOCUST_NUM_CHANNELS_PER_DOC"] = str(opts.num_channels_per_doc)

    scenario = "WriteThroughputDef.py"

    print("*** Running Locust ***")
    print("Environment:")
    print("LOCUST_NUM_CHANNELS: {}".format(os.environ["LOCUST_NUM_CHANNELS"]))
    print("LOCUST_NUM_CHANNELS_PER_DOC: {}".format(os.environ["LOCUST_NUM_CHANNELS_PER_DOC"]))
    print("Scenario: {}\n".format(scenario))

    with open("WriteThroughPut.txt", "w") as f:
        locust_proc = subprocess.Popen(
            [
                "locust",
                "--no-web",
                "--loglevel", "DEBUG",
                "--only-summary",
                "--host", "http://192.168.33.11",
                "--clients", clients,
                "--hatch-rate", "50",
                "--num-request", num_request,
                "-f", "testsuites/syncgateway/performance/locust/{}".format(scenario)
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        for line in iter(locust_proc.stdout.readline, ''):
            sys.stdout.write(line)
            f.write(line)

    print("*** Tearing down environment ***\n")

    # Parse Values
    with open("WriteThroughPut.txt") as f:
        output = f.read()
        print(output)

    # Clean up environment variables
    del os.environ["LOCUST_NUM_CHANNELS"]
    del os.environ["LOCUST_NUM_CHANNELS_PER_DOC"]

