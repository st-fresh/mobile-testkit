import requests
import tarfile
import os
import shutil

from lib.admin import Admin
from lib.syncgateway import SyncGateway


class SyncGatewayUtils:

    def __init__(self):
        self.file_name = "couchbase-sync-gateway-enterprise_1.2.0-83_x86_64.tar.gz"
        self.sync_gateway = SyncGateway({"ip": "localhost", "name": "local"})
        self.admin = Admin(self.sync_gateway)

    def install_local_sync_gateway(self, platform, version):
        print("Installing {} sync_gateway on {}".format(version, platform))

        url = "http://latestbuilds.hq.couchbase.com/couchbase-sync-gateway/1.2.0/1.2.0-83/couchbase-sync-gateway-enterprise_1.2.0-83_x86_64.tar.gz"
        os.chdir("resources/sync_gateway")

        r = requests.get(url)

        with open(self.file_name, "wb") as f:
            f.write(r.content)

        with tarfile.open(self.file_name) as tar_f:
            tar_f.extractall()

        os.chdir("../../")

    def uninstall_local_sync_gateway(self, platform):
        os.chdir("resources/sync_gateway")
        os.remove(self.file_name)
        shutil.rmtree("couchbase-sync-gateway")
        os.chdir("../../")

    def get_sync_gateway_document_count(self, db):
        docs = self.admin.get_all_docs(db)
        return docs["total_rows"]
