from testkit.listener import Listener
from testkit.listener import iOSListener
from testkit.listener import AndroidListener


class ClientKeywords:

    def launch_listener(self, platform):

        if platform == "ios":
            self.listener = iOSListener()
        elif platform == "android":
            self.listener = AndroidListener()

        self.listener.install()
        self.listener.launch()



