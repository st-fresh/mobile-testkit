import base64
import json

import requests

from couchbase.admin import Admin

from provision.ansible_runner import run_ansible_playbook

class Server:

    def __init__(self, target):
        self.ip = target["ip"]
        self.url = "http://{}:8091".format(target["ip"])
        self.hostname = target["name"]

        auth = base64.b64encode("{0}:{1}".format("Administrator", "password").encode())
        auth = auth.decode("UTF-8")
        self._headers = {'Content-Type': 'application/json', "Authorization": "Basic {}".format(auth)}

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

        # # Create buckets
        # extra_vars = {"bucket_names": names}
        # run_ansible_playbook(
        #     "tasks/create-server-buckets.yml",
        #     extra_vars=json.dumps(extra_vars),
        # )

        # Get ram
        resp = requests.get("{0}/pools/default".format(self.url), headers=self._headers)
        resp.raise_for_status()
        resp_json = resp.json()

        free_memory = resp_json["nodes"][0]["systemStats"]["mem_free"]
        free_memory_mb = free_memory / 1000000
        print(">>> Memory free (MB): {}".format(free_memory_mb))
        memory_per_bucket = (free_memory / 1000000) / len(names)
        print(">>> Memory per bucket (MB): {}".format(memory_per_bucket))

        print("http://{}".format(self.ip))

        cb_admin = Admin(
            username="Administrator",
            password="password",
            host="http://{}".format(self.ip),
            port=8091
        )

        for name in names:
            cb_admin.bucket_create(name=name, ram_quota=memory_per_bucket, replicas=1)


    def __repr__(self):
        return "Server: {}:{}\n".format(self.hostname, self.ip)


