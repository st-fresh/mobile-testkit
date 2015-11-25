import base64
import json
import time

import requests

from provision.ansible_runner import run_ansible_playbook

class Server:

    def __init__(self, target):
        self.ip = target["ip"]
        self.url = "http://{}:8091".format(target["ip"])
        self.hostname = target["name"]

        auth = base64.b64encode("{0}:{1}".format("Administrator", "password").encode())
        auth = auth.decode("UTF-8")
        self._headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "Basic {}".format(auth),
            "Accept": "*/*"
        }

    def delete_buckets(self):

        resp = requests.get("{}/pools/default/buckets".format(self.url), headers=self._headers)
        resp.raise_for_status()
        obj = json.loads(resp.text)

        existing_bucket_names = []
        for entry in obj:
            existing_bucket_names.append(entry["name"])

        print(">>> Existing buckets: {}".format(existing_bucket_names))
        print(">>> Deleting buckets: {}".format(existing_bucket_names))

        # Delete existing buckets
        for bucket_name in existing_bucket_names:
            resp = requests.delete("{0}/pools/default/buckets/{1}".format(self.url, bucket_name), headers=self._headers)
            resp.raise_for_status()

    def create_buckets(self, names):

        # Get available RAM on the server
        resp = requests.get("{0}/pools/default".format(self.url), headers=self._headers)
        resp.raise_for_status()
        resp_json = resp.json()

        free_memory = resp_json["nodes"][0]["systemStats"]["mem_free"]
        free_memory_mb = free_memory / 1000000
        print(">>> Memory free (MB): {}".format(free_memory_mb))
        memory_per_bucket = (free_memory / 1000000) / len(names)
        print(">>> Memory per bucket (MB): {}".format(memory_per_bucket))

        # Create buckets on the server
        proxyPort = 12000
        for name in names:
            params = {
                "name": name,
                "ramQuotaMB": memory_per_bucket,
                "authType": "none",
                "proxyPort": proxyPort,
            }

            r = requests.post("{0}/pools/default/buckets".format(self.url), headers=self._headers, data=params)
            r.raise_for_status()

            proxyPort += 1

        # Hack - need to test this
        # Sleep during bucket creation
        time.sleep(4)

    def __repr__(self):
        return "Server: {}:{}\n".format(self.hostname, self.ip)


