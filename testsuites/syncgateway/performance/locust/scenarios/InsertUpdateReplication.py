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

USER_INDEX = 0
LOCUSTS_HATCHED = False

class DocPusher(TaskSet):

    num_writes_per_user = int(os.environ["LOCUST_NUM_WRITES_PER_USER"])

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

        global USER_INDEX
        self.user_id = "user_{}".format(USER_INDEX)
        USER_INDEX += 1

        # Create session for user
        create_session_and_set_cookie(self.client, self.user_id)

        # Get channels
        self.channels = get_channels(self.client, self.user_id)

        # Calculte doc size and create doc body
        doc_size_bytes = int(os.environ["LOCUST_DOC_SIZE"])
        self.doc_body = get_doc_body(self.channels, doc_size_bytes)


    @task
    def add_doc(self):
        # Make sure metric are reset before performing the scenario
        if LOCUSTS_HATCHED:
            # Generate a doc that is doc_size_bytes + the channels prop size
            self.client.post(":4984/db/", self.doc_body)
            print("POST doc, user: {} channels: {}".format(self.user_id, self.channels))
            self.doc_write_count += 1

            # If user had written the expected number of docs, terminate
            print(self.doc_write_count)
            print(self.num_writes_per_user)
            if self.doc_write_count == self.num_writes_per_user:
                self.interrupt()

class DocPuller(TaskSet):

    num_writes_per_user = int(os.environ["LOCUST_NUM_WRITES_PER_USER"])

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

        global USER_INDEX
        self.user_id = "user_{}".format(USER_INDEX)
        USER_INDEX += 1

        # Create session for user
        create_session_and_set_cookie(self.client, self.user_id)

        # Get channels
        self.channels = get_channels(self.client, self.user_id)

        # Calculte doc size and create doc body
        doc_size_bytes = int(os.environ["LOCUST_DOC_SIZE"])
        self.doc_body = get_doc_body(self.channels, doc_size_bytes)


    @task
    def add_doc(self):
        # Make sure metric are reset before performing the scenario
        if LOCUSTS_HATCHED:
            # Generate a doc that is doc_size_bytes + the channels prop size
            self.client.post(":4984/db/", self.doc_body)
            print("POST doc, user: {} channels: {}".format(self.user_id, self.channels))
            self.doc_write_count += 1

            # If user had written the expected number of docs, terminate
            print(self.doc_write_count)
            print(self.num_writes_per_user)
            if self.doc_write_count == self.num_writes_per_user:
                self.interrupt()



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



