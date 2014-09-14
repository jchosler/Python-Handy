"""This class manages child processes.

When starting up a new child process, use appendProcess() to add it to
the list of child processes.
"""

import multiprocessing
import logging
from time import time

class ProcessManager:
    def __init__(self):
        self.log = logging.getLogger('logname') # Use a logger previously setup
        self.processes = []
    
    def appendProcess(self, process, max_runtime):
        """Add new process to list of processes"""
        process.time_expire = time() + max_runtime
        self.processes.append(process)
        
    def getProcesses(self):
        """Return list of all processes."""
        return self.processes
    
    def cleanupProcesses(self):
        """Loop through all processes and update status.
        
        Terminate processes that are running past process.time_expire.  Terminate
        does not remove process from the current list. It will be removed in the
        next iteration of cleanupProcesses().
        """
        new_process_list = []
        for process in self.processes:
            if process.is_alive() == True:
                self.log.debug("Process %s is alive: %s" % (process.name, True))
                new_process_list.append(process)
            elif process.is_alive() == False:
                self.log.debug("Process %s is alive: %s" % (process.name, False))
            elif time() > process.time_expire:
                process.terminate()
                self.log.warning("Terminating long running worker")
        self.processes = new_process_list
    
    def getProcessCount(self):
        """Return the number of processes after first running cleanup"""
        self.cleanupProcesses()
        return len(self.processes)
    
    def close(self, timeout=120):
        """Gracefully wait for processes to finish.
         
        Child processes must ignore signals for CTRL C!
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        Parent process should use signal handler and then call process_manager.close()
        """
        for process in self.processes:
            # self.log.debug("Pre join %s is alive? %s" % (process.name, process.is_alive()))
            process.join(timeout) # Ignore if process doesn't respond after timeout
            # self.log.debug("Post join %s is alive? %s" % (process.name, process.is_alive()))
        self.cleanupProcesses()
