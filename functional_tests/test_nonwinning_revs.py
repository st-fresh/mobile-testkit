import time

import pytest
import concurrent.futures

from lib.admin import Admin
from lib.verify import verify_changes

from fixtures import cluster


@pytest.mark.sanity
def test_non_winning_revision(cluster):

    cluster.reset(config="sync_gateway_default_functional_tests.json")

    number_of_docs = 1
    number_of_updates = 2

    admin = Admin(cluster.sync_gateways[2])

    seth = admin.register_user(target=cluster.sync_gateways[2], db="db", name="seth", password="password", channels=["ABC"])
    docs = seth.add_docs(number_of_docs)
    print docs

    updated_docs = seth.update_docs(number_of_updates)
    print updated_docs

    outdated_rev = updated_docs[docs[0]][0]
    print ("outdated_rev: {}".format(outdated_rev))

    updated_doc = seth.update_doc(docs[0], num_revision=5, rev_id=outdated_rev)

    time.sleep(1)

    print(seth.cache)
    verify_changes(seth, expected_num_docs=1, expected_num_revisions=2, expected_docs=seth.cache)



