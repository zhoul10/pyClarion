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
#   11/03/14    Renamed all the data elements, to reduce packet size.
#   01/23/15 - (MFL) Added ActionChunk class

__author__ = 'Mike'

from datetime import datetime
import json

from chunk import Chunk



class ActionChunk(Chunk): 
    """ An ActionChunk is a Chunk that carries additional information, not in 
    the DV Pair dictionary, needed for action selection. These are: activation
    (a), base level activation (b), utility (u).
    """

    def __repr__(self):
        return "<Chunk(t=%d, n='%s', s='%s', r='%s', l='%s', k=%d, v='%s', a=%.7f, bla=%.7f, u=%.7f, d=%s)>" % (
            self.t, self.n, self.s, self.r, self.l, self.k, self.v, self.a, self.bla, self.u, self.d)

    def __init__(self, prefix, type, sndr, rcvr, tic, verb, activ, bla, utility, log=None, cname=None):
        """Creates a chunk instance and fills it in. Note that the data
        elements are all given single letter names (contrary to PEP 8). This 
        is to minimize packet lengths as chunks get sent over sockets.
        """
        super(ActionChunk, self).__init__(prefix, type, sndr, rcvr, tic, log, cname)
        self.v = verb
        self.a = activ
        self.bla = bla
        self.u = utility

if __name__ == '__main__':
    
    action = ActionChunk("ACS-", Chunk.CT_EXT_ACTION, "ACS", "AGENT", 12345, "Play Louder", 0.5, 0.6, 0.7)
    print(action)


