import threading
import os

import conf

class Monitoring:

    def __init__ (self):
        self.information_map = {}
        self.timer = ""
        self.has_started = False

    def scan (self, list_of_nodes=conf.DIRS):
        for node in list_of_nodes:
            if (os.path.exists (os.path.abspath(node))):
                self.information_map[os.path.abspath(node)] = "UP"
            else:
                self.information_map[os.path.abspath(node)] = "DOWN"
        self.stats()
        self.timer = threading.Timer (conf.MONITORING_INTERVAL, self.scan)
        self.timer.start()

    def start (self):
        if (self.has_started == False):
            self.has_started = True
            self.timer = threading.Timer (conf.MONITORING_INTERVAL, self.scan)
            self.timer.start()
        else:
            print "Monitoring already enabled"

    def stop (self):
        self.timer.cancel()

    def stats (self):
        print "----Node----Status----"
        for each in self.information_map:
            print each + str(": ") + self.information_map[each]
        print "----------------------"
