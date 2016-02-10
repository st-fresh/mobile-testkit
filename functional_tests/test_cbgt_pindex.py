import time

import pytest


from lib.admin import Admin
from lib.verify import verify_changes

from fixtures import cluster
from fixtures import run_opts


def test_pindex_distribution(cluster, run_opts):

    # the test itself doesn't have to do anything beyond calling cluster.reset() with the
    # right configuration, since the validation of the cbgt pindex distribution is in the
    # cluster.reset() method itself.
    
    mode = cluster.reset("performance/sync_gateway_default_performance.json", run_opts)

    # Verify all sync_gateways are running
    errors = cluster.verify_alive(mode)
    assert(len(errors) == 0)




