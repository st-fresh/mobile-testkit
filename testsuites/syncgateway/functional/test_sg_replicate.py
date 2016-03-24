from testkit.cluster import Cluster

def test_sg_replicate_1():
    print "hello!!!!!!"
    cluster = Cluster()
    cluster.reset("resources/sync_gateway_configs/jdskjslkdjflsjdlkfsk")

    sg1 = SyncGateway()  # dict w/ name and ip
    sg1.url = #blah
    sg2 = cluster.sync_gateways[1]
    pass
