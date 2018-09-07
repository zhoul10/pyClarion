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
import os
import json
import random
import time
import logging
import pprint
import itertools

from clarion.core.dimension import Dimension, DimensionDict
from clarion.core.utilities import is_sequence 

"""
from pybrain.tools.shortcuts import buildNetwork
from pybrain.structure import TanhLayer
from pybrain.structure import SigmoidLayer
from pybrain.structure import SoftmaxLayer
from pybrain.supervised.trainers import BackpropTrainer
"""

# DEBUG # print (sys.path)

# P34: all the __init__ files in pybrain need the dot operator added in the from clauses
import pybrain

# TODO: For some reason, not finding the SimpleConvolutionalNetwork
from pybrain.structure.networks.convolutional import SimpleConvolutionalNetwork

logger = logging.getLogger(__name__)

# This is the entire set of network types in PyBrain. The ones commented out are 
# ones in the PyBrain library that for some reason are not getting picked up.

# TODO: more of the handy PyBrain shortcutting needs to be done with these.

# missing networks: NeuronDecomposableNetwork
network_types = {
    "FEEDFORWARD" : pybrain.FeedForwardNetwork,
    "BACKPROP" : pybrain.FeedForwardNetwork,
    "BACKPROPAGATION" : pybrain.FeedForwardNetwork,
    "Q-LEARNING" : pybrain.FeedForwardNetwork,      # TODO: was set to none ...
    "SQ-LEARNING": pybrain.FeedForwardNetwork,
    "HOPFIELD": pybrain.RecurrentNetwork,
    "RECURRENT": pybrain.RecurrentNetwork,          # TODO: was set to None before?
    "BIDIRECTIONAL": pybrain.BidirectionalNetwork,
    #"MULTIDIMENSIONALRNN" : pybrain.MultiDimensionalRNN,
        # from pybrain.structure.networks.multidimensional import MultiDimensionalRNN
        # set to MultiDimensionalRNN not pybrain.MultiDimensionalRNN
        # TODO: fix __init__.py file in /usr/local/lib/python3.4/site-packages/PyBrain-0.3.3-py3.4.egg/pybrain/structure/networks
    #"MULTIDIMENSIONALLSTM": pybrain.MultiDimensionalLSTM,
        # from pybrain.structure.networks.multidimensional import MultiDimensionalLSTM
        # set to MultiDimensionalLSTM not pybrain.MultiDimensionalLSTM
        # TODO: fix __init__.py file in /usr/local/lib/python3.4/site-packages/PyBrain-0.3.3-py3.4.egg/pybrain/structure/networks
    #"ACCUMMDRNN" : pybrain.MultiDirectionalMdrnn,
    #"ACCUM-MDRNN" : pybrain.MultiDirectionalMdrnn,
        # from pybrain.structure.networks.mdrnn import _MultiDirectionalMdrnn
        # set to _MultiDirectionalMdrnn not pybrain._MultiDirectionalMdrnn
        # TODO: fix __init__.py file in /usr/local/lib/python3.4/site-packages/PyBrain-0.3.3-py3.4.egg/pybrain/structure/networks
    "SWIPING": pybrain.SwipingNetwork,
    "BORDERSWIPING" : pybrain.BorderSwipingNetwork,
    #"CONVOLUTION" : pybrain.SimpleConvolutionalNetwork,
    #"CONVOLUTIONAL" : pybrain.SimpleConvolutionalNetwork,
        # from pybrain.structure.networks.convolutional import SimpleConvolutionalNetwork
        # set to SimpleConvolutionalNetwork not pybrain.SimpleConvolutionalNetwork
        # TODO: fix __init__.py file in /usr/local/lib/python3.4/site-packages/PyBrain-0.3.3-py3.4.egg/pybrain/structure/networks
    "CUSTOM" : None
}

# This is the entire set of layer types in PyBrain. The ones commented out are 
# ones in the PyBrain library that for some reason are not getting picked up.

module_types = {
    "GAUSSIAN" : pybrain.GaussianLayer,
    "LINEAR" : pybrain.LinearLayer,
    "MDRNN" :  pybrain.MdrnnLayer,
    "RELU" : pybrain.ReluLayer,
    #"SAMPLE" : pybrain.SampleLayer,
        # from pybrain.structure.modules.samplelayer import SampleLayer
        # set to SampleLayer not pybrain.SampleLayer
        # TODO: fix __init__.py file in /usr/local/lib/python3.4/site-packages/PyBrain-0.3.3-py3.4.egg/pybrain/structure/modules
    #"BERNOULLILAYER" : pybrain.BernoulliLayer,
        # from pybrain.structure.modules.samplelayer import BernoulliLayer
        # set to BernoulliLayer not pybrain.BernoulliLayer
        # TODO: fix __init__.py file in /usr/local/lib/python3.4/site-packages/PyBrain-0.3.3-py3.4.egg/pybrain/structure/modules
    "SIGMOID" : pybrain.SigmoidLayer,
    "STATEDEPENDENT" : pybrain.StateDependentLayer,
    "TANH" : pybrain.TanhLayer,
    "MULTIPLICATION" : pybrain.MultiplicationLayer,
    "GATE" : pybrain.GateLayer,
    "DOUBLEGATE" : pybrain.DoubleGateLayer,
    "SWITCH" : pybrain.SwitchLayer,
    "LSTM" : pybrain.LSTMLayer,
    "MDLSTM" : pybrain.MDLSTMLayer,
    "SOFTMAX" : pybrain.SoftmaxLayer,
    "PARTIALSOFTMAX" : pybrain.PartialSoftmaxLayer
    #"SOFTSIGNLAYER" : pybrain.SoftSignLayer,
        # from pybrain.structure.modules.softsign import SoftSignLayer
        # set to SoftSignLayer not pybrain.SoftSignLayer
        # TODO: fix __init__.py file in /usr/local/lib/python3.4/site-packages/PyBrain-0.3.3-py3.4.egg/pybrain/structure/modules
}


# This is the entire set of connection types in PyBrain. The ones commented out are 
# ones in the PyBrain library that for some reason are not getting picked up.

connection_types = {
    "FULL" : pybrain.FullConnection,
    "IDENTITY" : pybrain.IdentityConnection,
    "SHAREDFULL" : pybrain.SharedFullConnection,
    "SHARED" : pybrain.SharedConnection,
    "LINEAR" : pybrain. LinearConnection,
    "FULLNOTSELF" : pybrain.FullNotSelfConnection,
    #"PERMUTATION" : pybrain.PermutationConnection,
        # fix for Permutation
        #   from pybrain.structure.connections.permutation import PermutationConnection
        #   then set to PermutationConnection not pybrain.PermutationConnection
        #   TODO: fix __init__.py file in /usr/local/lib/python3.4/site-packages/PyBrain-0.3.3-py3.4.egg/pybrain/structure/connections
    #"SUBSAMPLING" : pybrain.SubsamplingConnection,
        # fix for Subsampling
        #   from pybrain.structure.connections.subsampling import SubsamplingConnection
        #   then set to SubsamplingConnection not pybrain.SubsamplingConnection
        #   TODO: fix __init__.py file in /usr/local/lib/python3.4/site-packages/PyBrain-0.3.3-py3.4.egg/pybrain/structure/connections
    #"SHAREDSUB" : pybrain.SharedSubsamplingConnection
        # fix for Sharedsub
        #   from pybrain.structure.connections.shared import SharedSubsamplingConnection
        #   then set to SharedSubsamplingConnection not pybrain.SharedSubsamplingConnection
        #   TODO: fix __init__.py file in /usr/local/lib/python3.4/site-packages/PyBrain-0.3.3-py3.4.egg/pybrain/structure/connections
}

class ClarionNeuralNet(object):
    """Abstract class for wrapping a PyBrain neural net object () with the 
    other items needed by Clarion itself.
    """
    def __init__(self):
        super(ClarionNeuralNet, self).__init__(self)
        pass

class ClarionFeedforwardNetwork(pybrain.structure.networks.Network, ClarionNeuralNet): 
    """Class for wrapping a PyBrain Feedforward neural net object with the 
    other items needed by Clarion itself.
    """
    def __init__(self):
        super(ClarionNeuralNet, self).__init__(self)
        pass

class ClarionRecurrentNetwork(pybrain.structure.networks.Network, ClarionNeuralNet): 
    """Class for wrapping a PyBrain Recurrent neural net object with the 
    other items needed by Clarion itself.
    """
    def __init__(self):
        super(ClarionNeuralNet, self).__init__(self)
        pass

class NetworkList (list):
    """Contains the dependency-ordered collection of PyBrain neural nets
    owned by a Clarion subsystem.  This is a list, not a dictionary, because
    running through the nets must be done in dependency order.
    """
    def __init__(self):
        super(NetworkList, self).__init__(self)
        pass

    def append(self, net):
        pass

def collect_networks(jcontext, netdict):
    """Copies out each network item in "Networks" in a JSON file into a dict 
    for later processing.  All JSON files have to be processed before the 
    dependency order can be determined.
    """
    try:
        if "idn_networks" in jcontext:
            #print (jcontext["Networks"])
            netnames = jcontext["idn_networks"].keys()
            for netname in netnames:
                net = jcontext["idn_networks"].get(netname)
                netdict[netname] = net
    except Exception as e:
        pass  

def determine_node_counts(dims, onenet):
    return 5, 5

def determine_dependencies(dims, netdescs):
    """Returns a partially ordered list of the names of the networks beginning
    with those that have no dependencies, on out. (Networks then have to be
    added to the process in that order.)
    """
    try:
        dependent = False
        nnames_so_far = list()          # P34: Had to change from []
        still_to_do = list()            # P34: Had to change from []
        found_so_far = dims.dimnames()

        still_to_do = list(netdescs.keys()) # P34: Had to cast to a list
        #TODO change idn_network to variable
        #TODO add label in json
        while len(still_to_do) > 0:
            for netname in still_to_do:
                # get the name of the network
                net = netdescs[netname]
                
				# get the inputs in network
                inputs = []
                input_modules = net.get("input_modules")
                input_layers = []
                for il in input_modules:
                    input_layers.append(il)
                for i in input_layers:
                    inputs.append(i)

                # get the outputs in network
                outputs = []
                output_modules = net.get("output_modules")
                output_layers = []
                for ol in output_modules:
                    output_layers.append(ol)
                for o in output_layers:
                    outputs.append(o)

                dependent = False

                # get the nodes in each input layer
                nodes = []
                for il in inputs:
                    for i in il:
                        nodes.append(i.get("nodes"))

                # flattening the list:
                chain = itertools.chain(*nodes)
                nodes = (list(chain))

                for nodename in nodes:
                    # DEBUG # print (type(nodename) is list)
                    if type (nodename) is list: dimname = nodename[0]
                    else: dimname = nodename

                    if not dimname in found_so_far: dependent = True
                # get the nodes in each output layer
                nodes = []
                for ol in outputs:
                    for o in ol:
                        nodes.append(o.get("nodes"))
                chain = itertools.chain(*nodes)
                nodes = (list(chain))
                for nodename in nodes:
                    if type (nodename) is list: dimname = nodename[0]
                    else: dimname = nodename

                    if not dimname in found_so_far: dependent = True
                
                if dependent == False:
                    nnames_so_far.append(netname)
                    found_so_far.append(netname)
                    still_to_do.remove(netname)


        return nnames_so_far

    except Exception as e:
        pass          


class PyNet():
    '''
        class to store the network information and dictionary for layer node information
    '''
    def __init__(self):
        self.net = None             # maybe change this to Network? leaving as this may cause errors, although those errors may be good
        self.nodes = {}             # a dictionary of dictionaries containing the nodes

        # TODO::: NEED TO CREATE AN ARRAY OF DICTIONARIES OF DICTIONARIES
    def add_nodes(self, name, new_nodes):
        # Function to add new nodes into dictionary of nodespyt
        self.nodes[name] = new_nodes



class PyclarionNetwork():
    '''
        class to store the parsed data
    '''
    def __init__(self, name, type):
        self.connections    = []
        self.input_modules  = []     # list of input modules (list of input layers (list of inputs))
        self.output_modules = []     # list of output modules (list of output layers (list of outputs))
        self.hidden_layers  = []     # list of hiddens
        self.name = name
        self.type = type
    def add_connection(self, new_conn):
        self.connections.append(new_conn)

    def add_input_layer(self, new_in_layer):
        self.input_modules.append(new_in_layer)

    def add_output_layer(self, new_out_layer):
        self.output_modules.append(new_out_layer)

    def add_hidden(self, new_hidden):
        self.hidden_layers.append(new_hidden)

    def print_debug(self):
        print(self.name, '\n',
                "TYPE: ", self.type, '\n',
                "INPUTS: ", self.input_modules, '\n',
                "OUTPUTS: ", self.output_modules, '\n',
                "HIDDEN: ", self.hidden_layers, '\n',
                "CONNECTIONS: ", self.connections)

def parse_networks(dims, ordered_nets, net_dict):
    '''
    Parses JSON  into usable class
    :param dims:
    :param ordered_nets:
    :param net_dict:
    :return:
    '''
    # net_dict is the list of idn nets
    net_list = []
    for net in ordered_nets:
        try:
            pyc_net = PyclarionNetwork(net, net_dict[net]["type"])
        except:
            pyc_net = PyclarionNetwork(net, "BACKPROP")
        try:
            pyc_net.connections = (net_dict[net]["connections"])
        except:
            pyc_net.connections = []

        for im in net_dict[net]["input_modules"]:
            pyc_net.add_input_layer(im)
        for om in net_dict[net]["output_modules"]:
            pyc_net.add_output_layer(om)
        for h in net_dict[net]["hidden_modules"][0]:
            pyc_net.add_hidden(h)

        net_list.append(pyc_net)

    return net_list

def build_network(dims, net):
    '''
    Building a network
    :param dims:
    :param net:
    :return:
    '''

    # TODO
        # build input nodes dictionary
        # build output nodes dictionary
        # add weights to the connections

    # NOTE
        # future bug possible if layers are named the same in the JSON
            # may need to sanitize JSON input
            # or add some sort of index number

    # create network in PyBrain
    newnet = PyNet()
    try:
        newnet.net = network_types[net.type.upper()](net.name)
    except:
        newnet.net = network_types[net.type.upper()]
    print("NEW NET\n-------\n", newnet.net)

    # adding all the input stuff
    # TODO: add to dictionary
    all_layers = {}
    print(net.name, net, net.input_modules)
    for il in net.input_modules:
        for i in il:
            # add nodes to dictionary
            temp_dict = {}
            for index, node in enumerate(i["nodes"]):
                temp_dict[node] = index
            newnet.add_nodes(i["name"], temp_dict)

            print("SIZE: ", len(i["nodes"])) # add these to an input layer, check type of input and create/add layer
            in_layer = module_types[i["type"].upper()](len(i["nodes"]))
            all_layers[i["name"]] = in_layer
            print(in_layer)
            newnet.net.addInputModule(in_layer)
            # if nodes is list, do thing
    # debug
    print("nodes XXX: ", newnet.nodes)


    # adding all the output stuff
    # TODO: add to dictionary
    print(net.name, net, net.output_modules)
    for ol in net.output_modules:
        for o in ol:
            # add nodes to dictionary
            temp_dict = {}
            for index, node in enumerate(o["nodes"]):
                temp_dict[node] = index
            newnet.add_nodes(o["name"], temp_dict)

            out_layer = module_types[o["type"].upper()](len(o["nodes"]))
            all_layers[o["name"]] = out_layer
            print(out_layer)
            newnet.net.addOutputModule(out_layer)
            # if nodes is list, do thing

    # Debug
    print("nodes XXX: ", newnet.nodes)

    # add the hidden stuff here
    hidden_layers = {}  # maybe rename this, poor naming convention w/ scoping TODO
    for h in net.hidden_layers:
        hidden_layer = (module_types[h["type"].upper()](h["count"]))
        all_layers[h["name"]] = hidden_layer
        print(hidden_layer)
        newnet.net.addModule(hidden_layer)

    # add the connections here
    # TODO add weights
    for c in net.connections:
        print(c)
        # connection type from dictionary( from ala JSON, to ala JSON )
        conn = connection_types[c["type"].upper()](all_layers[c["from"]], all_layers[c["to"]])
        print(conn)
        newnet.net.addConnection(conn)

    # finish up
    newnet.net.sortModules()
    print(newnet.net)

    # debug stuff to make sure the same when returned. printing the connections
    for mod in newnet.net.modules:
        for conn in newnet.net.connections[mod]:
            print(conn)
            for cc in range(len(conn.params)):
                print(conn.whichBuffers(cc), conn.params[cc])
    return newnet


def build_neural_net_from_desc(dims, nname, onenet, netnames):
    """
    Builds a Pybrain neural net based on the descriptor collected previously
    from the JSON file(s). This builds ONE net, so call multiple times for
    multiple nets.  Note that the DimensionDict must already have been set up  
    and available here.

    Returns a fully-built PyBrain network object or else none if errors.
    Second returned item is the error text itself (empty if successful).
    """

    def parse_node_subset(dim, entry):
        """Parses a sub-setted list of nodes for a particular dimension. 
        entry is in the form:
            [<dimname>, start, end] for doing a range, or else
            [<dimname>, [ list of values ]]
        if the latter, list of values can be ints, which are the actual
        indices into the vector of values, or the actual names of those values.

        TODO: NOT YET, only indices are getting picked up at the moment.

        Returns a tuple of dim_value indices and their munged names.
        """
        if is_integer(entry[1]) and is_integer(entry[2]) and len(entry)==3:
            return dim.get_node_vector_range(entry[1], entry[2])
        elif type (entry[1]) is list:
            return dim.get_node_vector_subset(entry[1])

    def parse_node_collection(dims, nlist, isInput):
        """Given a piece of JSON that is a list of nodes or subsets of node,
        constructs the vector of nodes per dimension as a list.
        """
        vecs = []

        for node in nlist:
            if type (node) is list:
                nodename = node[0]
                d = dims.has_dim(nodename)
                nodevec = parse_node_subset(d, node)
            
            elif dims.has_dim(node):
                nodename = node
                d = dims.has_dim(nodename)
                nodevec = d.get_node_vector()
               
            vecs.append(nodevec)

        return vecs

    def parse_hidden(h, suffix=None):
        if "name" in h: hn = h["name"]
        else: 
            if suffix != -1: hn = "hidden" + suffix
            else: hn = "hidden"

        if "count" in h: hc = int(h["count"])
        else: 
            hc = 0
            hn = "***BAD***"

        if "type" in h: ht = h["type"]
        else: ht = "SIGMOID"

        return hn, hc, ht

    def parse_connection(c, suffix=None):
        if "name" in c: cn = h["name"]
        else: cn = "conn" + suffix

        if "from" in c: cfrom = c["from"]
        else: cn = "***BAD***"

        if "to" in c: cto = c["to"]
        else: cn = "***BAD***"

        if "type" in c: ct = c["type"].upper()
        else: ct = "SIGMOID"

        return cn, cfrom, cto, ct

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    #  Code starts here
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

    newnet = None
    input_node_vecs = []
    output_node_vecs = []

    if "type" in onenet: t = (onenet["type"]).upper()
    else: t = "BACKPROP"

    # TODO - Probably going away
    in_nodecount, out_nodecount = determine_node_counts(dims, onenet)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    # Build the vector of input nodes
    if "input" in onenet: in_dict = onenet["input"]
    else: return None, "No input layer supplied for " + nname
   
    if "nodes" in in_dict: nodes = in_dict["nodes"]
    else: return None, "No nodes found for input dimensions for " + nname

    try:
        input_node_vecs = parse_node_collection(dims, nodes, True)
    except Exception as e:
        return None, "Error parsing input layer dimensions for " + nname

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    # Build the vector of output nodes
    if "output" in onenet: out_dict = onenet["output"]
    else: return None, "No output layer supplied for " + nname

    if "nodes" in out_dict: nodes = out_dict["nodes"]
    else: return None, "No nodes found for output dimensions for " + nname

    try:
        output_node_vecs = parse_node_collection(dims, nodes, False)
    except Exception as e:
        return None, "Error parsing output layer dimensions for " + nname

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    # Determine type of network. This establishes the correct initial form of
    # network before adding things to it.

    newnet = network_types[t](name=nname)

    # TODO: Refactor the following sections

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    # Add one (or more) input layers to the network

    if "type" in in_dict:  in_type = (in_dict["type"]).upper()
    else: return None, "No input layer type supplied for " + nname

    if "bias" in in_dict: in_bias = in_dict["bias"]
    else: in_bias = False

    nodes = in_dict["nodes"]    # only using this to capture dim names for the input laywe
    indx = 0                    # TODO: Kind of hacky here
    try:
        for node in input_node_vecs:
            in_module = module_types[in_type](len(node), "in_" + nodes[indx])
            newnet.addInputModule(in_module)
            indx += 1
    except Exception as e:
        return None, "Error constructing input layer for " + nname
 
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    # Add one (or more) output layers to the network

    if "type" in out_dict:  out_type = (out_dict["type"]).upper()
    else: return None, "No output layer type supplied for " + nname

    if "bias" in out_dict: out_bias = out_dict["bias"]
    else: out_bias = False

    nodes = out_dict["nodes"]    # only using this to capture dim names for the output laywe
    indx = 0                    # TODO: Kind of hacky here
    try:
        for node in output_node_vecs:
            out_module = module_types[out_type](len(node), "out_" + nodes[indx])
            newnet.addOutputModule(out_module)
            indx += 1
    except Exception as e:
        return None, "Error constructing output layer for " + nname

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    # Deal with the hidden layer(s)
    #
    # TODO: THIS IS NOT FINISHED!  No support yet for nets having
    #  more than one hidden layer.

    if "hidden" in onenet: 
        hidden = onenet["hidden"]   # This will be an array if more than one hidden layer in use
        try:
            # See if only one hidden layer
            hname, hcount, htype = parse_hidden(hidden, -1)
            
            # Guess not; try parsing as a list of hiddens
            if hname == "***BAD***":
                i = 0
                for h in hidden:
                    hname, hcount, htype = parse_hidden(h, i)
                    if hname == "***BAD***":
                        return None, "Badly formed hidden layer # " + i + " in " + nname    
                    i += 1

        except Exception as e:
            return None, "Unable to parse hidden layer in " + nname   

    else: return None, "No hidden layers specified for " + nname
    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    # Deal with the connections
    #
    # TODO: THIS IS NOT FINISHED!  No support yet for nets having
    #  more than one hidden layer.
    #
    # Types of connections:
    #   FULL        FullConnection (default)
    #   IDENTITY    IdentityConnection
    #   SHAREDFULL  SharedFullConnection
    #   SHARED      SharedConnection
    #   LINEAR      LinearConnection
    #   FULLNOTSELF FullNotSelfConnection
    #   PERMUTATION PermutationConnection
    #   SUBSAMPLING SubsamplingConnection    
    #   SHAREDSUB   SharedSubsamplingConnection

    if "connections" in onenet: 
        conns = onenet["connections"]   # This will be an array if more than one hidden layer in use
        try:
            if type (conns) is list:      # It always should be
                i = 0
                for c in conns:
                    cname, frm, to, ctype = parse_connection(c, i)
                    if cname != "***BAD***":
                        connection_types[ctype](name=nname)
                    else:
                        return None, "Badly formed connection #" + i + " in " + nname
    
                    i += 1
            else:
                return None, "Badly formed connection #" + i + " in " + nname  

        except Exception as e:
            return None, "Unable to parse connections in " + nname   

    else: return None, "No connections specified for " + nname


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    #  Finish up   

    # TODO: modify the following code to be cleaner than it is atm

    if t.startswith("FEEDFORWARD"):
        newnet = pybrain.FeedForwardNetwork(name=nname)

    elif t.startswith("BACKPROP"):
        newnet = pybrain.FeedForwardNetwork(name=nname)

    elif t.startswith("Q-LEARNING"):
        newnet = pybrain.FeedForwardNetwork(name=nname)

    elif t.startswith("SQ-LEARNING"):
        newnet = pybrain.FeedForwardNetwork(name=nname)

    elif t.startswith("HOPFIELD"):
        pass

    elif t.startswith("RECURRENT"):
        pass

    elif t.startswith("BIDIRECTIONAL"):
        newnet = pybrain.BidirectionalNetwork(name=nname)

    elif t.startswith("MULTIMDRNN") or  t.startswith("MULTI-MDRNN"):
        newnet = pybrain._MultiDirectionalMdrnn(name=nname)

    elif t.startswith("ACCUMMDRNN") or t.startswith("ACCUM-MDRNN"):
        newnet = pybrain._MultiDirectionalMdrnn(name=nname)

    elif t.startswith("SWIPING"):
        newnet = pybrain.SwipingNetwork(name=nname)

    elif t.startswith("BORDERSWIPING"):
        newnet = pybrain.BorderSwipingNetwork(name=nname)


    elif t.startswith("CUSTOM"):
        pass

    else:
        logger.error("Unknown network type specified.")
        return None


    return newnet, "OK"

def save_network_to_JSON(net):
    pass

def print_network_report(net):
    pass

def test_pybrain(jpath, dims):
    """Tests the JSON parsing and object construction for PyBrain.  The
    file path passed in should point to a special json test file that 
    flexes all the network creation options.
    """

    netlist = NetworkList()

    try:
        p = os.getcwd() + "/" + jpath
        json_data = open(p)    # TODO: Should probably clean this up
        print ("Was able to open", jpath)
        context = json.load(json_data)
    except Exception as e:
        logger.error("In test_pybrain, file '%s' not found.", p)
        return False
        
    try:
        print ("**********************************")

        nlist = determine_dependencies(dims, context)
        for nname in nlist:
            thenet = build_neural_net_from_json(dims, nname, context["Networks"].get(nname), nlist)
            netlist.append (thenet)

        return netlist

        """
        if "Networks" in context:
            print (context["Networks"])
            nnames= context["Networks"].keys()

            for nname in nnames:
                if nname != "SimpleNet":
                    continue
                build_neural_net_from_json(dims, nname, context["Networks"].get(nname))
        """

    except Exception as e:
        return e            # TODO: improve this