import time

import pytest
import concurrent.futures

from lib.admin import Admin
from lib.verify import verify_changes

from fixtures import cluster


@pytest.mark.sanity
def test_non_winning_revision(cluster):

    cluster.reset(config="sync_gateway_default_functional_tests.json")

    admin = Admin(cluster.sync_gateways[2])

    seth = admin.register_user(target=cluster.sync_gateways[2], db="db", name="seth", password="password", channels=["ABC"])
    docs = seth.add_docs(1)
    seth.update_docs(10)



