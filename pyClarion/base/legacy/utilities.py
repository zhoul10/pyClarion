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
__author__ = 'Mike'

import sys
import os.path
import random

# These are "non-ephemeral" port numbers not otherwise assigned by IANA or 
# otherwise claimed by a third party.  Based on the table in Wikipedia:
#
# http://en.wikipedia.org/wiki/List_of_TCP_and_UDP_port_numbers
#
# This list was prepared on 10/28/14 at 1:00 PM.
# The outer tuple contains a set of ranges; each range is in the inner tuple.

safe_port_nums = (
	(20001, 20013,),
	(20015, 20201,),
	(20561, 20594,),
	(20596, 20701,),
	(22351, 23072,),
)

def is_integer(arg):
    """Returns True if arg is an int or long, False otherwise.
    """
    if sys.version_info[0] < 3:
        return isinstance(arg, (int, long))
    else:
        return isinstance(arg, int)

def is_sequence(arg):
    """Returns True if arg is a list or tuple, False otherwise.
    """
    if isinstance(arg, str):
        return False

    return (not hasattr(arg, "strip") and
            hasattr(arg, "__getitem__") or
            hasattr(arg, "__iter__"))

def get_safe_portnum():
	"""Returns a "safe" non-ephemeral port number from a very long list.
	It can't actually try the number before returning; the caller does that
	when setting up a port and continues to call this until successful.
	"""

	ir = safe_port_nums[random.randint(0, len(safe_port_nums)-1)]
	#print(ir)
	iport = random.randint(ir[0], ir[1])
	return iport


def extract_agent_name (path):
    """Extracts the agent name from the full path of its "agent context"
    file and returns only the agent name
    """
    head, tail = os.path.split(path)
    aname, rest = tail.split('_context.json')
    return aname


def parse_command_line(args):
    """Call this just after the " if __name__ == '__main__' " test to validate 
    command line arguments passed in. If successful, the contents are returned 
    as a 4-tuple (agent_name, ac_path, ipaddr, port), otherwise returns None.
    """ 
    if len(args) >= 4:
	# Find out the agent process socket listener IP and port as well as the
	# path to the agent context file.
	
        ipaddr = args[1]
        port = int(args[2])
        ac_path = args[3]
	 
	# Isolate agent name and start logging
        aname = extract_agent_name(ac_path)
	
        return aname, ac_path, ipaddr, port
    else:
        return None

def random_keepalive (minsec, maxsec):
    "Returns a time (in seconds and fractions) between min and max seconds."
    return random.uniform(minsec, maxsec)

if __name__ == '__main__':
    #for i in range(100):
    #    print(get_safe_portnum())

    #for i in range(100):
    #    print(random_keepalive(5.2, 10.7))  
	
    path = "C:\\Users\\Mike\\Documents\\GitHub\\PyClarion\\simulations\\CI_simulation/agents/Alice/Alice_context.json"
    
    print(path)
    print(extract_agent_name(path))