import os
import sys

from optparse import OptionParser
from ansible_runner import AnsibleRunner


def install_dependencies():

    ansible_runner = AnsibleRunner()

    # OS-level modifications
    status = ansible_runner.run_ansible_playbook("os-level-modifications.yml", stop_on_fail=False)
    assert (status == 0)

    # Install dependencies
    status = ansible_runner.run_ansible_playbook("install-common-tools.yml", stop_on_fail=False)
    assert (status == 0)


if __name__ == "__main__":

    usage = "usage: python libraries/provision/install_dependencies.py"
    parser = OptionParser(usage=usage)

    arg_parameters = sys.argv[1:]

    (opts, args) = parser.parse_args(arg_parameters)

    try:
        cluster_config = os.environ["CLUSTER_CONFIG"]
    except KeyError as ke:
        print ("Make sure CLUSTER_CONFIG is defined and pointing to the configuration you would like to provision")
        raise KeyError("CLUSTER_CONFIG not defined. Unable to provision cluster.")

    install_dependencies()
