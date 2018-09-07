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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Changes:
#   10/23/14    Added 'log' to the set of meta data items
#   11/02/14    Changed get_cid. Now returns only the autoincrement integer
#   11/02/14    Added init_from_packet()
#   11/02/14    Baked chunk type equates into Chunk class definition
#   11/02/14    Added wrapper methods for getting and setting dvpairs
#   11/02/14    Added methods to encode and decode chunks to/from JSON
#   11/03/14    Set up a better enum scheme for chunk types
#   11/03/14    Removed the "factory" material, as it is not needed.
#   11/03/14    Renamed all the data elements, to reduce packet size
#   01/24/15 - (MFL) Removed cmd (var c); all done with type (var t) instead
#   01/24/15 - (MFL) Added prefix var so chunk ID naming reflects originator

__author__ = 'Mike'

from datetime import datetime
import json

#import clarion.core.dimension

class ChunkShell(object):
    """This is an empty instance of an object with a __dict__.  It later gets  
    turned into a Chunk from incoming socket data.
    """
    pass

# TODO: Do we even need this?
class ChunkType:
	"""Enum for identifying types of Chunks."""
	Nothing, EXT_action, WM_action, GS_action = range(4)

class DataDict(dict):
    """A subclass of dict that supplies useful fail-silent behavior
    for missing keys.
    """

    def __init__(self):
        super(DataDict, self).__init__()

    def __missing__(self, key):
        # TODO: Logging?
        return None


class Chunk(object):
    """This is an exact copy of a dictionary used as a Chunk to 
        keep the language consistent with the literature.

    10/23/14: Added 'log' to meta data
    """
    # These are the possible chunk types:
    CT_META = 0         # Internal use only
    CT_SI = 1           # Sensory input
    CT_WM = 2           # Contents of working memory
    CT_GOAL = 3         # Current Goal State
    CT_INPUT = 4        # Aggregation of SI, WM and GOAL
    CT_EXT_ACTION = 5   # External Action (operates on world)
    CT_WM_ACTION = 6    # Action that affects Working Memory
    CT_GS_ACTION = 7    # Action that affects Goal State
    CT_CONDITION = 11   # Condition chunk (for rules)
    #                     reserved
    
    # These verbs are used between the Simulation and any Agent
    CT_AGENT_JOIN = 61    # Simulation invites Agent to join after it connects
    CT_AGENT_JOINED = 62  # The Simulation responds to a successful join
    CT_AGENT_READY = 63   # Agent indicates it is ready to receive chunks
    CT_AGENT_RUN_SS = 64  # Simulation tells agent to do one P/A cycle
    CT_AGENT_RUN = 65     # Simulation tells agent to run N rounds
    CT_AGENT_DIE = 66     # Subprocess commands an Agent to terminate
    CT_AGENT_DYING = 67   # Agent ACKs the DIE command and starts shutting down
    CT_AGENT_DEAD = 68    # Agent is about to close conn and terminate
    CT_AGENT_END = 69     # Signals end of a series of chunks
       
    CT_AGENT_GET_SI = 71  # Agent requests an SI chunk
    CT_AGENT_SI = 72      # The SI chunk requested by the Agent
    CT_AGENT_ACK = 73     # Received SI chunk was good
    CT_AGENT_NAK = 74     # Received SI chunk was not good
    CT_AGENT_RESULT = 75  # Agent returns results from most recent cycle(s)
    
    # These verbs are used between an Agent and its subprocesses
    CT_JOIN = 91        # Initial type for a just-joining subprocess
    CT_JOINED = 92      # agent_process response to a successful join
    CT_READY = 93       # Subprocess indicates it is ready to receive chunks
    CT_ACK = 94         # received chunk was good
    CT_NAK = 95         # received chunk was not good
    CT_DIE = 96         # Agent commands a subprocess to terminate
    CT_DYING = 97       # Subprocess ACKs the DIE command and shuts down
    CT_DEAD = 98        # Subprocess is about to close conn and terminate
    CT_END = 999        # Signals end of a series of chunks
    
    # NOTE: Py 3.4 now has enums but since this code also has to work on 
    # Py 2.7 we can't use that yet.

    autoval = 0

    def __repr__(self):
        return "<Chunk(t=%d, n='%s', s='%s', r='%s', l='%s', k=%d, d=%s)>" % (
            self.t, self.n, self.s, self.r, self.l, self.k, self.d)

    def __init__(self, prefix, type, sndr, rcvr, tic, log=None, cname=None):
        """Creates a chunk instance and fills it in. Note that the data
        elements are all given single letter names (contrary to PEP 8). This 
        is to minimize packet lengths as chunks get sent over sockets.
        """
        if cname=="*" or cname==None:
            self.n = prefix + str(Chunk.get_cid())
        else:
            self.n = cname
            
        self.t = type # one of ChunkType
        # TODO: Do we need "mode"?
        self.s = sndr
        self.r = rcvr
        self.l = log
        self.k = tic        
        #self.timestamp = datetime.now()    # TODO: get format working  
        self.d = dict()                     # TODO: DataDict()?

    # Here is how to put something in...
    # self.data[dim_name] = value

    # Here is how to get something out...
    # myval = self.data[dim_name]

    def set_dvpair(self, dname, val):
        self.d[dname] = val

    def get_dvpair(self, dname):
        if dim_name in d.keys():
            return self.d[dim_name]
        else:
            return None

    def set_receiver(self, rcvr):
        self.r = rcvr

    @staticmethod
    def get_cid():
        """Returns the autoincrement ID from the Chunk class (then
        autoincrements it).
        """
        Chunk.autoval += 1
        return Chunk.autoval 



#------------------------------------------------------------------------------
#  Encoding and decoding this class for socket transmission
#------------------------------------------------------------------------------

    @staticmethod
    def init_from_packet(x):
        """Converts a packet received over a socket  (after .decode() was run
        on it) into a viable chunk.
        """
        c = ChunkShell()
        # TODO: This is really, really ugly
        #setattr(c, '__dict__', json.loads(x))
        try:
            c.__dict__ = json.loads(x)      # Yes, this works
            return c
        except:
            return None

    def convert_to_packet(self):
        """Turns the Chunk into a JSON'd string, ready to send. (It will still 
        need to have .encode() run on it in the Protocol.)
        """
        try:
            return json.dumps(self.__dict__, separators=(',', ':'))
        except:
            return "CRAP".encode()





if __name__ == '__main__':
    pass
