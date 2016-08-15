import subprocess
import sys

from keywords.constants import RESULTS_DIR


def run_locust_scenario(name, target, clients, num_request):
    results_path = "{}/perf/syncgateway/{}.txt".format(RESULTS_DIR, name)
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
                "-f", "testsuites/syncgateway/performance/locust/scenarios/{}.py".format(name)
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

        for line in iter(locust_proc.stdout.readline, ''):
            sys.stdout.write(line)
            f.write(line)