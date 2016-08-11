from libraries.testkit.cluster import Cluster

import json
import uuid

import statsd
import requests

from locust import HttpLocust, TaskSet, task, events

# Start statsd client
stats_client = statsd.StatsClient("localhost", 8125)

class WriteThroughPut(TaskSet):

    def on_start(self):
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

    @task
    def add_doc(self):
        data = {
            "prop1": "ehh"
        }
        resp = self.client.post(":4984/db/", json.dumps(data))



    # @task(10)
    # def update_doc(self):
    #     pass

# 10000

class SyncGatewayPusher(HttpLocust):

    weight = 1

    host = "http://192.168.33.11"

    task_set = WriteThroughPut
    min_wait = 100
    max_wait = 1000

# class SyncGatewayPullers(HttpLocust):
#
#     # Open a changes feed and listen for docs, when one is recieve
#     #   Calculate delta of now - creation and push this to time seriesdb
#
#     weight = 1
#
#     host = "http://192.168.33.13"
#
#     task_set = PullTask
#     min_wait = 1000
#     max_wait = 5000


stats = {
    "add_doc_time_total" : 0,
    "add_doc_num": 0,
    "add_docs_average_time": 0,
    "counter": 0
}

def on_request_success(request_type, name, response_time, response_length):
    """
    Event handler that get triggered on every successful request

    Process RTT
    """

    stats["counter"] += 1
    # Write time to statsd
    #stats_client.timing("response", response_time)
    stats_client.incr('pyinc', count=stats["counter"])  # Increment the 'foo' counter
    stats_client.timing('pyresponse', response_time)  # Increment the 'foo' counter

    # if name == "/db/":
    #     stats["add_doc_time_total"] += response_time
    #     stats["add_doc_num"] += 1
    #     stats["add_docs_average_time"] = stats["add_doc_time_total"] / stats["add_doc_num"]
    #
    # print(stats)

# Hook up the event listeners
events.request_success += on_request_success
