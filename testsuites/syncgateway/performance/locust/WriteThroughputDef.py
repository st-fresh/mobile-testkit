from libraries.testkit.cluster import Cluster

import json
import uuid
import os

import statsd
import requests

from locust import HttpLocust, TaskSet, task, events

# Start statsd client
stats_client = statsd.StatsClient("localhost", 8125, prefix="locust")


class WriteThroughPut(TaskSet):

    channel_index = 0

    def on_start(self):
        self.client.headers.update({"Content-Type": "application/json"})

        # build channels based on the LOCUST_NUM_CHANNELS and LOCUST_NUM_CHANNELS_PER_DOC
        num_channels = int(os.environ["LOCUST_NUM_CHANNELS"])
        num_channels_per_doc = int(os.environ["LOCUST_NUM_CHANNELS_PER_DOC"])

        print("LOCUST_NUM_CHANNELS: {}".format(num_channels))
        print("LOCUST_NUM_CHANNELS_PER_DOC: {}".format(num_channels_per_doc))

        self.channels = []
        for _ in range(num_channels_per_doc):
            # Take the current channel_index and mod by the num_channels
            self.channels.append("ch_{}".format(self.channel_index % num_channels))

            # HACK?: Update static class variable, so that the next locust with
            # use this when seeding channels
            WriteThroughPut.channel_index += 1

        user_id = "user_{}".format(uuid.uuid4())
        print("{} -> channels: {}".format(user_id, self.channels))

        data = {
            "name": user_id,
            "password": "password",
            "admin_channels": self.channels
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
            "channels": self.channels,
            "sample_prop" : "sample_value"
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
}

def on_request_success(request_type, name, response_time, response_length):
    """
    Event handler that get triggered on every successful request

    Process RTT
    """
    # Write response_time to statsd
    if name.startswith("/db/_user/"):
        stats_client.timing('user_add_response_time', response_time)
    elif name.startswith("/db/"):
        stats_client.timing('doc_add_response_time', response_time)

# Hook up the event listeners
events.request_success += on_request_success
