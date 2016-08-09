from libraries.testkit.cluster import Cluster

import json
import uuid

import requests

from locust import HttpLocust, TaskSet, task

class UserBehavior(TaskSet):

    user_id = 0

    def login(self):

        self.client.headers.update({"Content-Type": "application/json"})

        user_id = "user_{}".format(uuid.uuid4())
        data = {
            "name": user_id,
            "password": "password",
            "admin_channels": ["abc", "nbc"]
        }

        # Add user
        self.client.put(":4985/db/_user/{}".format(user_id), data=json.dumps(data))

        data = {
            "name": user_id,
            "ttl": 500
        }
        resp = self.client.post(":4985/db/_session", data=json.dumps(data))
        session_info = resp.json()

        requests.utils.add_dict_to_cookiejar(
            self.client.cookies,
            {"SyncGatewaySession": session_info["session_id"]}
        )

    def on_start(self):
        self.login()

    # @task
    # def stop(self):
    #     self.interrupt()

    @task(10)
    def add_doc(self):

        data = {
            "prop1": "ehh"
        }

        self.client.post(":4984/db/", json.dumps(data))

    @task(1)
    def admin_root(self):
        self.client.get(":4984/")



class WebsiteUser(HttpLocust):

    host = "http://192.168.33.13"

    task_set = UserBehavior
    min_wait = 5000
    max_wait = 9000