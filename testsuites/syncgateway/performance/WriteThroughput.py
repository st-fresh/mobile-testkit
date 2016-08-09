from locust import HttpLocust, TaskSet, task

import json

from locust import HttpLocust, TaskSet

class UserBehavior(TaskSet):

    user_id = 0

    def login(self):

        self.client.headers.update({"Content-Type": "application/json"})

        data = {
            "name": "seth_{}".format(self.user_id),
            "password": "password",
            "admin_channels": ["abc, nbc"]
        }
        self.client.post(":4985/db/_user", data)

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

    host = "http://192.168.33.11"

    task_set = UserBehavior
    min_wait = 5000
    max_wait = 9000