import sys
import subprocess
from optparse import OptionParser



if __name__ == "__main__":
    usage = """usage: WriteThoughputRunner.py
    --num-writers=1000
    --num-channels=100
    --total-docs=10000
    --doc-size=4000
    """

    parser = OptionParser(usage=usage)

    parser.add_option("", "--num-writers",
                      action="store", type="int", dest="num_writers",
                      help="number of writers")

    parser.add_option("", "--num-channels",
                      action="store", type="int", dest="num_channels",
                      help="number of channels")

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

    output = subprocess.check_output(
        [
            "locust",
            "--no-web",
            "--only-summary",
            "--clients", clients,
            "--hatch-rate", "50",
            "--num-request", num_request,
            "--logfile", "test.log",
            "-f", "testsuites/syncgateway/performance/locust/WriteThroughputDef.py"
        ],
        stderr=subprocess.STDOUT
    )

    # Write locust results
    with open("WriteThroughPut.txt", "w") as f:
        f.write(output)



