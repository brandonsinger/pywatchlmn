# Copyright 2009 Brandon Singer (brandonsinger.com)

"""
Example usage:
from monitor import Monitor
from monitor import MonitorStatLoad

mon = Monitor()
mon.add_server(server_name, host, user, password)
mon.add_stat(MonitorStatLoad(), server_name)
mon.run()
"""

import time
import paramiko


class MonitorStat(object):
    """Monitor Stat classes need to look something like this. But they don't need to subclass it."""
    def __init__(self):
        self.server = None
        self.results = {}
    def execute(self):
        return "some command"
    def process(self, out, err):
        self.results["why"] = 2
        return self.results
    def __str__(self):
        return "description"

class MonitorStatLoad(object):
    def __init__(self):
        self.server = None
        self.results = {}
    def execute(self):
        return "cat /proc/loadavg"
    def process(self, out, err):
        t = out.split()[:3]
        self.results["1min"], self.results["5min"], self.results["15min"] = t
        return self.results
    def __str__(self):
        return "Load: 1min 5min 15min"

class MonitorStatMemory(object):
    def __init__(self):
        self.server = None
        self.results = {}
    def execute(self):
        return "cat /proc/meminfo"
    def process(self, out, err):
        for line in out.splitlines():
            splitted = line.split()
            self.results[splitted[0]] = splitted[1]
        return self.results
    def __str__(self):
        return "description"

class MonitorHTTPDCount(object):
    def __init__(self):
        self.server = None
        self.results = {}
    def execute(self):
        return "ps ax | grep httpd | wc -l"
    def process(self, out, err):
        self.results = out.strip()
        return self.results
    def __str__(self):
        return "description"


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

    

