from libraries.testkit.cluster import Cluster

import json
import uuid
import os
import time
import random
import string
import sys

import statsd
import requests

from locust import HttpLocust, TaskSet, task, events

from common import set_content_type
from common import create_session_and_set_cookie
from common import get_channels
from common import get_doc_body

# Start statsd client
stats_client = statsd.StatsClient("localhost", 8125, prefix="locust")

PUSHER_USER_INDEX = 0
PULLER_USER_INDEX = 0

PUSHER_LOCUSTS_HATCHED = 0
ALL_PUSHERS_HATCHED = False
PUSHED_DOCS = {}

PULLER_LOCUSTS_HATCHED = 0
ALL_PULLERS_HATCHED = False
PULLED_DOCS = {}

class DocPusher(TaskSet):

    num_pushers = int(os.environ["LOCUST_NUM_PUSHERS"])
    num_writes_per_user = int(os.environ["LOCUST_NUM_WRITES_PER_USER"])
    user_prefix = os.environ["LOCUST_PUSHER_USER_PREFIX"]

    def on_start(self):
        """
        Called once when the client is started. Performs the following tasks:
            1. Updates HTTP session to use content type 'application/json'
            2. Create session authentication for the user on sync_gateway
            3. Get the user's channels to use in doc POSTs
            4. Calculate / Verify doc body == 'doc_size'
            4. Start issueing doc puts
        """
        set_content_type(self.client)

        self.doc_write_count = 0

        global PUSHER_USER_INDEX
        self.user_id = "{}_{}".format(self.user_prefix, PUSHER_USER_INDEX)
        PUSHER_USER_INDEX += 1

        global PUSHED_DOCS
        PUSHED_DOCS[self.user_id] = []

        # Create session for user
        create_session_and_set_cookie(self.client, self.user_id)

        # Get channels
        self.channels = get_channels(self.client, self.user_id)

        # Calculte doc size and create doc body
        doc_size_bytes = int(os.environ["LOCUST_DOC_SIZE"])
        self.doc_body = get_doc_body(self.channels, doc_size_bytes)

        global PUSHER_LOCUSTS_HATCHED
        PUSHER_LOCUSTS_HATCHED += 1

        if PUSHER_LOCUSTS_HATCHED == self.num_pushers:
            print("All pushers hatched ...")
            global ALL_PUSHERS_HATCHED
            ALL_PUSHERS_HATCHED = True

    @task
    def add_doc(self):
        # Make sure metric are reset before performing the scenario
        if ALL_PUSHERS_HATCHED:
            # Generate a doc that is doc_size_bytes + the channels prop size

            doc = json.loads(self.doc_body)
            doc["doc_added_at"] = time.time()

            resp = self.client.post(":4984/db/", json.dumps(doc))
            resp_obj = resp.json()

            global PUSHED_DOCS
            PUSHED_DOCS[self.user_id].append(resp_obj)

            print("add_doc user: {} channels: {} id: {}".format(self.user_id, self.channels, resp_obj["id"]))
            self.doc_write_count += 1

            # If user had written the expected number of docs, terminate
            if self.doc_write_count == self.num_writes_per_user:
                global PUSHED_DOCS
                print("PUSHED_DOCS: {}".format(PUSHED_DOCS))
                self.interrupt()

class DocPuller(TaskSet):

    num_pullers = int(os.environ["LOCUST_NUM_PULLERS"])
    user_prefix = os.environ["LOCUST_PULLER_USER_PREFIX"]

    def on_start(self):
        """
        Called once when the client is started. Performs the following tasks:
            1. Updates HTTP session to use content type 'application/json'
            2. Create session authentication for the user on sync_gateway
            3. Get the user's channels to use in doc POSTs
            4. Calculate / Verify doc body == 'doc_size'
            4. Start issueing doc puts
        """
        set_content_type(self.client)

        global PULLER_USER_INDEX
        self.user_id = "{}_{}".format(self.user_prefix, PULLER_USER_INDEX)
        PULLER_USER_INDEX += 1

        # Create session for user
        create_session_and_set_cookie(self.client, self.user_id)

        # Get channels
        self.channels = get_channels(self.client, self.user_id)

        self.last_seq = 0
        global PULLED_DOCS
        PULLED_DOCS[self.user_id] = []

        global PULLER_LOCUSTS_HATCHED
        PULLER_LOCUSTS_HATCHED += 1

        if PULLER_LOCUSTS_HATCHED == self.num_pullers:
            print("All pullers hatched ...")
            global ALL_PULLERS_HATCHED
            ALL_PULLERS_HATCHED = True

    @task
    def listen_to_changes(self):
        # Make sure metric are reset before performing the scenario
        if ALL_PULLERS_HATCHED:
            # Generate a doc that is doc_size_bytes + the channels prop size
            print("self.last_seq: {}".format(self.last_seq))
            resp = self.client.get(":4984/db/_changes?feed=longpoll&since={}".format(self.last_seq))
            print(resp.text)
            resp_obj = resp.json()
            print("listen_to_changes: user: {} channels: {} changes: {}".format(self.user_id, self.channels, resp_obj))

            for doc in resp_obj["results"]:
                if not doc["id"].startswith("_user"):
                    PULLED_DOCS[self.user_id].append({
                        "id": doc["id"],
                        "rev": doc["changes"][0]["rev"]
                    })
                    self.client.get(":4984/db/{}".format(doc["id"]))

            # Update the last_seq
            self.last_seq = resp_obj["last_seq"]

            #self.interrupt()



class SyncGatewayPusher(HttpLocust):

    weight = 1

    task_set = DocPusher

    # This needs to be discussed in order to baseline perf runs
    min_wait = 100
    max_wait = 100

class SyncGatewayPuller(HttpLocust):

    weight = 1

    task_set = DocPuller

    # This needs to be discussed in order to baseline perf runs
    min_wait = 2000
    max_wait = 2000

def on_hatch_complete(user_count):
    """
    Make sure all locusts have been hatched before issuing doc POSTs to ensure stats
    are reset before tasks are run
    """
    global LOCUSTS_HATCHED
    LOCUSTS_HATCHED = True

events.hatch_complete += on_hatch_complete



