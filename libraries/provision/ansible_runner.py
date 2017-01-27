from ansible_python_runner import Runner
from ansible import constants
import logging
import os
from keywords.utils import log_info

PLAYBOOKS_HOME = "libraries/provision/ansible/playbooks"


class AnsibleRunner:

    def __init__(self, config):
        self.provisiong_config = config

    def run_ansible_playbook(self, script_name, extra_vars={}, subset=constants.DEFAULT_SUBSET):

        inventory_filename = self.provisiong_config

        # Check if there is a windows inventory file
        #if os.path.exists("libraries/provision/ansible/playbooks/inventory/windows"):
        #    inventory_filename = "libraries/provision/ansible/playbooks/inventory/windows"


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
