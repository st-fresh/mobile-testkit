from testkit.cluster import Cluster
from testkit.syncgateway import SyncGateway
from testkit.admin import Admin
from testkit.user import User
from testkit.android import parallel_install
import sys

import time

# Attempt to spinup liteserv .. ran into port forwarding issues and emulator crashing OSX issues
def test_sg_replicate_2():

    # deploy liteserv

    should_reinstall = True
    apk_path = "deps/couchbase-lite-android-liteserv/couchbase-lite-android-liteserv/build/outputs/apk/couchbase-lite-android-liteserv-debug.apk"
    activity = "com.couchbase.liteservandroid/com.couchbase.liteservandroid.MainActivity"
    source_db = "source_db"
    target_db = "target_db"

    device_defs = [
        {"target": "emulator-5554", "local_port": 10000, "apk_path": apk_path, "activity": activity},
        {"target": "emulator-5556", "local_port": 11000, "apk_path": apk_path, "activity": activity},
    ]

    # if should_reinstall is false, it will wipe app cache and relaunch
    listeners = parallel_install(device_defs, should_reinstall)

    time.sleep(2)

    emu_1 = listeners["emulator-5554"]
    emu_2 = listeners["emulator-5556"]

    all_emus = [emu_1, emu_2]
    for emu in all_emus:
        emu.verify_launched()


def test_sg_replicate_1():

    # don't need this, spinning up couchdb by hand
    # cluster = Cluster()
    # cluster.reset("resources/sync_gateway_configs/jdskjslkdjflsjdlkfsk")

    # To run this test, you must manually spin up CouchDB under docker
    # with docker toolbox via:
    #  docker run -p 5984:5984 -d couchdb
    #  docker run -p 5986:5984 -d couchdb

    db = "db"

    target1 = {}
    target1["ip"] = "192.168.99.100"  # the hostname that appears in Docker Quickstart Terminal
    target1["name"] = "sg1"

    sg1 = SyncGateway(target1)  # dict w/ name and ip
    sg1.url = "http://{}:5984".format(target1["ip"])

    target2 = {}
    target2["ip"] = "192.168.99.100"  # the hostname that appears in Docker Quickstart Terminal
    target2["name"] = "sg2"
    sg2 = SyncGateway(target2)  # dict w/ name and ip
    sg2.url = "http://{}:5986".format(target2["ip"])

    admin = Admin(sg1)
    admin.admin_url = sg1.url

    sg1_user = User(
        target=sg1,
        db=db,
        name=None,
        password=None,
        channels=[],
    )

    sg2_user = User(
        target=sg2,
        db=db,
        name=None,
        password=None,
        channels=[],
    )

    # Delete dbs if they already exist
    sg1_dbs = sg1.get_dbs()
    sg2_dbs = sg2.get_dbs()
    if db in sg1_dbs:
        sg1.delete_db(db)
    if db in sg2_dbs:
        sg2.delete_db(db)

    # Add docs to the source db
    sg1.create_db(db)
    doc_id = sg1_user.add_doc()
    print("Doc: {}".format(doc_id))

    # Create the target db
    sg2.create_db(db)

    # Start a push replication
    sg1.start_push_replication(sg2.url, db)

    # Verify that the doc made it to the target
    sg2_doc = sg2_user.get_doc(doc_id)
    print("Sg2_doc: {}".format(sg2_doc))

    assert sg2_doc is not None
    assert sg2_doc["_id"] == doc_id


pass
