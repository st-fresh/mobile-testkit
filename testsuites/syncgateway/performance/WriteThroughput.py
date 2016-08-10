from libraries.testkit.cluster import Cluster

import json
import uuid

import requests

from locust import HttpLocust, TaskSet, task, events

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


stats = {
    "add_doc_time_total" : 0,
    "add_doc_num": 0,
    "add_docs_average_time": 0
}

def on_request_success(request_type, name, response_time, response_length):
    """
    Event handler that get triggered on every successful request
    """
    if name == "/db/":
        stats["add_doc_time_total"] += response_time
        stats["add_doc_num"] += 1
        stats["add_docs_average_time"] = stats["add_doc_time_total"] / stats["add_doc_num"]

    print(stats)

# Hook up the event listeners
events.request_success += on_request_success
