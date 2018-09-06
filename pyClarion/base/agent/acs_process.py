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


# CHANGE HISTORY:
#   11/08/14 - Initial commit to repository (in staging).
#   01/14/15 - (MFL) Extensively rewritten to work with agent_process
#   01/22/15 - (MFL) Finished conn state machine. Now works with agent_processs
#   01/24/15 - Changed code to reflect fact that Chunk no longer has cmd ("c")

#   03/23/15 - (MFL) Had logger display milliseconds.
#   05/30/15 - (MFL) Factored out common agent subprocess code into ClarionSubprocess.py

""" 
This program is the standalone "ACS" subprocess for a PyClarion agent. It is 
usually launched by agent_process.py, although it can be launched by another 
python program or shell script.

All that is passed in is the full path to the agent's "context" file, from 
which this program learns the correct port to connect to.

NO: Also pass the port number -- this needs to be fixed

There are two modes of operation:
    -- testing: fake some traffic between this process and agent_process

    -- production: get set up, then ask for SI chunks and generate action 
        chunks by way of reply, over and over until told to stop.


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
    from asyncio.subprocess import PIPE
except ImportError:
    # asyncio is not installed
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    import asyncio
    from asyncio.subprocess import PIPE

# TODO: Until Clarion is a proper package, add this line of code to the test files:
##sys.path.append("C:\\Users\\Mike\\Documents\\GitHub\\PyClarion")
sys.path.append("/home/ratchet/pyclarion/TRUNK")

import clarion.core.utilities as utilities
from clarion.core.chunk import Chunk
from clarion.core.clarion_subprocess import ClarionSubprocess
from clarion.core.clarion_comm_protocol import ClarionCommProtocol
from clarion.core.agent_context import AgentContext

#from clarion.core.component import ClarionSubprocessClientProtocol, Component

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Signature for Chunk init is: type, sndr, rcvr, cmd, tic, log=None, cname=None
# Asterisk for cname causes chunk's name to be C following by an autoincrement
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# Holds all the action recommendations generated in a single P/A cycle.
action_recs = []

def generate_action_recommendations(tic):
    # list.pop() has LIFO semantics, so the end marker goes in first.
    c = Chunk("ACS-", Chunk.CT_END, "ACS", "AGENT", tic)
    action_recs.append(c) 

    for i in range(2):
        if random.random() < 0.5:
            c = acs.generate_random_action_chunk(tic, Chunk.CT_GS_ACTION)
            action_recs.append(c)
    for i in range(3):
        if random.random() < 0.5:
            c = acs.generate_random_action_chunk(tic, Chunk.CT_WM_ACTION)
            action_recs.append(c)
    for i in range(2, random.randint(3, 5)):
        c = acs.generate_random_action_chunk(tic, Chunk.CT_EXT_ACTION)
        action_recs.append(c)

    for a in action_recs:
        logging.debug("--- action: {}".format(a))


class ACS_Protocol(ClarionCommProtocol):
    """Main processing for ACS traffic between agent_process and this process
    """

    def __init__(self):
        super(ACS_Protocol, self).__init__()    

    def process_message(self, x):
        """All the work of the subprocess is done here. 
    
        NO LONGER: When first connected, a ProjectContext is sent from the agent, 
        and this is used for setting up the entire ACS process. We may reconsider
        this in the future. 
    
        After that, all that comes in are SI chunks (& WM and goal states if using).
        """
    
        # Treat anything that doesn't start with bang as a Chunk
        if x[0] != "!":
            c_in = Chunk.init_from_packet(x)
            logging.debug("Chunk from {}, type {}".format(c_in.s, c_in.t))
    
            # Agent process has sent a Sensory Input
            if c_in.t == Chunk.CT_SI:
                # generate a pile of random action chunks, then send the first one.
                generate_action_recommendations(c_in.k)
                c_out = action_recs.pop()
    
            # Agent process has acknowledged receipt of an action chunk.
            # Send another until you run out.
            elif c_in.t == Chunk.CT_ACK:
                c_out = action_recs.pop()
                if c_out == None:
                    pass    # TODO: Shouldn't happen; add error code
    
            elif c_in.t == Chunk.CT_JOINED:
                # Nothing to do except to make self ready for SIs
                c_out = Chunk("ACS-", Chunk.CT_READY, "ACS", "AGENT", c_in.k)
    
            else:
                c_out = None
    
            if c_out != None:
                msg = json.dumps(c_out.__dict__)
                return msg
            else:
                return None
    
        # Strings that start with bang are immediate commands. There are very few 
        # of these, eventually maybe none.
        
        elif x == "!Welcome":
            c_out = Chunk("ACS-", Chunk.CT_JOIN, "ACS", "AGENT", -1)
            return json.dumps(c_out.__dict__)            
    
        elif x == "!DIE":
            # close the socket
            rport = (self.transport.get_extra_info("peername"))[1]
            print("This guy is checking out: {}".format(rport))
    
            self.transport.close()
            # NO!  self.terminate = True


class ActionCenteredSubsystem(ClarionSubprocess):
    """ActionCenteredSubsystem is the top level of the ACS component of Clarion.
    """

    def __init__(self, aname, ip, pnum, apath):
        super(ActionCenteredSubsystem, self).__init__(aname, ip, pnum, apath)

        # TODO: should be local; save the parts you need
        self.context = AgentContext(aname)
        self.context.load_agent_context(apath)

        print(self.context.sim_host, self.context.sim_port)

    def generate_random_action_chunk(self, tic, typ=Chunk.CT_EXT_ACTION):
        c = Chunk("ACS-", typ, "ACS", "AGENT", tic)
        for dname in self.context.dimensions:
            dim = self.context.dimensions[dname]
            dvp = dim.generate_random_dvpair()
            c.set_dvpair(dvp[0], dvp[1])
        return c

if __name__ == '__main__':
    try:
        # Parse command line, isolate agent name, and start logging
        aname, ac_path, ipaddr, port = utilities.parse_command_line(sys.argv)
        
        print (aname, ac_path, ipaddr, port)
        # Local logging file just for ACS, written fresh each time
        logging.basicConfig(filename=aname+'_acs.log', filemode='w', level=logging.DEBUG,
        format='%(asctime)-15s %(module)s: %(levelname)s: %(message)s') 
        #  Removed this piece of basicConfig: datefmt='%Y-%m-%d %H:%M:%S')
        logging.info("Opened log, at least!")
    except:
        print("Must supply IP addr, portnum, and path to agent context file.")
        quit(1)

    logging.info("Running ACS_emulator for {}".format(aname))

    acs = ActionCenteredSubsystem(aname, ipaddr, port, ac_path)
    acs.connect_to_agent(ACS_Protocol)

    # TODO: Need a way to kill the connection to agent w/o an explicit 
    # command from agent (allows for testing).