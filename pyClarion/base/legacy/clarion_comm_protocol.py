from __future__ import absolute_import

# Clarion Architecture implementation in Python.
# Copyright (C) 2013-2014 Clarion-Architecture Authors (see AUTHORS.txt)
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


# ClarionSubprocess.py



""" 
This module contains the parent class for any and all asyncio communication
protocols used by any Clarion subprocess. It handles connecting and reconnecting
and supplies a few standard hooks for the specific subclassed protocol to do
its job.
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

class ClarionCommProtocol(asyncio.Protocol):
    """ClarionCommProtocol is the parent of the various socket-based 
    communication protocols used by the various subprocesses. It handles 
    connecting, disconnecting and reconnecting and supplies a few standard 
    hooks for the specific subclassed protocol to do its job.
    """

    def __init__(self):
        super(ClarionCommProtocol, self).__init__()

        self.ccount = 0
        self.retries = 0 

    def set_loop(loop):
        self.loop = loop

    def connection_made(self, transport):
        logging.debug("Entering connection_made()")
        self.running = True
        self.transport = transport

    def data_received(self, data):
        x = data.decode()
        logging.debug('--RECD--: {}'.format(x))

        msg = self.process_message(x)
        
        if msg != None:
            logging.debug("--SENT--: {}".format(msg))
            self.transport.write(msg.encode())

        """
        TODO: This may come back to life at some point.

        CHUNKS = 10
        RETRIES = 50

        FSM_NEW = 0
        FSM_JOINING = 1
        FSM_JOINED = 2
        FSM_SI = 3
        FSM_DYING = 8
        FSM_DEAD = 9

        if x.startswith("CHUNK"):
            self.ccount += 1
            if self.ccount < CHUNKS:
                self.message = "OK_CHUNK"
            else:
                self.message = "DONE"          

        elif x.startswith("Welcome"):
            self.message = "JOIN"

        elif x.startswith("FILES"):
            self.message = "OK_FILES"

        elif x.startswith("DIMS"):
           self.message = "OK_DIMS"

        elif x.startswith("PARAMS"):
           self.message = "OK_PARAMS"
        
        elif x.startswith("CONTEXT"):
           self.message = "OK_PARAMS"

        else:
            self.retries += 1
            if self.retries < RETRIES:       
                self.message = "HUH?"
            else:
                logging.error("...Too many retries on this socket.")
                self.message = "DONE"       
        """


    def connection_lost(self, exc):
        logging.debug('server closed the connection')

        if os.name == 'nt':
            loop = asyncio.ProactorEventLoop()
            asyncio.set_event_loop(loop)
        else:   
            loop = asyncio.get_event_loop()
        loop.stop()

    def process_message(self, msg):
        """This method must be overridden by an inheriting ptotocol class to
        get work done.
        """
        pass
