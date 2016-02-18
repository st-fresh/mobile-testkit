import time
from lib.admin import Admin
from lib.verify import verify_changes
import pytest
import concurrent
import concurrent.futures
import requests

import lib.settings
import logging

from fixtures import cluster
from fixtures import run_opts

log = logging.getLogger(lib.settings.LOGGER)


@pytest.mark.parametrize("conf, num_docs, user_channels, filter, limit", [
        ("sync_gateway_channel_cache_cc.json", 5000, ["ABC"], True, 50),
        ("sync_gateway_channel_cache_cc.json", 1000, ["ABC"], True, 50),
        ("sync_gateway_channel_cache_cc.json", 5000, ["ABC"], False, 50),
    ],
    ids=["CC-1", "CC-2", "CC-3"]
)
def test_overloaded_channel_cache(cluster, run_opts, conf, num_docs, user_channels, filter, limit):

    log.info("Using conf: {}".format(conf))
    log.info("Using num_docs: {}".format(num_docs))
    log.info("Using user_channels: {}".format(user_channels))
    log.info("Using filter: {}".format(filter))
    log.info("Using limit: {}".format(limit))

    mode = cluster.reset(conf, run_opts)

    target_sg = cluster.sync_gateways[0]

    admin = Admin(target_sg, run_opts.id)

    users = admin.register_bulk_users(target_sg, "db", "user", 1000, "password", user_channels)
    assert len(users) == 1000

    doc_pusher = admin.register_user(target_sg, "db", "abc_doc_pusher", "password", ["ABC"])
    doc_pusher.add_docs(num_docs, bulk=True)

    doc_pusher_nbc = admin.register_user(target_sg, "db", "nbc_doc_pusher", "password", ["NBC"])
    doc_pusher_nbc.add_docs(num_docs, bulk=True)

    # Give a few seconds to let changes register
    time.sleep(2)

    start = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:

        changes_requests = []
        errors = []

        for user in users:
            if filter and limit is not None:
                changes_requests.append(executor.submit(user.get_changes, since=0, limit=limit, filter="sync_gateway/bychannel", channels=["ABC"]))
            elif filter and limit is None:
                changes_requests.append(executor.submit(user.get_changes, filter="sync_gateway/bychannel", channels=["ABC"]))
            elif not filter and limit is not None:
                changes_requests.append(executor.submit(user.get_changes, limit=limit))
            elif not filter and limit is None:
                changes_requests.append(executor.submit(user.get_changes))

        for future in concurrent.futures.as_completed(changes_requests):
            changes = future.result()
            if limit is not None:
                assert len(changes["results"]) == 50
            else:
                assert len(changes["results"]) == 5001

        # changes feed should all be successful
        log.info(len(errors))
        assert len(errors) == 0

        if limit is not None:
            # HACK: Should be less than a minute unless blocking on view calls
            end = time.time()
            time_for_users_to_get_all_changes = end - start
            log.info("Time for users to get all changes: {}".format(time_for_users_to_get_all_changes))
            assert time_for_users_to_get_all_changes < 120

        # Sanity check that a subset of users have _changes feed intact
        for i in range(10):
            verify_changes(users[i], expected_num_docs=num_docs, expected_num_revisions=0, expected_docs=doc_pusher.cache)

        # Get sync_gateway expvars
        resp = requests.get(url="http://{}:4985/_expvar".format(target_sg.ip))
        resp.raise_for_status()
        resp_obj = resp.json()

        assert("view_queries" not in resp_obj["syncGateway_changeCache"])

    # Verify all sync_gateways are running
    errors = cluster.verify_alive(mode)
    assert(len(errors) == 0)
