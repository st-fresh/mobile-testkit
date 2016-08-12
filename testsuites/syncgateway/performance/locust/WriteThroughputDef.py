from libraries.testkit.cluster import Cluster

import json
import uuid
import os

import statsd
import requests

from locust import HttpLocust, TaskSet, task, events

# Start statsd client
stats_client = statsd.StatsClient("localhost", 8125, prefix="locust")

CHANNEL_INDEX = 0

def get_channel_index():
    return CHANNEL_INDEX

def incr_channel_index():
    global CHANNEL_INDEX
    CHANNEL_INDEX += 1

class WriteThroughPut(TaskSet):


    def on_start(self):
        """
        Called once when the client is started. Performs the following tasks:
            1. Updates HTTP session to use content type 'application/json'
            2. Creates a list of channels per document using a global increment
                to ensure all the channels are used. For example, if the
                LOCUST_NUM_CHANNELS = 4 and LOCUST_NUM_CHANNELS_PER_DOC = 2,
                the channels for Locust 1 will be ["ch_0", "ch_1"] and Locust 2
                will be ["ch_2", "ch_3"]. Since we are using a global counter (CHANNEL_INDEX)
                and a modulus by LOCUST_NUM_CHANNELS, Locust 3 would wrap around and have
                channels ["ch_0", "ch_1"].
            3. Registers itself as a user on sync_gateway
            4. Create session authentication for the user on sync_gateway
        """
        self.client.headers.update({"Content-Type": "application/json"})

        # build channels based on the LOCUST_NUM_CHANNELS and LOCUST_NUM_CHANNELS_PER_DOC
        num_channels = int(os.environ["LOCUST_NUM_CHANNELS"])
        num_channels_per_doc = int(os.environ["LOCUST_NUM_CHANNELS_PER_DOC"])

        print("LOCUST_NUM_CHANNELS: {}".format(num_channels))
        print("LOCUST_NUM_CHANNELS_PER_DOC: {}".format(num_channels_per_doc))

        self.channels = []
        for _ in range(num_channels_per_doc):
            # Take the current channel index counter and mod by the num_channels
            self.channels.append("ch_{}".format(get_channel_index() % num_channels))

            # Increment global counter
            incr_channel_index()

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
