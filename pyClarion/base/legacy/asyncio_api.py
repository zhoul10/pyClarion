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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

#=============================================================================
# This module supplies essential wrapper routines for asyncio for use by the 
# various processes and subprocesses in the Clarion system.
#=============================================================================

__author__ = 'Mike'

import os
import sys
import time
import logging

try:
    import asyncio
    from asyncio import subprocess
    from asyncio.subprocess import PIPE
except ImportError:
    # asyncio is not installed
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    import asyncio
    from asyncio import subprocess
    from asyncio.subprocess import PIPE

import clarion.core.utilities as utilities

logger = logging.getLogger(__name__)

MAX_RETRIES = 20

def get_asyncio_loop():
    """Get the main loop (a/k/a "reactor" in Twisted), taking into account
    whether we're running on Windows or not.)
    """
    loop = None
    error = None

    try:
        logger.info ("Getting loop...")       
        if os.name == 'nt':
            logger.info ("running on Windows, I see...")
            loop = asyncio.ProactorEventLoop()
            asyncio.set_event_loop(loop)
            error = None
        else:   
            loop = asyncio.get_event_loop()
    except:
        error = "Unable to get a working asyncio loop."
        logger.error(error)

    return loop, error

#-----------------------------------------------------------------------------
#  These functions relate to setting up the socket listener.
#-----------------------------------------------------------------------------

def prepare_socket_listener(loop, protocol):
    """Sets up the socket listener by grabbing an unused non-volatile 
    port number using a utility call.

    It only creates the socket server, it does not actually begin Listening
    on it until the loop itself does run_until_complete() on it.
    """
    # TODO: FAILURE CASES HAVE NOT BEEN TESTED!
    # TODO: Should have a retry count and a better way of 

    # TODO: Should generalize beyond localhost
    listener_host = '127.0.0.1'
    listener_port = 0
    server = None
    error = None
    retries = MAX_RETRIES

    done = False

    while not done:
        retries -= 1
        if retries <= 0: 
            return None, "Out of retries"

        # Get a legal unassigned non-volatile port for socket listener.
        listener_port = utilities.get_safe_portnum()
        #self.listener_port = 50011  # TODO: adopt get_safe_portnum whenever
        logger.info("Trying portnum %s %d", listener_host, listener_port)

        try:
           coro = loop.create_server(
                protocol, listener_host, listener_port)
        except:
            error = "Problem with create_server coroutine."
            logger.error(error)
            return None, error
        
        try:
            server = loop.run_until_complete(coro)
            logger.info("Port number %d was successful.", listener_port)
            done = True
        except Exception as e:      # TODO: be more specific here
            logger.warning("Port number %d didn't work.", listener_port)
    
    #logger.info('Listener socket serving on {}'.format(
    #    server.sockets[0].getsockname()))

    return server, error

def prepare_socket_listener_the_hard_way(loop, protocol):
    """Set up the socket listener the hard way, by using the port_for
    library. This takes a remarkably long time to do, and we will be 
    needing a lot of port numbers.

    It only creates the socket server, it does not actually begin Listening
    on it until the server loop is started. 
    """
    # TODO: Should generalize beyond localhost
    listener_host = '127.0.0.1'
    listener_port = 0
    server = None
    error = None

    try:
        # Get a legal unassigned port number for the socket listener.
        logger.info("Trying for a portnum")
        # TODO: Provide a fallback if port_for times out
        listener_port = port_for.select_random()
        logger.info("portnum=%d", listener_port)
    except:
        error = "Problem getting a portnum."
        logger.error(error)
        
    logger.info("Past portnum")
    
    try:
        coro = loop.create_server(Protocol, listener_host, listener_port)
    except Exception as e:
        error = "Could not create simulation server."
        logger.error(error)

    server = loop.run_until_complete(coro)

    logger.info('Listener socket serving on {}'.format(
        server.sockets[0].getsockname()))

    return server, error
