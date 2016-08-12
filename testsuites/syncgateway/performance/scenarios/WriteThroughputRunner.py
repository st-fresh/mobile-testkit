import sys
import subprocess
import os

from optparse import OptionParser

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
                      action="store", type="string", dest="num_channels",
                      help="number of channels that docs ")

    parser.add_option("", "--num-channels-per-doc",
                      action="store", type="string", dest="num_channels_per_doc",
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

    clients = str(opts.num_writers)

    # POST _user + POST + _session = opts.num_writers * 2 requests
    # POST docs = total_docs requests
    num_requests = (opts.num_writers * 2) + opts.total_docs
    num_request = str(num_requests)

    print("*** LOCUST ***")
    print("clients: {}".format(clients))
    print("num_request: {}\n".format(num_request))

    print("*** Starting statsd ***")
    print("Starting Server on :8125 ...")

    # Set needed environment variables
    os.environ["LOCUST_NUM_CHANNELS"] = opts.num_channels
    os.environ["LOCUST_NUM_CHANNELS_PER_DOC"] = opts.num_channels_per_doc

    output = subprocess.check_output(
        [
            "locust",
            "--no-web",
            "--clients", clients,
            "--hatch-rate", "50",
            "--num-request", num_request,
            "-f", "testsuites/syncgateway/performance/locust/WriteThroughputDef.py"
        ]
        #stderr=subprocess.STDOUT
    )

    # Write locust results
    with open("WriteThroughPut.txt", "w") as f:
        f.write(output)

    # Clean up environment variables
    del os.environ["LOCUST_NUM_CHANNELS"]
    del os.environ["LOCUST_NUM_CHANNELS_PER_DOC"]

