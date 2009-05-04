
"""
Example usage:
from monitor import Monitor
from monitor import MonitorStatLoad

mon = Monitor(5)
mon.add_server(server_name, host, user, password)
mon.add_stat(MonitorStatLoad(), server_name)
mon.run()
"""

import time
import paramiko

class MonitorStatLoad(object):
    def __init__(self):
        self.server = None
        self.last_results = None
    
    def execute(self):
        return "cat /proc/loadavg"

    def process(self, out, err):
        d = out.split()
        self.last_results = (d[0], d[1], d[2])
        return self.last_results

    def __str__(self):
        return "Load: 1min 5min 15min"


class Monitor(object):
    def __init__(self, delay=15):
        self.delay = delay
        self.servers = {}
        self.stats = []

    def add_server(self, name, host, username, password):
        #TODO: Add error handling
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        ssh.connect(host, username=username, password=password)
        self.servers[name] = ssh

    def add_stat(self, stat, server):
        #TODO: Add error handling
        stat.server = self.servers[server]
        self.stats.append(stat)
        

    def run(self):
        print "Starting run loop"
        while True:
            for stat in self.stats:
                stdin, stdout, stderr = stat.server.exec_command(stat.execute())
                stdin.close()
                out = stdout.read()
                err = stderr.read()
                result = stat.process(out, err)
                print result
                
            #print "Sleeping for %s" % (self.delay)
            #time.sleep(self.delay)
            raise SystemExit()

    

