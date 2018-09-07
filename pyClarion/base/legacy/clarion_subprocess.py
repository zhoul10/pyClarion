from __future__ import absolute_import

# Clarion Architecture implementation in Python.
# Copyright (C) 2013-2015 Clarion-Architecture Authors (see AUTHORS.txt)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>. 
#
# CHANGE HISTORY:
#   05/30/15 - (MFL) All Clarion agent subprocesses now inherit from this.
#   08/06/15 - (MFL) Removed everything having to do with pipes

# ClarionSubprocess.py



""" 
This module contains the parent class for any and all subprocesses used in a 
Clarion agent. It performs all the common tasks, including processing of the 
AgentContext file and connecting to the other parts of the agent.
"""

__author__ = 'Mike'

import os
import sys
import time
import random
import socket
import json
import logging

try:
    import asyncio
except ImportError:
    # asyncio is not installed
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    import asyncio

import clarion.core.utilities as utilities
from clarion.core.agent_context import AgentContext

class ClarionSubprocess(asyncio.SubprocessProtocol):
    """ClarionSubprocess is the parent of every one of an agent's subprocesses.
    """

    def __init__(self, aname, ip, pnum, apath):
        super(ClarionSubprocess, self).__init__()
        
        self.agent_name = aname   
        self.agent_host = ip
        self.agent_port = pnum
        self.ac_path = apath
        self.tic = -1

        # TODO: should be local; save the parts you need
        self.context = AgentContext(aname)
        self.context.load_agent_context(apath)


    def get_core_context():
        """Loads the context and sets up Dimensions and Parameters, which are
        needed by all subprocesses. The context itself in then returned, and 
        should be used to retrieve everything else the subprocess is interested
        in. After that, the context object can be safely GC'd.
        """
        # TODO: Finish this!
        pass
    
    # TODO: The following is an attempt at refactoring. Must finish it.
        
    def connect_to_process(self, protocol, ipa, pn):
        """Attempts to connect to some other running process via its passed-in
        ipaddr and port number.  Must also be passed in the correct protocol to 
        use for the subprocess making the connection (i.e. this side). 
        """

        try:
            logging.debug("--------------------------------------------")
            logging.debug("Getting loop")
            if os.name == 'nt':
                logging.debug("running on Windows, I see...")
                self.loop = asyncio.ProactorEventLoop()
                asyncio.set_event_loop(self.loop)
            else:   
                self.loop = asyncio.get_event_loop()
        
        except Exception as e:
            logging.debug("Could not get a loop.")

        # Playing with socket connections
        try:     
            logging.info("Attempting to connect to{}:{} using context file{}".format(
            ipa, pn, self.ac_path))

            logging.debug("Trying to create connection")
            #self.coro = self.loop.create_connection(ActionCenteredSubsystem, '127.0.0.1', 8888)
            #logging.debug("Got the coroutine")
            #self.trans, self.prot = self.loop.create_connection(asyncio.SubprocessProtocol, '127.0.0.1', 8888)
            
            try:
                self.coro = self.loop.create_connection(protocol, ipa, pn) 
            except Exception as ee:
                logging.debug("Failed at the create_connection coroutine")

            logging.debug("Back from create_connection")

            self.loop.run_until_complete(self.coro)
            logging.debug("Back from the Future")
            self.loop.run_forever()
            self.loop.close()
        except Exception as e:
            logging.debug("Could not get a connection.")


    def connect_to_agent(self, protocol):
        """Attempts to connect to the agent's boss process via the previously 
        obtained ipaddr and port number for the agent.  Must be passed in the 
        correct protocol to use for the subprocess making the connection (i.e.,
        this side).
        """

        try:
            logging.debug("--------------------------------------------")
            logging.debug("Getting loop")
            if os.name == 'nt':
                logging.debug("running on Windows, I see...")
                self.loop = asyncio.ProactorEventLoop()
                asyncio.set_event_loop(self.loop)
            else:   
                self.loop = asyncio.get_event_loop()
        
        except Exception as e:
            logging.debug("Could not get a loop.")

        # Playing with socket connections
        try:     
            logging.info("Attempting to connect to{}:{} using context file{}".format(
            self.agent_host, self.agent_port, self.ac_path))

            logging.debug("Trying to create connection")
            #self.coro = self.loop.create_connection(ActionCenteredSubsystem, '127.0.0.1', 8888)
            #logging.debug("Got the coroutine")
            #self.trans, self.prot = self.loop.create_connection(asyncio.SubprocessProtocol, '127.0.0.1', 8888)
            
            try:
                self.coro = self.loop.create_connection(protocol, 
                    self.agent_host, self.agent_port)    # ipaddress.ip_address()
            except Exception as ee:
                logging.debug("Failed at the create_connection coroutine")

            logging.debug("Back from create_connection")

            self.loop.run_until_complete(self.coro)
            logging.debug("Back from the Future")
            self.loop.run_forever()
            self.loop.close()
        except Exception as e:
            logging.debug("Could not get a connection.")


