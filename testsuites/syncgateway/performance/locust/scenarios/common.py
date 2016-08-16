import requests
import json
import sys
import random
import string

def set_content_type(client):
    """
    Called in on_start of locust scenarios. Make sure client is prepared to
    communicate with sync_gateway
    """
    client.headers.update({"Content-Type": "application/json"})

def create_session_and_set_cookie(client, user_id):
    data = {
        "name": user_id,
        "ttl": 500
    }
    resp = client.post(":4985/db/_session", data=json.dumps(data))
    session_info = resp.json()

    # Store cookie auth for user
    requests.utils.add_dict_to_cookiejar(
        client.cookies,
        {"SyncGatewaySession": session_info["session_id"]}
    )

def get_channels(client, user_id):
    resp = client.get(":4985/db/_user/{}".format(user_id))
    resp_obj = resp.json()
    return resp_obj["admin_channels"]

def get_doc_body(channels, doc_size_bytes):
    data = {
        "channels": channels,
        "dummy_data": ""
    }
    doc_structure_size = sys.getsizeof(json.dumps(data))

    dummy_data_size = doc_size_bytes - doc_structure_size
    dummy_data = "".join(random.choice(string.ascii_letters) for _ in xrange(dummy_data_size))
    data["dummy_data"] = dummy_data
    doc_body = json.dumps(data)

    doc_body_size = sys.getsizeof(doc_body)
    # Validate POST data == doc size
    assert doc_body_size == doc_size_bytes, "self.doc_body ({}B) != doc_size_bytes ({}B)".format(
        doc_body_size,
        doc_size_bytes
    )

    return doc_body