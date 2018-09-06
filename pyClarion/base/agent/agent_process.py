from __future__ import absolute_import

# Clarion Architecture implementation in Python.
# Copyright (C) 2013-2015 Clarion-Architecture Authors (see AUTHORS.txt)
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
# CHANGE HISTORY:
#   11/08/14 - Initial commit to repository.
#   01/12/15 - (MFL) Continued work on AgentProtocol.
#   01/22/15 - (MFL) Finished conn state machine. Now works with acs_processs.py
#   01/24/15 - (MFL) Changed code to remove cmd ("c") in Chunks
#   01/24/15 - (MFL) Fixed tic counting
#   08/06/15 - (MFL) Adding agent <--> simulation comm; some cleanups

# NOTE:

__author__ = 'Mike'

import os
import sys
import time
import random
import json
import logging

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

# TODO: Until Clarion is a proper package, add this line of code to the files:
# TODO: Investigate __init__.py issues.
# sys.path.append("C:\\Users\\Mike\\Documents\\GitHub\\PyClarion")

sys.path.append("/home/ratchet/pyclarion/TRUNK")

from clarion.core.chunk import Chunk

import clarion.core.utilities as utilities
from clarion.core.agent_context import AgentContext
import clarion.core.asyncio_api as asyncio_api

# print ("agent_process is starting...")

acs_proc = None

# List of all the agent subprocesses that can potentially be launched, in the
# correct order.
#
# Contains (testname, varname, py-version, filename)
agent_subprocesses = [
    ("ACS", "acs_proc", "python3", "acs_process.py"),
    ("IDN", "idn_proc", "python2", "idn_process.py"),
    ("WM", "wm_proc", "python3", "wm_process.py"),
    ("NACS", "nacs_proc", "python3", "nacs_process.py"),
    ("AMN", "amn_proc", "python2", "amn_process.py"),
    ("MS", "ms_proc", "python2", "ms_process.py"),
    ("MCS", "mcs_proc", "python2", "mcs_process.py")
]


class SubprocessWrangler(dict):
    """Wrangles the various subprocesses launched by this process while
    getting the agent launched. As each subprocess connects to the agent
    process (this one), it is entered here.
    """

    def __init__(self):
        super(SubprocessWrangler, self).__init__()


subprocesses = SubprocessWrangler()

# Holds the transports objects for communicating with the various subprocesses
transports = dict()

transports["ACS"] = 'ANGRY'
transports["IDN"] = 'FEARFUL'
transports["WM"] = 'SURPRISED'

# Holds all the action recommendations received by the ACS
action_recs = []

# Used for computing delta-T.
time_stamp = 0.

global the_SI_chunk


def Random_PA_sleep():
    """Generates a delay of about 50 mS, but with some randomness.
    """
    stall = random.randint(20, 30) / 1000.0
    # print(stall)
    time.sleep(stall)


# ----------------------------------------------------------------------------
# Flag mechanism
#
# Each subprocess has a corresponding flag, which is set to 1 when the agent
# hasn't heard back from a subprocess, and gets set to 0 once the subprocess
# does. When all flags are 0 (and their sum is zero), another PA Cycle can be
# launched
# ----------------------------------------------------------------------------

# For any PA cycle, any subprocess that has not yet responded has flag set to 1
global acs_flag
global idn_flag


# TODO: This could be better
def set_flags():
    global acs_flag
    global idn_flag
    acs_flag = 1
    idn_flag = 1


# TODO: This could be better
def reset_flag(who):
    global acs_flag
    global idn_flag

    if who == "ACS":
        acs_flag = 0
    elif who == "IDN":
        idn_flag = 0


def select_action():
    if len(action_recs):
        pass


def cycle_pa_loop():
    global acs_flag
    global idn_flag
    global the_SI_chunk

    logging.debug("Entering cycle_pa_loop")

    # Only do this when we're supposed to.
    if acs_flag + idn_flag == 0:

        # Log the contents of action_recs
        logging.debug("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
        for c in action_recs:
            ct = "From " + c.s + ", type =" + str(c.t)
            logging.debug("-------- {}".format(ct))
        logging.debug("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")

        select_action()
        # TODO: do something with the action!

        del action_recs[:]

        logging.debug("Generating a random SI chunk")
        Random_PA_sleep()
        agent.advance_tic()

        acs_flag = 1
        idn_flag = 1

        the_SI_chunk = agent.generate_random_si_chunk("***")
        print(the_SI_chunk)
        # The s field will need to be updated each time this is sent.

        # Works fine; print statements are for diagnostics.
        """
        print(len(transports))
        for t in transports:
            trans = transports[t]
            print(trans)
        """

        # Tell the affected parties about the new SI.
        # TODO: THis needs to be normalized better!
        trans = transports["ACS"]
        # verbosity # logging.debug("trans for ACS is {}".format(trans))
        the_SI_chunk.set_receiver("ACS")
        msg = json.dumps(the_SI_chunk.__dict__)
        trans.write(msg.encode())
        logging.debug("AGENT SENDS: {}".format(msg))
        print("AGENT SENDS: {}".format(msg))

        trans = transports["IDN"]
        # verbosity # logging.debug("trans for IDN is {}".format(trans))
        the_SI_chunk.set_receiver("IDN")
        msg = json.dumps(the_SI_chunk.__dict__)
        trans.write(msg.encode())
        logging.debug("AGENT SENDS: {}".format(msg))
        print("AGENT SENDS: {}".format(msg))

    else:
        logging.debug(" -----    flags: {} {}".format(acs_flag, idn_flag))


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Signature for Chunk init is: type, sndr, rcvr, cmd, tic, log=None, cname=None
# Asterisk for cname causes chunk's name to be C following by an autoincrement
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


class AgentProtocol(asyncio.SubprocessProtocol):
    """Main protocol handler by which an agent's sub-processes communicate with
    the agent process. This class is the master message broker for the agent
    with regards to its various sub-processes. This is NOT the protocol by
    which the agent communicates with the overall simulation.
    """

    def __init__(self):
        super(AgentProtocol, self).__init__()

        self.ccount = 0
        self.retries = 0
        self.terminate = False

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        logging.info('connection from {}'.format(peername))
        self.transport = transport
        self.rport = (transport.get_extra_info("peername"))[1]

        # print(transport)
        # print(self.rport)
        try:
            subprocesses[self.rport] = "NEW"
        except:
            print("Bombed")

        # Note that all meta-commands that aren't chunks must start with '!'
        self.transport.write("!Welcome".encode())

    def data_received(self, data):
        x = data.decode()
        # DEBUG # print('--RCVD--: {}'.format(x))
        logging.info('--RCVD--: {}'.format(x))
        # DEBUG # print(len(subprocesses))

        msg = self.process_message(x)

        if msg != None:
            logging.debug("--SENT--: {}".format(msg))
            # DEBUG #  print("--SENT--: {}".format(msg))

            try:
                self.transport.write(msg.encode())
            except:
                # This appears to happen because of what's going on in Simulation
                logging.debug("**************** GOT NULL DATA **************** {}".format(x))

    def eof_received(self):
        logging.debug("**************** eof_received ****************")

    def pipe_data_received(fd, data):
        """ Called when the child process writes data into its stdout or stderr
        pipe. fd is the integer file descriptor of the pipe. data is a non-empty
        bytes object containing the data.
        """
        logging.debug("**************** pipe_data_received ****************")

    def pipe_connection_lost(fd, exc):
        """Called when one of the pipes communicating with the child process is
        closed. fd is the integer file descriptor that was closed.
        """
        logging.debug("!!!!! PIPE CONNECTION LOST: {} {}".format(fd, exc))

    def process_exited():
        logging.debug("**************** process_exited ****************")

    # --------------------|
    # process_message    |
    # --------------------|
    def process_message(self, x):
        """This function does most of the work for the agent and also coordinates
        what all the subprocesses are doing.
        """

        c_out = None

        # Treat anything that doesn't start with bang as a Chunk
        if x[0] != "!":
            try:
                c_in = Chunk.init_from_packet(x)
                logging.debug("Chunk from {}, type {}".format(c_in.s, c_in.t))
                # TODO: self.tic = c_in.k
            except:
                logging.error("   -=-=-=-=- Had error in Chunk.init_from_packet -=-=-=-=-")

            # subprocess sent last action chunk marker, so mark that one complete
            if c_in.t == Chunk.CT_END:
                logging.debug("***** Got last action chunk marker for {} *****".
                              format(c_in.s))

                reset_flag(c_in.s)

                # If both are done, select an action then clear the list
                cycle_pa_loop()

                # Nothing is sent out now; that happens for all subprocesses and is
                # handled by cycle_pa_loop.

            # The subprocess has sent an action chunk.
            elif ((c_in.t == Chunk.CT_EXT_ACTION) or
                  (c_in.t == Chunk.CT_WM_ACTION) or
                  (c_in.t == Chunk.CT_GS_ACTION)):

                # not the last action chunk, so accumulate it and keep going.
                logging.debug("Got an action recommendation")
                action_recs.append(c_in)
                c_out = Chunk('Agent-', Chunk.CT_ACK, "AGENT", c_in.s, c_in.k)

            elif c_in.t == Chunk.CT_READY:
                random_PA_sleep()

                reset_flag(c_in.s)

                # If both are done, select an action then clear the list
                cycle_pa_loop()

            # The subprocess is connecting for the first time.
            elif c_in.t == Chunk.CT_JOIN:
                subprocesses[self.rport] = c_in.s
                transports[c_in.s] = self.transport
                c_out = Chunk('Agent-', Chunk.CT_JOINED, "AGENT", c_in.s, c_in.k)

            # The subprocess is acknowledging it's received the DIE command.
            elif c_in.t == Chunk.CT_DYING:
                pass

            else:
                pass

            if c_out != None:
                return json.dumps(c_out.__dict__)
            else:
                return None

        # Strings that start with bang are immediate commands. There are very few
        # of these, eventually maybe none.

        elif x == "!DIE":
            # close the socket
            rport = (self.transport.get_extra_info("peername"))[1]
            logging.debug("This guy is checking out: {}".format(rport))

            self.transport.close()
            # NO!  self.terminate = True

    def update_fsm(self, x):
        """Main manager for the entire agent_process state machine. Call this
        after every packet received from any subprocess.

        Changes the content of self.message as its main side effect.
        TODO: Use a return?
        """

        """
        if x.startswith("ACS"):
            self.message = "PARAMS"

        if x.startswith("JOIN"):
            self.message = "PARAMS"

        elif x.startswith("OK_PARAMS"):
           self.message = "DIMS"

        elif x.startswith("OK_DIMS"):
           self.message = "FILES"

        elif x.startswith("OK_FILES"):
           self.message = "CHUNK"

        elif x.startswith("OK_CHUNK"):
           self.message = "CHUNK"

        elif x.startswith("DONE"):
            self.message = "DONE"

        """


class AgentSimProtocol(asyncio.SubprocessProtocol):
    """Main protocol handler by which this agent communicates with the
    simulation itself. This class is the master message broker for the agent
    with regards how it gets controlled by the simulation and is NOT the
    protocol by which the agent communicates with its subprocesses.
    """

    def __init__(self):
        super(AgentSimProtocol, self).__init__()

        self.ccount = 0
        self.retries = 0
        self.terminate = False

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        logging.info('connection from {}'.format(peername))
        self.sim_transport = transport
        self.rsimport = (self.sim_transport.get_extra_info("peername"))[1]

        # Note that all meta-commands that aren't chunks must start with '!'
        self.sim_transport.write("!Welcome".encode())

    def data_received(self, data):
        x = data.decode()
        # DEBUG # print('--RCVD FROM SIMULATION--: {}'.format(x))
        logging.info('--RCVD FROM SIMULATION--: {}'.format(x))

        msg = self.process_message(x)

        if msg != None:
            logging.debug("--SENT--: {}".format(msg))
            # DEBUG #  print("--SENT--: {}".format(msg))

            try:
                self.sim_transport.write(msg.encode())
            except:
                # This appears to happen because of what's going on in Simulation
                logging.debug("**************** GOT NULL DATA **************** {}".format(x))

    def eof_received(self):
        logging.debug("**************** eof_received ****************")

    def process_exited():
        logging.debug("**************** process_exited ****************")

    # --------------------|
    # process_message    |
    # --------------------|
    def process_message(self, x):
        """This function deals with messages received from the Simulation.
        """

        c_out = None

        # Treat anything that doesn't start with bang as a Chunk
        if x[0] != "!":
            try:
                c_in = Chunk.init_from_packet(x)
                logging.debug("Chunk from {}, type {}".format(c_in.s, c_in.t))
            except:
                logging.error("   -=-=-=-=- Had error in Chunk.init_from_packet -=-=-=-=-")

                """
                Simulation sends these:
                    CT_AGENT_JOINED = 62  # The Simulation responds to a successful join
                    CT_AGENT_RUN_SS = 64  # Simulation tells agent to do one P/A cycle
                    CT_AGENT_RUN = 65     # Simulation tells agent to run N rounds
                    CT_AGENT_SI = 72      # The SI chunk requested by the Agent
                    CT_AGENT_DIE = 66     # Subprocess commands an Agent to terminate
                    CT_AGENT_DYING = 67   # Agent ACKs the DIE command and starts shutting down
                    CT_AGENT_DEAD = 68    # Agent is about to close conn and terminate
                """

            # Simulation sent in the requested SI. ACK it and do another P/A cycle.
            if c_in.t == Chunk.CT_AGENT_SI:
                logging.debug("***** Got SI chunk from Simulation. *****")

                # TODO:
                main_cycle_pa_loop()

                # Make sure Chunk is good and ACK it.
                # TODO:

            # Simulation tells agent to do a round:
            elif c_in.t == Chunk.CT_AGENT_RUN_SS:
                # TODO: Not fully set up
                c_out = Chunk('Agent-', Chunk.CT_AGENT_GET_SI, "AGENT", c_in.s, c_in.k)

            elif c_in.t == Chunk.CT_AGENT_RUN:
                # TODO: Not fully set up
                # THIS WILL BE SOME SORT OF LOOP WITHIN THE FSM
                c_out = Chunk('Agent-', Chunk.CT_AGENT_GET_SI, "AGENT", c_in.s, c_in.k)

            # The subprocess is connecting for the first time.
            elif c_in.t == Chunk.CT_AGENT_JOINED:
                subprocesses[self.rport] = c_in.s
                transports[c_in.s] = self.transport
                c_out = Chunk('Agent-', Chunk.CT_JOINED, "AGENT", c_in.s, c_in.k)

            # The subprocess is acknowledging it's received the DIE command.
            elif c_in.t == Chunk.CT_AGENT_DIE:
                pass

            else:
                pass  # Should never get here

            if c_out != None:
                return json.dumps(c_out.__dict__)
            else:
                return None

        # Strings that start with bang are immediate commands. There are very few
        # of these, eventually maybe none.

        elif x == "!DIE":
            # close the socket
            logging.debug("This guy is checking out: {}".format(rport))

            self.transport.close()
            # NO!  self.terminate = True


class AgentProcess(object):
    """The master process for a single Clarion agent. It communicates with all
    the agent's subprocesses (via its AgentProtocol), while it itself
    communicates with the Simulation process via a separate socket connection.

    At launch it is given only the full path to the agent context file. It
    finds everything it needs there.
    """
    MAX_RETRIES = 20

    def __init__(self, aname, acp):
        """Does the following:
        -- Opens the passed-in pcontext file
        -- Gets the asyncio loop
        -- starts the socket listener that services the subprocesses
        -- connects to the Simulation and awaits commands
         """

        self.ac_path = acp
        self.tic = -1  # REVISIT

        try:
            self.context = AgentContext(aname)
            self.context.load_agent_context(acp)
            self.sim_host = self.context.sim_host
            self.sim_port = self.context.sim_port
            logging.info("Simulation host and port are {}:{}".format(self.sim_host, self.sim_port))
        except:
            logging.error("Could not open agent_context.")
            exit(1)

        # TODO: Set up the Perception/Action state machine for this agent.

        # Just to make sure agent context is OK:
        # print(self.context.sim_host, self.context.sim_port)

        try:
            self.loop, error = asyncio_api.get_asyncio_loop()
            logging.debug(">>>>>>>>>>> Subprocess loop {}".format(id(self.loop)))

        except:
            # TODO: Do a better job with failure case
            logging.info("Could not obtain an asyncio loop.")
            exit(2)

        try:
            # Get an unassigned port for the agent_process socket listener
            self.server, error = asyncio_api.prepare_socket_listener(
                self.loop, AgentProtocol)

            logging.info("Got socket_listener {}".format(
                self.server.sockets[0].getsockname()))

            self.listener_host = self.server.sockets[0].getsockname()[0]
            self.listener_port = self.server.sockets[0].getsockname()[1]

            # print (self.listener_host, self.listener_port)
        except:
            # TODO: Do a better job with failure case
            logging.info("Could not obtain an agent_process socket listener.")
            exit(3)

        self.connect_to_simulation()

    def connect_to_simulation(self):
        """Attempts to connect to the master Simulation process via the
        previously obtained ipaddr and port number for the Simulation itself.
        Uses the AgentSimProtocol and the Simulation's IP addr and port num.
        """

        """
        # We should use the loop we have
        try:
            logging.debug("--------------------------------------------")
            logging.debug("Getting loop for the Simulation connection.")
            if os.name == 'nt':
                logging.debug("running on Windows, I see...")
                self.loop = asyncio.ProactorEventLoop()
                asyncio.set_event_loop(self.loop)
            else:   
                self.loop = asyncio.get_event_loop()

            logging.debug(">>>>>>>>>>> Simulation loop {}".format(id(self.loop)))

        except Exception as e:
            logging.debug("Could not get a loop for the Simulation connection.")
        """

        logging.debug(">>>>>>>>>>> Simulation loop {}".format(id(self.loop)))

        # Playing with socket connections
        try:
            logging.info("Attempting to connect to the Simulation running at {}:{}".format(
                self.sim_host, self.sim_port))

            logging.debug("Trying to create connection to Simulation")
            # self.coro = self.loop.create_connection(ActionCenteredSubsystem, '127.0.0.1', 8888)
            # logging.debug("Got the coroutine")
            # self.trans, self.prot = self.loop.create_connection(asyncio.SubprocessProtocol, '127.0.0.1', 8888)

            try:
                self.coro = self.loop.create_connection(AgentSimProtocol,
                                                        self.sim_host, self.sim_port)  # ipaddress.ip_address()
            except Exception as ee:
                logging.debug("Failed at the create_connection coroutine (to Simulation)")

            logging.debug("Back from create_connection (to Simulation)")

            self.loop.run_until_complete(self.coro)
            logging.debug("Back from the Future")
            self.loop.run_forever()
            # self.loop.close()
        except Exception as e:
            logging.debug("Could not get a connection to the Simulation.")

    @asyncio.coroutine
    def launch_acs_process(self, *args):
        try:
            logging.info("Inside launch_acs_process")
            # logging.info("...launch_acs_process args: {}".format(*args))
            print("...launch_acs_process args:", *args)
            # time.sleep(4)
            self.acs_proc = yield from asyncio.create_subprocess_exec(
                *args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
            time.sleep(1)
            logging.info("...The ACS process is: {}".format(self.acs_proc))
            return 0
        except Exception as e:
            print("Exception!")
            return e

    @asyncio.coroutine
    def launch_idn_process(self, *args):
        try:
            logging.info("Inside launch_idn_process")
            # logging.info("...launch_idn_process args: {}".format(*args))
            print("...launch_idn_process args:", *args)
            time.sleep(1)
            self.idn_proc = yield from asyncio.create_subprocess_exec(*args,
                                                                      stdin=subprocess.PIPE,
                                                                      stdout=subprocess.PIPE,
                                                                      stderr=subprocess.STDOUT)

            time.sleep(1)
            logging.info("...The IDN process is: {}".format(self.idn_proc))
            return 0
        except Exception as e:
            print("Exception!")
            return e

    # TODO: Unproven, not tested yet
    @asyncio.coroutine
    def launch_any_process(self, ipaddr, port):
        try:
            print("launch_any_process: starting")
            print("launch_any_process: ", *args)
            print("%s %d", ipaddr, port)

            # time.sleep(4)
            proc = yield from asyncio.create_subprocess_exec(ipaddr,
                                                             port,
                                                             stdout=subprocess.PIPE,
                                                             stderr=subprocess.STDOUT)

            time.sleep(1)
            return proc, None

        except Exception as e:
            print("Exception!")
            return None, e

    def launch_subprocesses(self):
        """This method launches the various subprocessing belonging to the
        agent in strict order. As each is launched, it communicates back to this
        process.
        """

        # TODO: Need descriptors and a better way to do this!

        logging.info("Entering launch_subprocesses()...")

        try:
            logging.info("Trying to launch the ACS process")

            coro_acs_ = self.launch_acs_process(sys.executable,
                                                self.context.clarion_path + "/agent/acs_process.py",
                                                '127.0.0.1',
                                                str(self.listener_port),
                                                self.ac_path)
        except Exception as e:
            logging.error("Could not launch the ACS process, {}".format(e))

        logging.info("... Did launch of ACS...")
        exitcode = self.loop.run_until_complete(coro_acs_)

        # TODO: Doesn't like the conversion
        # FIX: logging.info("Back from the launch call with exitcode...", str(exitcode))
        logging.info("!!! Back from the ACS launch call")

        try:
            logging.info("Trying to launch the IDN process")

            coro_idn = self.launch_idn_process(sys.executable,
                                               self.context.clarion_path + "/agent/idn_process.py",
                                               '127.0.0.1',
                                               str(self.listener_port),
                                               self.ac_path)
        except Exception as e:
            logging.error("Could not launch the IDN process, {}".format(e))

        logging.info("... Did launch of IDN...")
        exitcode = self.loop.run_until_complete(coro_idn)

        # TODO: Doesn't like the conversion
        # FIX: logging.info("Back from the launch call with exitcode...", str(exitcode))
        logging.info("!!! Back from the IDN launch call")

        # At the end of all this, get the main loop going.

        try:
            logging.info("Entering run_forever()...")

            self.loop.run_forever()
        except KeyboardInterrupt:
            logging.info("exit")
        finally:
            server.close()
            self.loop.close()

    def tic_value(self):
        return self.tic

    def advance_tic(self):
        self.tic += 1
        return self.tic

    def generate_random_si_chunk(self, receiver):
        c = Chunk("Agent-", Chunk.CT_SI, "AGENT", receiver, agent.tic_value())

        for dname in self.context.dimensions:
            dim = self.context.dimensions[dname]
            dvp = dim.generate_random_dvpair()
            c.set_dvpair(dvp[0], dvp[1])

        return c


if __name__ == '__main__':
    """Because this is launched as a separate process, the code below does get
    executed as if it were an ordinary launch.
    """

    # Must be handed the full path to a well-formed agent context json file.
    if len(sys.argv) >= 2:
        ac_path = sys.argv[1]
    else:
        exit(1)

    # Isolate agent name and start logging
    aname = utilities.extract_agent_name(ac_path)
    print(aname)
    print(os.getcwd())

    # Local logging file just for agent process, written fresh each time
    # logging.basicConfig(filename='agent.log', filemode='w', level=logging.DEBUG)
    # logger = logging.getLogger(__name__)

    logging.basicConfig(filename=aname + '.log', level=logging.DEBUG, filemode='w',
                        format='%(asctime)-15s %(module)s: %(levelname)s: %(message)s')

    random_PA_sleep()

    print("Starting Agent '{}' using {}".format(aname, ac_path))
    logging.info("Starting Agent '{}' using {}".format(aname, ac_path))

    agent = AgentProcess(aname, ac_path)

    print(agent.listener_host)
    print(agent.listener_port)

    # chnk = agent.generate_random_si_chunk("ACS")
    # print(chnk)

    set_flags()

    """
    # Debug code for dealing with waiting for subprocs to respond.
    set_flags()
    print(acs_flag, idn_flag)
    test = Chunk("ACS-", Chunk.CT_READY, "ACS", "AGENT", 123)
    print(test.s)
    reset_flag(test.s)
    print(acs_flag, idn_flag)
    idn_flag = 0
    print(acs_flag, idn_flag)
    set_flags()

    print(transports)
    transports["ACS"] = 'HAPPY'
    transports["IDN"] = 'SAD'
    print(transports)
    """

    logging.info("Starting AgentProcess...")

    agent.launch_subprocesses()
