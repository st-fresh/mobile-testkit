from libraries.testkit.cluster import Cluster

import json
import uuid
import os

import statsd
import requests

from locust import HttpLocust, TaskSet, task, events
from keywords.utils import prepare_locust_client

# Start statsd client
stats_client = statsd.StatsClient("localhost", 8125, prefix="locust")

USER_INDEX = 0
USER_SESSION_INFO = json.loads(os.environ["LOCUST_USER_SESSION_INFO"])

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
        prepare_locust_client(self.client)

        global USER_INDEX
        user_id = "user_{}".format(USER_INDEX)
        USER_INDEX += 1

        # Store Cookie auth for user
        requests.utils.add_dict_to_cookiejar(
            self.client.cookies,
            USER_SESSION_INFO[user_id]
        )

    @task
    def add_doc(self):
        data = {
            "channels": "TESTS",
            "sample_prop" : "sample_value"
        }
        resp = self.client.post(":4984/db/", json.dumps(data))
        print(resp.status_code)


class SyncGatewayPusher(HttpLocust):

    weight = 1

    task_set = WriteThroughPut
    min_wait = 100
    max_wait = 1000

