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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#   CHANGE HISTORY:
#       01/07/15 - (MFL) Removed load_initial_json(), not needed
#       01/07/15 - (MFL) Allowed for rehoming project by passing a nonlocal
#                   path to the constructor. (This facilitates testing.)
#       01/07/15 - (MFL) Clean-ups
#

__author__ = 'Mike'

# TODO: Add command line options (logging, etc.)

import sys
import os
import io
import json
import logging
from pathlib import Path  # This is P3.4 and up only

from clarion.core.parameters import Parameters
from clarion.core.dimension import Dimension, DimensionDict

logger = logging.getLogger(__name__)

# This is how agents locate themselves within simulation project folders
AGENTS_FOLDER = "/agents/"
ARCHETYPES_FOLDER = "/archetypes/"
SHARED_STUB = "_shared/"

class ProjectContextEncoder(json.JSONEncoder):
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

class ProjectContextDecoder(json.JSONDecoder):
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

class ProjectContextShell(object):
    """This is an empty instance of an object with a __dict__.  It later gets  
    turned into a ProjectContext from incoming socket data.
    """
    pass


class ProjectContext(object):
    """Container to hold various simulation-wide config info to be passed 
    around the various agents and their subprocesses.
    """

    def __init__(self, jfile):
        """Gets called at the beginning of any simulation to establish a
        centralized store of simulation-wide objects. This is not a "global".
        It loads the config data and the simulation-wide set of parameters 
        (and possibly Dimensions) from the JSON file associated with this 
        simulation itself.
        
        Does the following:
        -- reads the simulation-level config file
        -- establishes various file paths
        -- establishes address and port for sim-level socket listener
        -- Sets up the sim-level Parameters block
        -- Sets up the sim-level Dimensions (if any)
        -- knows how to find agents and archetypes
        """
        super(ProjectContext, self).__init__()

        # Create simulation-wide parameters block. Agents can later override 
        # any parameters they like from there.
        self.parameters = Parameters()

        # Create empty DimensionDict. It will get loaded from the JSON file. 
        self.dimensions = DimensionDict()

        currpath = os.getcwd()
        self.proj_name = Path(currpath).name
        self.jfilepath = currpath + '/' + jfile
        self.proj_path = os.path.dirname(self.jfilepath)

        logger.info("Project Name: %s", self.proj_name) 
        logger.info("jfile path is {}".format(self.jfilepath))
        logger.info("Actual project path is {}".format(self.proj_path))

        logger.info("Attempting to open %s", self.jfilepath)
        
        # TODO: Add error handling
        json_data = io.open(self.jfilepath)
        context = json.load(json_data)

        self.env_host = context["environment"].get("env_host")
        self.env_port = int(context["environment"].get("env_port"))
        self.multi_sim = int(context["environment"].get("multi_sim"))

        # TODO: Refactor
        good = True
        keys = context["parameters"].keys()
        for x in keys:
            good = good and self.parameters.set(x, context["parameters"].get(x))

        self.dimensions.load_from_jcontext(context)
        json_data.close()

    def pcontext_filepath(self):
        """Returns full path to the generated pcontext file itself.
        """
        return self.proj_path + '/pcontext.json'

    def agent_path(self, agntname):
        """Returns full path to agent's own folder, w/ slash at end
        """
        return self.proj_path + '/agents/' + agntname + '/'

    def archetype_path(self, archname):
        """Returns full path to archetype's folder, w/ slash at end
        """
        return self.proj_path + '/archetypes/' + agntname + '/'

#------------------------------------------------------------------------------
#  Service functions of various kinds
#------------------------------------------------------------------------------

    # Wrapped utility functions for parameters

    def set_parameter(self, pname, pval):
        return self.parameters.set (pname, pval)

    def get_parameter(self, pname):
        return self.parameters.get (pname)

#------------------------------------------------------------------------------
#  Saving to JSON and loading from JSON for this class
#------------------------------------------------------------------------------

    def save_pcontext(self):
        """Saves the generated pcontext in whatever directory holds the project
        as <path>/pcontext.json.
        """

        pcpath = self.pcontext_filepath()
        self.save_to_json(pcpath)

    def save_to_json(self, path):
        """Saves the generated pcontext at the desired path."""

        try:
            fp = open(path, 'w')
            logger.info("Was able to open %s for writing", path)
        except:
            logger.error("File '%s' could not be opened, or not found.", path)
            return False
        
        try:
            json.dump(self.__dict__, fp, cls=ProjectContextEncoder)
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
        pc = ProjectContextShell()
        try:
            json_data = open(path)
            logger.info("Was able to open %s", path)
        except:
            logger.error("File '%s' not found.", path)
            return False
        
        try:
            pc.__dict__ = json.loads(json_data, cls=ProjectContextDecoder)      # Yes, this works
            return pc
        except:
            return None
       
#------------------------------------------------------------------------------
#  Encoding and decoding this class for socket transmission
#------------------------------------------------------------------------------

    @staticmethod
    def init_from_packet(x):        
        """Converts a packet received over a socket (after .decode() was run
        on it) into a viable ProjectContext.
        """
        pc = ProjectContextShell()
        try:
            pc.__dict__ = json.loads(x, cls=ProjectContextDecoder)      # Yes, this works
            return pc
        except:
            return None

    def convert_to_packet(self):
        """Turns the ProjectContext into a JSON'd string, almost ready to send.
        (It will still need to have .encode() run on it in the Protocol.)
        """
        try:
            return json.dumps(self.__dict__, separators=(',', ':'), 
            	cls=ProjectContextEncoder)
        except:
            return "CRAP".encode()