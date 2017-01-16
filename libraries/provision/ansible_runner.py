from ansible_python_runner import Runner
from ansible import constants
import logging

from keywords import exceptions

PLAYBOOKS_HOME = "libraries/provision/ansible/playbooks"


class AnsibleRunner:

    def __init__(self, config):
        self.provisiong_config = config

    def run_ansible_playbook(self, script_name, extra_vars=None, subset=constants.DEFAULT_SUBSET):

        if extra_vars is None:
            extra_vars = {}

        inventory_filename = self.provisiong_config

        playbook_filename = "{}/{}".format(PLAYBOOKS_HOME, script_name)

        runner = Runner(
            inventory_filename=inventory_filename,
            playbook=playbook_filename,
            extra_vars=extra_vars,
            verbosity=0,  # change this to a higher number for -vvv debugging (try 10),
            subset=subset
        )

        stats = runner.run()
        logging.info(stats)

        return len(stats.failures) + len(stats.dark)

    def must_run_playbook(self, script_name, extra_vars=None):
        """ Run an ansible playbook and will raise an exception if any errors occur."""

        if extra_vars is None:
            extra_vars = {}

        num_errors = self.run_ansible_playbook(script_name=script_name, extra_vars=extra_vars)
        if num_errors != 0:
            raise exceptions.ProvisioningError("Ansible runner failed while executing: {}".format(script_name))
