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
import clarion.core.rules as Rule
import clarion.core.utilities as utilities


# Set up the logging before anything else.  Note that the Simulation-level
# logging is separate from the Environment-level logging.

logger = logging.getLogger(__name__)


    
"""
HOW RER WORKS (from Clarion Tutorial, p. 41)
1. Update the rule statistics (to be explained later).
2. Check the current criterion for rule extraction, generalization, and
specialization:
	2.1. If the result is successful according to the current rule extraction
	criterion, and there is no rule matching the current state and action,
	then perform extraction of a new rule: condition -> action. Add the
	extracted rule to the ARS.
	2.2. If the result is unsuccessful according to the current specialization
	criterion, revise all the rules matching the current state and action
	through specialization:
		2.2.1. Remove the rules from the rule store.
		2.2.2. Add the revised (specialized) versions of these rules into the rule
		store.
	2.3. If the result is successful according to the current generalization
	criterion, then generalize the rules matching the current state and action
	through generalization:
		2.3.1. Remove these rules from the rule store.
		2.3.2. Add the generalized versions of these rules to the rule store.

"""
    
    
# Current State Buffer (CSB)  current_state_buffer

class ActionRuleStore(dict):
    """The ActionRuleStore (ARS) stores and manages the rules in the top level
    of the ACS. It also supports operations for Rule Extraction and Refinement
    (RER) and databasing.
    """
    
    def __init__(self): 
        fr_store = {}
        irl_store = {}
        rer_store = {}      
        pass
    
    def add_rule(self, rule):
        """Adds the rule to the correct collection within the ARS. In old 
        Clarion this was commit_action_rule()
        """
        
        if is_instance (FixedRule, rule):
            fr_store.add(rule)
        elif is_instance (IRLRule, rule):
            irl_store.add(rule)
        elif is_instance (RefineableActionRule, rule):
            rer_store.add(rule)
            
				
        # Something about extractParameters
        # Something about prevEM    
        """
        			if (r.InRuleStore):	# FIX
				# WHAT IS mas ?
				if (!mas.ContainsKey(r.ActionChunkID))
				{
					ma = RefineableActionRule()
					
					if (extractParameters != null)
					{
						dynamic[] p = new dynamic[extractParameters.Count()];
						int count = 0;
						foreach (dynamic d in extractParameters)
						{
							p[count] = d;
							++count;
						}
						ma = extractFactory.Generate(r.Action, p);
					}
					else
						ma = extractFactory.Generate(r.Action);

					ma.IsMatchAll = true;

					mas.Add(ma.ActionChunkID, ma);
				}


				if(prevEM != null)
					r.LastEligibleTimeStamp = prevEM.RelatedSI.TimeStamp;

				foreach (Rule cr in r.Children)
					World.GetAgent(aID).RemovePublisherSubscriber(cr);
        """
    
    
    def delete_rule (self, rule):
        """Adds the rule to the correct collection within the ARS. In old 
        Clarion this was RetractActionRule()
        """
        
        if is_instance (FixedRule, rule):
            fr_store.remove(rule)
        elif is_instance (IRLRule, rule):
            irl_store.remove(rule)
        elif is_instance (RefineableActionRule, ar):
            rer_store.remove(rule)
				
    
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
    
    
    
    def find_rules(self, si):
        """Finds all rules that match the incoming Sensory Input (si). How many
        are returned are a function of relevant Clarion parameters.
        
        These are in an ordered list with the rule at [0] the one that best
        matches. It is possible for none or only one rule to be returned.
        """
        pass