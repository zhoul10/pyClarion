"""
This module defines the Agent class, the core class for creating a Clarion 
agent. A single agent can be instanced by calling its constructor, or via
the AgentFactory (preferred, especially for multi-agent simulations).

Usage
=====

The main export of this module is the ``Agent`` class. A pyClarion ``Agent`` 
is a module that houses a single Clarion agent and manages all of its 
sub-components (ACS, NACS, etc.). The detailed construction of an agent, 
which elements it excludes or includes, their "parameters," and so forth,
are specified through JSON files or in code.

Instantiation
-------------

The agent is preferentially constructed with a name that is given to it in the
constructor. If no name is given, one is supplied.

>>> Agent("Alice")
Alice

>>> Agent()
"""

__author__ = 'Mike'

import sys
import os
import json
import random
import time
import argparse
import logging
import uuid

"""
THIS IS GOING TO CHANGE:
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
"""

"""
BRING THESE BACK IN AS THEY ADDED TO THE PROJECT:

# TODO: Until Clarion is a proper package, add this line of code to the files:
# TODO: Investigate __init__.py issues.
sys.path.append("C:\\Users\\Mike\\Documents\\GitHub\\PyClarion")

from clarion.core.agent_context import AgentContext

# The Agent creates a database to store DVs, rules, chunks, GKS entries, etc.
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

### TODO: from clarion.subsystems.acs.actioncenteredsubsystem import ActionCenteredSubsystem
#from clarion.core.component import Component

# NOTE THAT THIS IS THE ONE TRUE IMPORT STYLE.
# SEE: http://stackoverflow.com/questions/5811463/when-to-use-absolute-imports

#import clarion.core
#from clarion.core.component import Component

from clarion.core.agent_context import AgentContext

# TODO: The need for "Component" may be going away.
#from clarion.core.component import Component

from clarion.core.dimension import Dimension, DimensionDict

from clarion.core.parameters import Parameters
#from environments.filemanager import FileManager

from clarion.core.utilities import is_sequence
"""

logger = logging.getLogger(__name__)

################
#  AGENT TYPE  #
################


class Agent:
    """Agent is the top-level class that implements a full Clarion cognitive 
    architecture for an agent and represents a single agent in the simulation
    environment.

    The Agent object runs in the context of the simulation and is essentially a
    stub object which provides a front-end for the multi-process-based agent
    processes that together actually comprise a working Clarion agent.

    It does the following:

    -- Reads all the agent's JSON files and merges them with the previously
        constructed project context, thus creating the agent's entire "agent
        context", which it saves out.

    -- When told to, fires up the AgentProcess (which is not the same as Agent).
        AgentProcess runs as a separate process, and its subprocesses in turn run
        in separate contexts.  THIS MAY CHANGE!
    """

    def __init__(self, aname, pcontext, files):
        """Instances the agent and gets it ready for launch.

        aname is the name of the agent, like "Alice".

        pcontext is the project_context that was previously created by the
        Simulation.  Agent builds on the project context data.

        files can point to a single agent-specific JSON file or be a list or 
        tuple of named files to be loaded one after another. At least one file 
        must be specified.

        Does the following:
            -- copies the passed-in project context data (parameters and 
                dimensions, etc.) into the agent-specific agent context
            -- processes the additional agent-specific JSON file(s) and 
                merges it/them with the project context data
            -- saves the resulting agent context out  
            -- establishes the agent's topology (subprocesses)
            -- starts socket listener for the subprocesses

        DISCUSS: PCONTEXT IS PROBABLY GOING AWAY. IT COULD BE SOMETHING
        PUSHED INTO THE FACTORY.
        """ 

        self.agent_name = aname
        logger.info("Initializing agent %s", self.agent_name)

        # This call causes the agent's agent_context JSON file to be created.
        temp = AgentContext(aname)
        temp.build(pcontext, files)
        self.clarion_path = temp.clarion_path
        self.ac_path = temp.ac_path
        # self.context.load_agent_context(acp) , pcontext, files

        logger.info("Created agent {}'s agent_context file.".format(self.agent_name))

        # All the subprocesses that make up the agent, in strict order
        # of launch.

        self.processes = list()     # TODO: Special collection for this?

        self.defined = False  # set True after agent architecure is specified.
             
        # TODO: RETURN TO THIS LATER!
        # TODO: FIX cannot have a RAM DB if we're multiprocess.
        # self.engine = create_engine('sqlite:///:memory:', echo=True)
        # self.decl_base = declarative_base()

        logger.info("... My name is %s", self.agent_name)

    # ------------------------------------------------------------------------------
    #  Methods for setting up the various subprocesses begin here.
    # ------------------------------------------------------------------------------

    def launch_agent(self, loop):
        """Attempts to launch the "agent_process" (boss process for any agent),
        which in turn should launch all its own subprocesses.
        """

        print("===== Trying to launch the agent process =====")
        logger.info("Trying to launch the agent process")

        # debug # print("Path to agent process: %s", self.clarion_path)
        # debug # print("Path to agent context file: %s", self.ac_path)

        try:
            # TODO: Fix hard coding
            coro2 = self.launch_agent_process(sys.executable,
                                              self.clarion_path + "/agent/agent_process.py", self.ac_path)
            # debug # print("executable", sys.executable),
            # debug # print("clarion_path", self.clarion_path)
            # debug # print("ac_path", self.ac_path)
            logger.info("... back from setting up the coroutine")

        except:
            logger.error("... problem setting up the coroutine")
            print("... problem setting up the coroutine")

        print("Did the launch...")

        exitcode = loop.run_until_complete(coro2)

        # time.sleep(10)

        logger.info("Back from launch call with exitcode: {}".format(exitcode))

    @asyncio.coroutine
    def launch_agent_process(self, *args):
        """This launches the separate agent_process, which does all the rest
        of the work of running the agent.
        """
        try:
            print("inside launch_agent_process")
            print("args", *args)

            """
            Big experiment... don't create pipes
            self.agent_proc = yield from asyncio.create_subprocess_exec (*args, 
                                                                         stdin=subprocess.PIPE, 
                                                                         stdout=subprocess.PIPE, 
                                                                         stderr=subprocess.STDOUT)
            """
            self.agent_proc = yield from asyncio.create_subprocess_exec(*args)

            print("... got past the yield")
        except:
            logger.error("... problem with launch_agent_process")
            print("... problem with launch_agent_process")

    def launch_subprocesses(self):
        for p in iter(agent_subprocesses):
            print(p)
            self.launch_subprocess(p)

    # ------------------------------------------------------------------------------
    #  Methods for setting up the various subprocesses begin here.
    #    THESE ARE GOING AWAY!
    # ------------------------------------------------------------------------------

    def main_loop(self):
        pass

    # -------------------------------------------------------------------------
    #  Test and utility functions begin here.
    # -------------------------------------------------------------------------


class AgentFactory(dict):
    """AgentFactory BLAH.
    """

    def __init__(self, aname):
        """
        """

        self.agent_name = aname

        self.ACS = ActionCenteredSubsystem()

        self.NACS = None  # TODO # of type NonActionCenteredSubsystem
        self.MS = None  # TODO # of type MotivationSubsystem
        self.MCS = None  # TODO # of type MetaCognitiveSubsystem

        self.WM = None  # TODO # of type WorkingMemory
        self.SI = None  # TODO # of type SensoryInformation

        self.DVCollection = None  # TODO # of type DVCollection
        pass

    def AttachNACS(self):
        """
        """
        pass

    def AttachMS(self):
        """
        """
        pass

    def AttachMCS(self):
        """
        """
        pass


def main(argv):
    print("Here I am")
    # print 'Number of arguments:', len(argv), 'arguments.'
    print('Argument List:', str(argv))

    if len(argv) >= 2:
        path = argv[1]
        print(path)
        if fm.FileManager.ValidPath("xxx"):
            print("path is good")
        else:
            print("path is bad")


if __name__ == '__main__':
    # TODO: Get rid of hard coding
    pth = "C:\\Users\\Mike\\Documents\\GitHub\\clarion-architecture\\clarion\\test_agent.json"
    # TODO: Deal with global parameters
    a = Agent("test_agent", pth, None)
    a.load(pth)
    a.launch_processes()

    print(a.MS_process)

    print(a.MS_process.is_alive())

    k = 0

    # a.MS_process.join()

    for i in range(4):
        ss = random.randint(1, 4)
        k += 1
        time.sleep(ss)
        msg = "Another message " + str(k) + " taking " + str(ss) + " seconds"
        a.MS_sendQ.put(msg)

    print(a.MS_recvQ.get_nowait())
    print(a.MS_recvQ.get_nowait())
    print(a.MS_recvQ.get_nowait())
    print(a.MS_recvQ.get_nowait())

    # a.MS_sendQ

    # TODO: More testing
