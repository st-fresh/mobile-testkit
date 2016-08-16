from libraries.testkit.cluster import Cluster

import json
import uuid
import os
import time

import statsd
import requests

from locust import HttpLocust, TaskSet, task, events
from keywords.utils import prepare_locust_client

# Start statsd client
stats_client = statsd.StatsClient("localhost", 8125, prefix="locust")

USER_INDEX = 0
LOCUSTS_HATCHED = False

class WriteThroughPut(TaskSet):

    num_writes_per_user = int(os.environ["LOCUST_NUM_WRITES_PER_USER"])

    def on_start(self):
        """
        Called once when the client is started. Performs the following tasks:
            1. Updates HTTP session to use content type 'application/json'
            2. Create session authentication for the user on sync_gateway
            3. Get the user's channels to use in doc POSTs
            4. Start issueing doc puts
        """
        prepare_locust_client(self.client)

        self.doc_write_count = 0

        global USER_INDEX
        self.user_id = "user_{}".format(USER_INDEX)
        USER_INDEX += 1

        # Create session for user
        data = {
            "name": self.user_id,
            "ttl": 500
        }
        resp = self.client.post(":4985/db/_session", data=json.dumps(data))
        session_info = resp.json()

        # Store cookie auth for user
        requests.utils.add_dict_to_cookiejar(
            self.client.cookies,
            {"SyncGatewaySession": session_info["session_id"]}
        )

        # Get user channels
        resp = self.client.get(":4985/db/_user/{}".format(self.user_id))
        resp_obj = resp.json()
        self.channels = resp_obj["admin_channels"]
        print("READY: user {} -> {}".format(self.user_id, self.channels))

    @task
    def add_doc(self):
        # Wait until all locusts are hatched before issueing doc POSTs
        if LOCUSTS_HATCHED:
            data = {
                "channels": self.channels,
                "sample_prop" : "sample_value"
            }
            self.client.post(":4984/db/", json.dumps(data))
            print("POST doc, user: {} channels: {}".format(self.user_id, self.channels))
            self.doc_write_count += 1

            # If user had written the expected number of docs, terminate
            print(self.doc_write_count)
            print(self.num_writes_per_user)
            if self.doc_write_count == self.num_writes_per_user:
                self.interrupt()


class SyncGatewayPusher(HttpLocust):

    weight = 1

    task_set = WriteThroughPut

    # This needs to be discussed in order to baseline perf runs
    min_wait = 100
    max_wait = 100

def on_hatch_complete(user_count):
    """
    Make sure all locusts have been hatched before issuing doc POSTs to ensure stats
    are reset before tasks are run
    """
    global LOCUSTS_HATCHED
    LOCUSTS_HATCHED = True

events.hatch_complete += on_hatch_complete



