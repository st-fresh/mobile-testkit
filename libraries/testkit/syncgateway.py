import os
import requests
import json

from requests.packages.urllib3.util import Retry
from requests.adapters import HTTPAdapter

import testkit.settings
from testkit.debug import *

import logging
log = logging.getLogger(testkit.settings.LOGGER)

from provision.ansible_runner import AnsibleRunner

class SyncGateway:

    def __init__(self, target):
        self.ansible_runner = AnsibleRunner()
        self.ip = target["ip"]
        self.url = "http://{}:4984".format(target["ip"])
        self.hostname = target["name"]
        self._headers = {'Content-Type': 'application/json'}

    def info(self):
        r = requests.get(self.url)
        r.raise_for_status()
        return r.text

    def stop(self):
        status = self.ansible_runner.run_targeted_ansible_playbook(
            "stop-sync-gateway.yml",
            target_name=self.hostname,
            stop_on_fail=False,
        )
        return status

    def start(self, config):

        conf_path = os.path.abspath(config)

        log.info(">>> Starting sync_gateway with configuration: {}".format(conf_path))

        status = self.ansible_runner.run_targeted_ansible_playbook(
            "start-sync-gateway.yml",
            extra_vars="sync_gateway_config_filepath={0}".format(conf_path),
            target_name=self.hostname,
            stop_on_fail=False
        )
        return status

    def restart(self, config):
        conf_path = os.path.abspath(config)

        log.info(">>> Restarting sync_gateway with configuration: {}".format(conf_path))

        status = self.ansible_runner.run_targeted_ansible_playbook(
            "reset-sync-gateway.yml",
            extra_vars="sync_gateway_config_filepath={0}".format(conf_path),
            target_name=self.hostname,
            stop_on_fail=False
        )
        return status


    def verify_launched(self):
        r = requests.get(self.url)
        log.info("GET {} ".format(r.url))
        log.info("{}".format(r.text))
        r.raise_for_status()


    def create_db(self, name):
        r = requests.put("{}/{}".format(self.url, name))
        log.info("PUT {} ".format(r.url))
        r.raise_for_status()
        return r.json()


    def delete_db(self, name):
        r = requests.delete("{}/{}".format(self.url, name))
        log_request(r)
        log_response(r)
        r.raise_for_status()
        return r.json()


    def get_dbs(self):
        r = requests.get("{}/_all_dbs".format(self.url))
        log.info("GET {}".format(r.url))
        r.raise_for_status()
        return r.json()


    def reset(self):
        dbs = self.get_dbs()
        for db in dbs:
            self.delete_db(db)


    def start_push_replication(self, target, db):
        data = {
            "source": "{}".format(db),
            "target": "{}/{}".format(target, db),
            "continuous": True
        }
        r = requests.post("{}/_replicate".format(self.url), data=json.dumps(data))
        log_request(r)
        log_response(r)
        r.raise_for_status()


    def stop_push_replication(self, target, db):
        data = {
            "source": "{}".format(db),
            "target": "{}/{}".format(target, db),
            "cancel": True
        }
        r = requests.post("{}/_replicate".format(self.url), data=json.dumps(data))
        log_request(r)
        log_response(r)
        r.raise_for_status()


    def start_pull_replication(self, target, db):
        data = {
            "source": "{}/{}".format(target, db),
            "target": "{}".format(db),
            "continuous": True
        }
        r = requests.post("{}/_replicate".format(self.url), data=json.dumps(data))
        log_request(r)
        log_response(r)
        r.raise_for_status()


    def stop_pull_replication(self, target, db):
        data = {
            "source": "{}/{}".format(target, db),
            "target": "{}".format(db),
            "cancel": True
        }
        r = requests.post("{}/_replicate".format(self.url), data=json.dumps(data))
        log_request(r)
        log_response(r)
        r.raise_for_status()


    def get_num_docs(self, db):
        r = requests.get("{}/{}/_all_docs".format(self.url, db))
        log_request(r)
        log_response(r)
        r.raise_for_status()
        resp_data = r.json()
        return resp_data["total_rows"]

    # PUT /{db}/{doc}
    # PUT /{db}/{local-doc-id}
    # NOTE: Copied and pasted from user.py
    def add_doc(self, db, doc_id=None, content=None, channels=None, retries=False):

        doc_body = dict()
        doc_body["updates"] = 0

        if channels is not None:
            doc_body["channels"] = channels

        if content is not None:
            doc_body["content"] = content

        body = json.dumps(doc_body)

        if doc_id is None:
            # Use a POST and let sync_gateway generate an id
            resp = requests.post("{0}/{1}/".format(self.url, db), headers=self._headers, data=body,
                                 timeout=settings.HTTP_REQ_TIMEOUT)
            log.debug("{0} POST {1}".format(db, resp.url))
        else:
            # If the doc id is specified, use PUT with doc_id in url
            doc_url = self.url + "/" + db + "/" + doc_id

            if retries:
                session = requests.Session()
                adapter = requests.adapters.HTTPAdapter(
                    max_retries=Retry(total=settings.MAX_HTTP_RETRIES, backoff_factor=settings.BACKOFF_FACTOR,
                                      status_forcelist=settings.ERROR_CODE_LIST))
                session.mount("http://", adapter)
                resp = session.put(doc_url, headers=self._headers, data=body, timeout=settings.HTTP_REQ_TIMEOUT)
            else:
                resp = requests.put(doc_url, headers=self._headers, data=body, timeout=settings.HTTP_REQ_TIMEOUT)

            log.debug("{0} PUT {1}".format(db, resp.url))

        resp.raise_for_status()
        resp_json = resp.json()

        # 200 as result of POST to /{db}/, 201 is result of PUT to /{db}/{doc}
        if resp.status_code == 200 or resp.status_code == 201:
            if doc_id is None:
                # Get id generated from sync_gateway in response
                doc_id = resp_json["id"]

        return doc_id

    def __repr__(self):
        return "SyncGateway: {}:{}\n".format(self.hostname, self.ip)
