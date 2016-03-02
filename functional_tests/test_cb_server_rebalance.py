import time
import pytest
from lib.user import User
import concurrent.futures
from lib.admin import Admin
from fixtures import cluster
import pytest
from lib.parallelize import *
import logging
log = logging.getLogger(settings.LOGGER)



@pytest.mark.parametrize(
        "conf", [
            ("sync_gateway_default_functional_tests_cc.json")
        ],
        ids=["CC-1"]
)
def test_cb_server_remove_node_rebalance(cluster, conf):
    log.info("Starting test...")
    log.info("conf: {}".format(conf))

    start = time.time()

    mode = cluster.reset(config=conf)

    log.info("server nodes:{}".format(cluster.servers))
    log.info("server node1:{}".format(cluster.servers[0].ip))
    nodes = ["172.23.105.163"]
    cluster.rebalance_in(nodes)

