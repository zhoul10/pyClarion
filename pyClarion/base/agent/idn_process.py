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
#   01/24/15 - (MFL) New, derived from acs_process.py

#   03/23/15 - (MFL) Had logger display milliseconds.


""" 
This program is the standalone "IDN" subprocess for a PyClarion agent. It is 
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
    c = Chunk("IDN-", Chunk.CT_END, "IDN", "AGENT", tic)
    action_recs.append(c) 

    for i in range(2):
        if random.random() < 0.5:
            c = idn.generate_random_action_chunk(tic, Chunk.CT_GS_ACTION)
            action_recs.append(c)
    for i in range(3):
        if random.random() < 0.5:
            c = idn.generate_random_action_chunk(tic, Chunk.CT_WM_ACTION)
            action_recs.append(c)
    for i in range(2, random.randint(3, 5)):
        c = idn.generate_random_action_chunk(tic, Chunk.CT_EXT_ACTION)
        action_recs.append(c)

    for a in action_recs:
        logging.debug("--- action: {}".format(a))




class IDN_Protocol(ClarionCommProtocol):
    """Main processing for IDN traffic between agent_process and this process
    """

    def __init__(self):
        super(IDN_Protocol, self).__init__()   
        
    def process_message(self, x):
        """All the work of the subprocess is done here. 
    
        NO LONGER: When first connected, a ProjectContext is sent from the agent, 
        and this is used for setting up the entire IDN process. We may reconsider
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
                c_out = Chunk("IDN-", Chunk.CT_READY, "IDN", "AGENT", c_in.k)
    
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
            c_out = Chunk("IDN-", Chunk.CT_JOIN, "IDN", "AGENT", -1)
            return json.dumps(c_out.__dict__)            
    
        elif x == "!DIE":
            # close the socket
            rport = (self.transport.get_extra_info("peername"))[1]
            print("This guy is checking out: {}".format(rport))
    
            self.transport.close()
            # NO!  self.terminate = True


class ImplicitDecisionNetworkSubsystem(ClarionSubprocess):
    """ImplicitDecisionNetwork is the bottom level of the ACS component of Clarion.
    """

    def __init__(self, aname, ip, pnum, apath):
        super(ImplicitDecisionNetworkSubsystem, self).__init__(aname, ip, pnum, apath)

        # TODO: should be local; save the parts you need
        self.context = AgentContext(aname)
        self.context.load_agent_context(apath)

        print(self.context.sim_host, self.context.sim_port)          


    def generate_random_action_chunk(self, tic, typ=Chunk.CT_EXT_ACTION):
        c = Chunk("IDN-", typ, "IDN", "AGENT", tic)
        for dname in self.context.dimensions:
            dim = self.context.dimensions[dname]
            dvp = dim.generate_random_dvpair()
            c.set_dvpair(dvp[0], dvp[1])
        return c


# temp class to hold the networks info
class NetworkFromJson(object):
    def __init__(self, name, h_modules, i_modules, o_modules, type):
        self.name = name
        self.hidden_modules = h_modules
        self.input_modules = i_modules
        self.output_modules = o_modules
        self.type = type
        self.nodes = []


    # something to extract the nodes in the nodes in the layers in the modules

# mostly in testing phase
# move this function to pybrain api once working
def test_json_parse(jpath):
    # open json
    try:
        json_data = open(jpath)
        context = json.load(json_data)
    except Exception as e:
        logging.error(e)
        return False

    try:
        if("idn_networks" in context):
            idn_nets = [] # list of idn_networks
            for indx,el in ( enumerate(context["idn_networks"])):
                # prints the network name
                # logging.info(el)
                # prints the network type
                # logging.info(context["idn_networks"][el]["type"])
                n = NetworkFromJson(el,
                                    context["idn_networks"][el]["hidden_modules"],
                                    context["idn_networks"][el]["input_modules"],
                                    context["idn_networks"][el]["output_modules"],
                                    context["idn_networks"][el]["type"])
                idn_nets.append(n)

        logging.info(len(idn_nets))
        logging.info(idn_nets[0].name)
        # input_modules[0][0] where first 0 is input_layer and second is input and the last is nodes
        logging.info(idn_nets[0].input_modules)
    except Exception as e:
        logging.error(e)
        return False

if __name__ == '__main__':
    try:
        # Parse command line, isolate agent name, and start logging
        aname, ac_path, ipaddr, port = utilities.parse_command_line(sys.argv)
        
        print (aname, ac_path, ipaddr, port)
        # Local logging file just for IDN, written fresh each time
        logging.basicConfig(filename=aname+'_idn.log', filemode='w', level=logging.DEBUG,
        format='%(asctime)-15s %(module)s: %(levelname)s: %(message)s') 
        #  Removed this piece of basicConfig: datefmt='%Y-%m-%d %H:%M:%S')
        logging.info("Opened log, at least!")
    except:
        print("Must supply IP addr, portnum, and path to agent context file.")
        quit(1)

    logging.info("Running IDN_emulator for {}".format(aname))

    #TEST PARSING OF JSON
    logging.info("path of json {}".format(ac_path))
    test_json_parse(ac_path)

    idn = ImplicitDecisionNetworkSubsystem(aname, ipaddr, port, ac_path)        
    idn.connect_to_agent(IDN_Protocol)

    # TODO: Need a way to kill the connection to agent w/o an explicit
    # command from agent (allows for testing).

