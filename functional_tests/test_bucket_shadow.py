import time

import pytest


from lib.admin import Admin
from lib.verify import verify_changes

from fixtures import cluster

## 1. Do cluster reset with config that specifies shadow buckets
## 2. Presumably add some docs via SG Rest API?
## 3. (check order) Shut down sync gateway
## 4. Delete document from "source bucket" directly in couchbase server
## 5. Restart sync gw
## 6. Do some verification

"""
2) Create a new doc via REST API, this will create a doc in shadow and will set the "upstream-rev" property on the SG doc metadata

3) Take shadow offline (I deleted the CBS bucket I don't know if a restore will have the same effect)

4) While shadow is offline, update the doc enough times to exceed the revs_limit setting. This will updated the doc but will not update the "upstream_rev" property.

4a) Delete doc, this will generate the following log message in the SG log

Shadow: Pushing "doc1", rev "9-ebbae742633c5059d80a062db256e1cb" [deletion]
2016-02-25T19:28:47.851Z WARNING: Error pushing rev of "doc1" to external bucket: MCResponse status=0x20, opcode=SASL_AUTH, opaque=0, msg: Auth failure -- db.(*Shadower).PushRevision() at shadower.go:164

5) Bring shadow back online

6) Edit document in shadow
"""

def test_bucket_shadow(cluster):

    """
    Reproduce CBSE-2399
    Details in https://github.com/couchbaselabs/sync-gateway-testcluster/issues/291
    """
    
    source_bucket_name = "source-bucket"
    config_path = "sync_gateway_bucketshadow_cc.json"
    
    mode = cluster.reset(config_path=config_path)
    #mode = "channel_cache"
    
    config = cluster.sync_gateway_config
    
    if len(config.get_bucket_name_set()) != 2:
        raise Exception("Expected to find two buckets, only found {}".format(len(config.bucket_name_set())))
    
    # Verify all sync_gateways are running
    errors = cluster.verify_alive(mode)
    assert(len(errors) == 0)

    admin = Admin(cluster.sync_gateways[0])

    alice = admin.register_user(
        target=cluster.sync_gateways[0],
        db="db",
        name="alice",
        password="password",
        channels=["ABC", "NBC", "CBS"],
    )

    # Add doc to sync gateway
    doc_id = alice.add_doc()
    
    # Get a connection to the bucket
    bucket = cluster.servers[0].get_bucket_connection(source_bucket_name)

    # Wait til the docs appears in the source bucket
    doc  = None
    maxTries = 5
    i = 0
    while True:
        i += 1
        print("trying to get doc: {}".format(doc_id))
        doc = bucket.get(doc_id, quiet=True)
        print("doc.success: {}".format(doc.success))
        if doc.success:
            break
        else:
            if i > maxTries:
                # too many tries, give up
                raise Exception("Doc {} never made it to source bucket.  Aborting".format(doc_id))
            time.sleep(i)
            continue
        
    print("Doc {} appeared in source bucket".format(doc))
    
    # Take source bucket offline by deleting it
    cluster.servers[0].delete_bucket(source_bucket_name)

    # 4) While shadow is offline, update the doc enough times to exceed the revs_limit setting. This will updated the doc but will not update the "upstream_rev" property.
    alice.update_doc(doc_id, num_revision=10)

    # 4a) Delete doc, this will generate the following log message in the SG log
    alice.delete_doc(doc_id)
    
    # 5) Bring shadow back online

    # 6) Edit document in shadow
    
    #doc = {}
    #doc_id = "{}".format(time.time())
    #doc["foo"] = "bar"
    #bucket.add(doc_id, doc)

    # Delete doc from source bucket
    #bucket.remove(doc_id)

    # Restart Sync gateway
    #cluster.sync_gateways[0].restart(config_path)

    # Verify all Sync Gateways are running
    errors = cluster.verify_alive(mode)
    assert(len(errors) == 0)

    

