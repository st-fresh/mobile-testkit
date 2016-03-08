
from testkit.cluster import Cluster

class TestCbgtPIndex:

    def test_pindex_distribution(self, conf):

        # the test itself doesn't have to do anything beyond calling cluster.reset() with the
        # right configuration, since the validation of the cbgt pindex distribution is in the
        # cluster.reset() method itself.
        cluster = Cluster()
        mode = cluster.reset(config_path=conf)

        # Verify all sync_gateways are running
        errors = cluster.verify_alive(mode)
        assert(len(errors) == 0)
