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
#   11/08/14 - Initial commit to repository (as agent.py, in /staging).
#   01/07/15 - (MFL) Moved from staging into actual development.
#   01/12/15 - (MFL) Split AgentContext out of agent.py and is now standalone.
#   01/12/15 - (MFL) Cleaned up code.
#               

"""
The AgentContext is a per-agent store of the various parameters, dimensions, 
etc. known by an agent. One of these is created briefly to create the initial
agent_context.json file, which is subsequently read in by each of the agent's 
active subprocesses. To keep runtime sizes low, each agent subprocesses loads a 
local of AgentContext, keeps only what it needs, and then allows the entire 
AgentContext to be garbage collected.
"""

__author__ = 'Mike'

import sys
import os
import json
import random
import time
import argparse
import logging

# The Agent creates a database to store DVs, rules, chunks, GKS entries, etc.
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

# NOTE THAT THIS IS THE ONE TRUE IMPORT STYLE.
# SEE: http://stackoverflow.com/questions/5811463/when-to-use-absolute-imports

from clarion.core.project_context import ProjectContext
from clarion.core.dimension import Dimension, DimensionDict
from clarion.core.parameters import Parameters

from clarion.core.utilities import is_sequence

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  These are the process instantiation calls needed to set up a multiprocess
#  Clarion agent.  
#------------------------------------------------------------------------------

class AgentContext(object):
    """AgentContext contains the complete context needed by an agent. Each of 
    an agent's subprocesses will create temporary instance of it and retrive
    only those things that it needs.

    Calling its .build() method will allow it to be built up piecemeal from the
    supplied ProjectContext object, after which the additional agent-specific  
    files are loaded one after another. This is only done when first loading
    and creating the agent.

    Calling its .load() method will bring in the previously constructed agent
    context. This is how every agent subprocess will recover the entire 
    AgentContext previously saved out by the agent itself.
    
    For data structures that are used by multiple subprocesses (dimension, 
    parameters, actions), AgentContext performs the necessary parsing. For data 
    structures that are used by a single subprocess, that subprocess needs to 
    perform the necessary parsing and processing; all AgentContext does is 
    collect them up from the various JSON files and put them in the master
    <agent>_context.json file.
    """

    def __init__(self, aname):
        """Creates an empty AgentContext, except for the name and some object
        instantiation.
        """
        self.agent_name = aname
        self.dimensions = DimensionDict()       

        self.config = dict()

        # Rules and Actions
        self.actions = dict()
        self.fixed_rules = dict()
        self.irl_rules = dict()
        self.rer_rules = dict()

        # Networks in the ACS
        self.idn_networks = dict()

        # Motivation Subsystem
        self.drives = dict()
        self.goal_settings = dict()
        self.motivations = dict()
        self.goal_rules = dict()
        self.ms_networks = dict()

    def build(self, pcontext, files):
        """Builds the "agent context" JSON file out of the previously built 
        "project context" and additional JSON files by merging/overwriting data 
        from those files and then writing the JSON out. This is only done when 
        the agent is first being put together.
        """

        self.agent_path = pcontext.agent_path(self.agent_name)
        self.ac_path = self.agent_path + self.agent_name + "_context.json"
        logger.info ("---> agent path: {}".format(self.agent_path))
        logger.info ("---> agent context path: {}".format(self.ac_path))

        # TODO: Consider putting this into its own block
        self.sim_host = pcontext.sim_host
        self.sim_port = pcontext.sim_port
        self.env_host = pcontext.env_host
        self.env_port = pcontext.env_port
        self.proj_name = pcontext.proj_name
        self.proj_path = pcontext.proj_path
        self.clarion_path = pcontext.clarion_path

        # Fill in these essential objects
        self.parameters = pcontext.parameters.copy()
        self.dimensions.deep_copy(pcontext.dimensions)

        # Get ready to load one or more JSON files
        logger.info("Files to load for agent %s:", self.agent_name)
        self.loadfiles = list()     # list of paths to hand off to other processes
        if is_sequence(files):
            for f in files:
                fp = self.agent_path + f
                self.loadfiles.append(fp)
                logger.info("---> %s", fp)
        else:
            fp = self.agent_path + f
            self.loadfiles.append(fp)
            logger.info("---> %s", fp)
        
        # Now build the AgentContext, file by file, in the given order.
        for fp in self.loadfiles:
            print ("File", fp)
            self.load(fp)

        # Final step is to save out the built-up AgentContext so that all the
        # agent's subprocesses can read from it.
        self.save_to_json(self.ac_path)


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #   Each of the following "process_" routines handles one section in the
    #   JSON file(s).  
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def process_agent_configuration(self, jcontext):
        """Adds, or doesn't add, the various Clarion subsystems as needed by
        the simulation model.
        """
        # ---------------------------------------------------------------------
        #  These are set True or False depending on agent is using.
        #  All Clarion agents have to have an ACS, though.
        # ---------------------------------------------------------------------
        
        logger.info("In process_agent_configuration()")

        self.config = jcontext["configuration"]
        """
        self.hasACS = jcontext["config"].get("ACS")
        self.hasACS = 1     # There is ALWAYS an ACS
        self.hasIDN  = jcontext["config"].get("IDN")
        self.hasRER = jcontext["config"].get("RER")
        self.hasWM = jcontext["config"].get("WM")
        self.hasNACS = jcontext["config"].get("NACS")
        self.hasAMN = jcontext["config"].get("AMN")
        self.hasMCS = jcontext["config"].get("MCS")
        self.hasMS = jcontext["config"].get("MS")
        """

        # TODO: More needed here?

        self.defined = True     # we now know the agent's internal architecure

    def process_parameters(self, jcontext):
        """Updates (overwrites) the Parameters from the JSON load file. The 
        initial project-specific parameters were copied from the ProjectContext.
        """
        
        keys = jcontext["parameters"].keys()

        try:
            for x in keys:
                #logger.info("Trying to set parameter %s", x)
                self.parameters.set(x, jcontext["parameters"].get(x) )
        except Exception as e:
            logger.error("Could not access parameter %s", x)

    def process_dimensions(self, jcontext):
        """Appends the Dimensions from the JSON load file. Dimensions can 
        accumulate over multiple load files, but if any of these duplicate 
        existing dimensions, the existing dimension gets overridden. 
        """

        keys = jcontext["dimensions"].keys()

        for dname in keys:
            try:
                try:
                    d = jcontext["dimensions"].get(dname)
                except:
                    logger.error(">>> problem retrieving Dimension key for %s", dname)

                try:
                    if "minval" in d:
                        minv = d["minval"]
                    else:
                        minv = None
                    
                    if "maxval" in d:
                        maxv = d["maxval"]
                    else:
                        maxv = None
                    
                    #print(dname, d["dtype"], d["mode"], d["vals"], minv, maxv)
                    dim = Dimension(dname, d["dtype"], d["mode"], d["vals"], minv, maxv)
                    #print (dim)        
                    self.dimensions.append(dim)

                except:
                    logger.error("Problem with Dimension() call for %s", dname)


                # TODO: Go back to this once databasing is working:
                #self.dimensions.append(dim)
                #self.dimensions[dname] = dim

            except Exception as e:
                logger.error("In 'Dimensions', could not process %s", dname) 

        pass #self.dimensions[x] = jcontext["Dimensions"].get(x)

    def process_actions(self, jcontext):
        """Appends the Actions from the JSON load file. Actions can accumulate
        over multiple load files, but if any of these duplicate existing 
        actions, the earlier action gets overridden. 
        """

        keys = jcontext["actions"].keys()
        # DEBUG # print(keys)

        for verb in keys:
            try:
                try:
                    act = jcontext["actions"].get(verb)
                except:
                    logger.error("Problem retrieving Action key for {}".format(verb))
                
                try:
                    # "bind" is the name of a function that will be called if
                    # this action is selected. That must the name of a function
                    # supplied in the agent's code module that subclasses Agent.

                    # Yes, this is the Python ternary operator

                    callback = act["bind"] if "bind" in act else None

                    # DEBUG # print(callback)
                    
                    # 'dimensions' is a dict of one or more dimensions which 
                    # will have values computed for it/them as part of 
                    # outputting this action chunk. Only those dimensions
                    # given here will be made part of that chunk.
                    if "dimensions" in act:
                        dims = act["dimensions"]
                    else:
                        dims = None
                    # DEBUG # print(dims)

                    """
                    -- ANYTHING ELSE?
                    # 'dimensions' is a dict of one or more dimensions which 
                    # will have values computed for it/them as part of 
                    # outputting this action chunk.
                    if "dimensions" in act:
                        dims = act["maxval"]
                    else:
                        dims = None
                    """

                    # TODO: Parsing for _feedback
                    
                    #print(dname, d["dtype"], d["mode"], d["vals"], minv, maxv)
                    #dim = Action(verb, callback, act["dimensions"], d["vals"], minv, maxv)
                    #print (dim)        
                    #self.dimensions.append(dim)
                
                except:
                    logger.error("Problem processing Action {}".format(verb))


                # TODO: Go back to this once databasing is working:
                #self.dimensions.append(dim)
                #self.dimensions[dname] = dim

            except Exception as e:
                logger.error("In 'process_actions', could not process {}".format(verb))
    
    
    def process_idn_networks(self, jcontext):
        pass

    def process_drives(self, jcontext):
        pass

    def process_goal_settings(self, jcontext):
        pass

    def process_motivations(self, jcontext):
        pass
    
    def process_generic_entry(self, jcntx, target, entry):
        """For the supplied entry (one of the top level dict-like entries in 
        the JSON file), retrieve its dict items and add them to the passed-in
        dict that they are intended for.
        """

        if entry in jcntx:
            # verbosity # logger.info("generically processing {}".format(entry))
            
            keys = jcntx[entry].keys()
            print(keys)
            count = 0
            for itemkey in keys:        
                try:
                    try:
                        item = jcntx[entry].get(itemkey)
                    except:
                        logger.error("Problem retrieving key {} for entry {}".format(itemkey, entry))
                    
                    try:        
                        
                        if itemkey in target:
                            logger.warning("The key {} for entry {} already exists but is getting overridden".format(itemkey, entry))
    
                        target[itemkey] = item
                        count += 1
                        
                    except:
                        logger.error("Problem processing key {} for entry {}".format(itemkey, entry))
    
    
                    # TODO: Go back to this once databasing is working:
                    #self.dimensions.append(dim)
                    #self.dimensions[dname] = dim
    
                except Exception as e:
                    logger.error("In 'process_actions', could not process {}".format(verb))
                
            return count        
        else:
            #logger.info("No entry for {} found".format(entry))
            return 0
                
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #   The load() function is used to build up the agent context from one or
    #   more descriptor files.
    #
    #   The load_agent_context() function is used to retrieve an entire agent
    #   context.
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def load(self, jpath):
        """Call once or more to load agent data from JSON into the agent. Can 
        be called multiple times, each with a different JSON file. In case of 
        duplicate items, AgentContext always takes the last one loaded as the 
        definitive one. 
        """

        try:
            json_data = open(jpath)
            logger.info("Was able to open %s", jpath)
        except:
            logger.error("File '%s' not found.", jpath)
            return False

        try:
            jcontext = json.load(json_data)
            logger.info("Created context for %s", jpath)            
        except:
            logger.error("JSON errors found in %s", jpath)
            return False

        # TODO: This is ugly. Rework it.

        try:
            if "configuration" in jcontext:
                # verbosity # logger.info("agent context")
                self.process_agent_configuration(jcontext)

            if "parameters" in jcontext:
                # verbosity # logger.info("parameters context")
                self.process_parameters(jcontext)

            if "dimensions" in jcontext:
                # verbosity # logger.info("dimensions context")
                self.process_dimensions(jcontext)
                # TODO: self.dimensions.load_from_json(self.context)

            if "actions" in jcontext:
                # verbosity # logger.info("actions context")
                self.process_actions(jcontext)
        
            self.process_generic_entry(jcontext, self.fixed_rules, "fixed_rules")
            self.process_generic_entry(jcontext, self.irl_rules, "irl_rules")
            self.process_generic_entry(jcontext, self.rer_rules, "rer_rules")

            self.process_generic_entry(jcontext, self.idn_networks, "idn_networks")

            self.process_generic_entry(jcontext, self.drives, "drives")
            self.process_generic_entry(jcontext, self.goal_settings, "goal_settings")
            self.process_generic_entry(jcontext, self.motivations, "motivations")
            self.process_generic_entry(jcontext, self.goal_rules, "goal_rules")
            self.process_generic_entry(jcontext, self.ms_networks, "ms_networks")

            json_data.close()
            return True

        except:
            logger.error("Errors loading file %s.", jpath)
            return False

    def load_agent_context(self, acpath):
        """Used to retrieve an entire agent context.  This should be called
        once with only the main <agent>_context.json file itself.  It loads the 
        master information, then in turn calls the load() function, which 
        loads in the various sections.
        """
 
        try:
            json_data = open(acpath)
            logger.info("Was able to open the agent\'s context file %s", acpath)
        except: 
            logger.error("Context file '%s' not found.", acpath)
            return False

        try:
            jfile = json.load(json_data)
            logger.info("Loading main context elements for %s", acpath)            
        except:
            logger.error("JSON errors found in %s", acpath)
            return False

        try:
            # Read in essential top-level information
            self.agent_path = jfile["agent_path"]
            self.clarion_path = jfile["clarion_path"]
            self.env_host = jfile["env_host"]
            self.env_port = jfile["env_port"]
            self.proj_name = jfile["proj_name"]
            self.proj_path = jfile["proj_path"]
            self.sim_host = jfile["sim_host"]
            self.sim_port = jfile["sim_port"]
            # TODO: agent host and port? 
            
            json_data.close()
        except:
            logger.error("Errors loading file %s.", acpath)

  
        self.parameters = Parameters()

        # Now retrieve the individual sections
        self.load(acpath)


#------------------------------------------------------------------------------
#  Methods for  Saving to JSON and loading from JSON for the agent itself.
#------------------------------------------------------------------------------

    def save_to_json(self, path):
        try:
            fp = open(path, 'w')
            logger.info("Was able to open %s for writing", path)
        except:
            logger.error("File '%s' could not be opened, or not found.", path)
            return False
        
        try:
            json.dump(self.__dict__, fp, cls=AgentContextEncoder)
        except:
            logger.error("File '%s' could not be opened, or not found.", path)
            return False
        finally:
            fp.flush()
            fp.close()

    def load_from_json(self, path):
        """Converts a packet received over a socket (after .decode() was run
        on it) into a viable ProjectContext.
        """

        # TODO: Rewrite with with

        pc = AgentContextShell()
        try:
            json_data = open(path)
            logger.info("Was able to open %s", path)
            return True
        except Exception as e:
            logger.error("File %s not found.", path)
            return False, e
        
        try:
            pc.__dict__ = json.loads(json_data, cls=AgentContextDecoder)      # Yes, this works
            return pc

        # TODO: deal with the exception 
        except Exception as e:
            logger.error("Error processing file %s", path)
            return False, e

#------------------------------------------------------------------------------
#  Helper classes for serializing the agent itself.
#------------------------------------------------------------------------------

class AgentContextShell(object):
    """This is an empty instance of an object with a __dict__.  It later gets  
    turned into an AgentContext from incoming socket data.
    """
    pass

class AgentContextEncoder(json.JSONEncoder):
    """ Converts a python object, where...
    -- a Parameters object is converted into its dict representation 
    -- a Dimensions object is converted into a DimensionDict
    """
    def default(self, obj):
        if isinstance(obj, Parameters):
            return obj.__dict__
        if isinstance(obj, DimensionDict):
            return obj.__dict__
        if isinstance(obj, Dimension):
            return obj.__dict__

class AgentContextDecoder(json.JSONDecoder):
    """ 
    Converts a json string, where datetime and timedelta objects were converted
    into objects using the DateTimeAwareJSONEncoder, back into a python object.
    """

    def __init__(self):
            JSONDecoder.__init__(self, object_hook=self.dict_to_object)

    def dict_to_object(self, d): 
        if '__type__' not in d:
            return d

        type = d.pop('__type__')
        if type == 'Parameters':
            return Parameters(**d)
        if type == 'Dimensions':
            return DimensionDict(**d)
        #elif type == 'timedelta':
        #    return timedelta(**d)
        else:
            # Oops... better put this back together.
            d['__type__'] = type
            return d



