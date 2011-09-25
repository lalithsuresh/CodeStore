import threading
import os
import split
import conf

class Monitoring:

    def __init__ (self, regen):
        self.information_map = {}
        self.timer = ""
        self.has_started = False
        self.reg =regen

    def scan (self, list_of_nodes=conf.DIRS):
        for node in list_of_nodes:
            if (os.path.exists (os.path.abspath(node))):
                self.information_map[os.path.abspath(node)] = "UP"
            else:
                self.information_map[os.path.abspath(node)] = "DOWN"
                print "monitor"
                print self.reg.regen_from
                print self.reg.name
                print node
                split.Regenerate ( int(node), self.reg.regen_from, self.reg.name) 
#        self.stats()
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
