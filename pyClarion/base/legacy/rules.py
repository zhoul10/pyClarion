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


""" 
This module contains definitions for the Rule class and its several subclasses.

"""

__author__ = 'Mike'

import os
import sys
import time
import random
import socket
import json
import logging

# TODO: Until Clarion is a proper package, add this line of code to the files:
# TODO: Investigate __init__.py issues.
sys.path.append("C:\\Users\\Mike\\Documents\\GitHub\\PyClarion")

#print(sys.path)    # Uncomment if having problems locating import paths

# TODO: Bring back Environment someday
#from clarion.environment import Environment

from clarion.core.project_context import ProjectContext
from clarion.core.dimension import Dimension
from clarion.core.chunk import Chunk
import clarion.core.utilities as utilities


# Set up the logging before anything else.  Note that the Simulation-level
# logging is separate from the Environment-level logging.

logger = logging.getLogger(__name__)

K_FIXED_RULE = 1
K_IRL_RULE = 2
K_RER_RULE = 3

class Rule(object):
    """Parent class of the subtypes FixedRule, IRLRule and RERRule.
    """
    
    def __init__(self):
        cchunk = None
        action = None
        rule_type = None
        match_all = True    # TODO
        bla = 0.0
        
    def parse_cond_chunk(cclst):
        """Parses the condition chunk DV pairs passed in as a list.

        @return Chunk   a condition chunk object
        """
        if utilities.is_sequence(cclst):
            cchunk = Chunk(None, Chunk.CT_CONDITION, None, None, -1)

            for dv in cclst:
                cchunk.set_dvpair(self, dv, cclst[dv])
                print(dv, cclst[dv]) 
            
        return cchunk
    
    def load_from_json(self, jcontext):
        """Loads a single rule from the stub point within a JSON file. Call
        repeatedly to load all the rules from a previously saved ARS JSON file.
        """
        pass
                       
 
    def saves_to_json(self, jcontext):
        """Saves a single rule into the json context. Call repeatedly to save
        all the rules into a new ARS JSON file.
        """
        pass
    
    def process_fixed_rules(self, jcontext):
        """Appends the Fixed Rules from the JSON load file. Fixed Rules can 
        accumulate over multiple load files, but if any of these duplicate 
        existing ones, the earlier one gets overridden. 
        """
    
        keys = jcontext["fixed_rules"].keys()
        print(keys)
    
        for frname in keys:
            try:
                try:
                    rule = jcontext["fixed_rules"].get(frname)
                except:
                    logger.error("Problem retrieving Fixed Rule key for {}".format(frname))
                
                try:
                    action = rule["action"] if "action" in rule else None
                except:
                    logger.error("Error processing action in Fixed Rule {}".format(frname))
    
                try:
                    tmplst = rule["condition_chunk"] if "action" in rule else None
                    if tmplst is not None:
                        cc = parse_cond_chunk(tmplst)
    
                except:
                    logger.error("Error processing action in Fixed Rule {}".format(frname))
    
    
                # TODO: Go back to this once databasing is working:
                #self.dimensions.append(dim)
                #self.dimensions[dname] = dim
    
            except Exception as e:
                logger.error("In 'process_actions', could not process %s", verb)
    
    
    def process_irl_rules(self, jcontext):
        pass

