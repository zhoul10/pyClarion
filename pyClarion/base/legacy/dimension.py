from __future__ import absolute_import

#    Clarion Architecture implementation in Python.
#    Copyright (C) 2013-2014  Clarion-Architecture Authors (see AUTHORS.txt)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#   CHANGE HISTORY:
#       12/16/14 - Arthur's final version, committed to repository
#       01/07/15 - (MFL) Added deep_copy() function to DimensionDict.
#       01/07/15 - (MFL) Small style clean-ups.

__author__ = 'Arthur'

import sys
import random
import collections
import logging
import json

# Uncomment to help debug problems with the path
# print(sys.path)

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, MetaData, Column, Integer, Float, String, Boolean, DateTime
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

#  from agentdatabase import Base

Base = declarative_base()


class DimensionEnum:
    """Enum for identifying types of Dimensions."""
    # For some reason, Python gets unhappy if you split this line and don't 
    # use the old-fashioned backslash.
    Nothing, Node, Integer, Float, Double, RangedInt, RangedFloat, RespTime, \
    Sys_TS, Tic_TS, OSC_TS, Max_TS, String, Chunk, Meta = range(15)


DimensionTypes = [
#                                       isInt, isFloat, isTime, hasNodes, hasMinMax, Desc    
(DimensionEnum.Nothing, "Nothing",         False, False, False, False, False, "Placeholder only, do not use"),
(DimensionEnum.Node, "Node",               True,  False, False, True,  False, "Finite set of values mapping to a neural net"),
(DimensionEnum.Integer, "Integer",         True,  False, False, False, False, "Any integer value"),
(DimensionEnum.Float, "Float",             False, True,  False, False, False, "Any floating point value"),
(DimensionEnum.Double, "Double",           False, True,  False, False, False, "Any double precision value"),
(DimensionEnum.RangedInt, "RangedInt",     True,  False, False, True,  True,  "Integer value having a range, maps to a neural net"),
(DimensionEnum.RangedFloat, "RangedFloat", False, True,  False, True,  True,  "Floating point value having a range, maps to a neural net"),
(DimensionEnum.RespTime, "RespTime",       True,  False, True,  False, False, "Response time value, integer milliseconds"),
(DimensionEnum.Sys_TS, "Sys_TS",           False, False, True,  False, False, "Operating system clock time"),
(DimensionEnum.Tic_TS, "Tic_TS",           True,  False, True,  False, False, "Number of P/A Cycles since start"),
(DimensionEnum.OSC_TS, "OSC_TS",           False, False, True,  False, False, "Open Sound Connect (OSC) timestamp"),
(DimensionEnum.Max_TS, "Max_TS",           False, False, True,  False, False, "Max/MSP timestamp"), 
(DimensionEnum.String, "String",           False, False, False, False, False, "any string"),
(DimensionEnum.Chunk, "Chunk",             False, False, False, False, False, "name of a known chunk"),
(DimensionEnum.Meta, "Meta",               False, False, False, False, False, "no given meaning; meaning derived from context"),
]


dimtypelookup = dict()
for dl in DimensionTypes:
    dimtypelookup [(dl[1]).upper()] = dl

def parse_dimension_type(dtstr):
    if dtstr.upper() in dimtypelookup:
        dt = dimtypelookup[dtstr.upper()]
        return dt[0]
    else:  
        return -1


class DimensionMode:
	"""Enum for identifying modes of Dimensions."""
	Nothing, ModeA, ModeB, ModeC = range(4)

# TODO: Placeholder here for a possible DimensionRole 

class Dimension(Base):
    """Database representation of a Dimension, as used in Clarion.
    Note that this defines the Dimension itself and is not a "D/V" Pair.
    """
    __tablename__ = 'dimensions'

    id = Column(Integer, primary_key = True)
    dtype = Column(Integer, nullable=False)
    minval = Column(Float)
    maxval = Column(Float)
    label = Column(String, nullable=False)
    valstring = Column(String, nullable = False)
    mode = Column(Integer, nullable = False)

    def __repr__(self):
        return "<Dimension(id='%s', dtype='%s', minval='%s', maxval='%s', label='%s', valstring='%s', vals='%s')>" % (
            self.id, self.dtype, self.minval, self.maxval, self.label, self.valstring, self.vals)

    def __init__(self, l, t, mode, vals, minval=0, maxval=0, **kwargs):
        #logger.info("Got here")    # uncomment if you really need to debug through this.
        super(Dimension, self).__init__()

        self.label = l      
        self.dtype = t
        self.mode = mode
        self.vals = vals
        self.valstring = json.dumps(vals)
        self.minval = minval
        self.maxval = maxval
        #logger.info("And here")    # uncomment if you really need to debug through this.

        #if "Values" in kwargs: 
        #    self.values = kwargs["Values"]   # TODO: add checking Must be a list or tuple, not a dict
        #else:
        #    self.values = None

        if self.dtype == DimensionEnum.Node:
            self.minval = 0
            self.maxval = len(vals) - 1
        elif self.dtype == DimensionEnum.RangedFloat:
            self.minval = 0.0
            self.maxval = 1.0
        elif self.dtype == DimensionEnum.RangedInt:
            self.minval = 0
            self.maxval = 10

        # TODO: Needs error checking here
        if "minval" in kwargs: 
            self.minval = kwargs["minval"]   # not for Node, String or Chunk types     
        if "maxval" in kwargs: 
            self.maxval = kwargs["maxval"]   # ditto

    def get_node_vector(self):
        """ Returns a list of munged nodenames for setting up a neural net.
        The munging is the dimension name, an underbar, then the name of a value, in 
        succession.  This is only applied to "node" type dimensions, no others.
        """
        i = 0
        l = []
        if self.dtype == DimensionEnum.Node:
            pre = self.label + '_'
            for vn in self.values:
                l.append( (i, (pre + vn),) )
                i += 1
        return l

    def get_node_vector_range(self, lo, hi):
        """ Returns a subset list of munged nodenames, which includes only those
        values in the range lo to hi, inclusive.  The munging is the dimension name, 
        an underbar, then the name of a value, in succession.  This is only applied 
        to "node" type dimensions, no others.
        """
        l = []
        if self.dtype == DimensionEnum.Node:
            pre = self.label + '_'
            # Note that 1 is added to hi since range here is inclusive
            for i in range(lo, hi+1):      # TODO: Error check this
                try:
                    l.append( (i, (pre + self.values[i]),) )
                except Exception as e:
                    return None
        return l
    
    # TODO:
    def get_node_vector_subset(self, entries):
        """ Returns a subset list of munged nodenames, which includes only those
        items listed in the list of entries.  The munging is the dimension name, 
        an underbar, then the name of a value, in succession.  This is only applied 
        to "node" type dimensions, no others.
        """

        """
        l = []

        if self.type == DimensionEnum.Node:
            pre = self.name + '_'
            for i in range(lo, hi):      # TODO: Error check this
                try:
                    l.append(pre + self.values[i])
                except Exception as e:
                    return None
        """
        return get_node_vector()

    def generate_random_dvpair(self):
        """
        Creates a DV Pair tuple from this dimension.

        TODO: Some of these need work.
        """

        if self.dtype == DimensionEnum.Node:
            i = random.randint(0, len(self.vals)-1)
            v = self.vals[i]
        elif self.dtype == DimensionEnum.Integer:    
            v = random.randint() * 1000000    
        elif self.dtype == DimensionEnum.Float:
            v = random.random()
        elif self.dtype == DimensionEnum.Double:
            v = random.random()
        elif self.dtype == DimensionEnum.RangedInt:
            v = random.randint(self.minval, self.maxval)
        elif self.dtype == DimensionEnum.RangedFloat:
            v = random.random() * (self.maxval-self.minval) + self.minval
        elif self.dtype == DimensionEnum.RespTime:
            v = random.random() / 2.0
        elif self.dtype == DimensionEnum.Sys_TS:
            v = 0.0        
        elif self.dtype == DimensionEnum.Tic_TS:
            v = 0.0        
        elif self.dtype == DimensionEnum.OSC_TS:
            v = 0.0        
        elif self.dtype == DimensionEnum.Max_TS:
            v = 0.0
        elif self.dtype == DimensionEnum.String:
            v = random.sample(["ABC", "XYZ", "CAT", "DOG", "WOW", "FOO", "BAR", "BAZ"], 8)
        elif self.dtype == DimensionEnum.Chunk:
            v = "Chunk" + random.sample(["1", "2", "3", "4", "5"], 5)
        elif self.dtype == DimensionEnum.Meta:
            v = "***Meta***"
        else:
            v = "NONE"

        return make_dvpair(self.label, v)

    def clone(self):
        """Makes a new dimension object that is a replica of this one.
        """
        clone = Dimension(self.label, self.dtype, self.mode, self.vals, self.minval, self.maxval)
        return clone

    @classmethod
    def parse_dimension_type(fld):
        if utilities.is_integer(fld):
            pass

# We would have liked to use collection.OrderedDict, but that's not pickable 
# and so can't be used with multiprocessing.

class DimensionDict (dict):
    """
    The DimensionDict holds all Dimensions for use by the simulation at runtime.
    It can also act as a writethrough for an underlying database.
    """

    def __init__(self):
        super(DimensionDict, self).__init__()
        self.order = []

    def append(self, d):
        self[d.label] = d
        self.order.append(d)

    def value_count_of_dim(self, dname):
        """Returns the number of possible values for the named dimension.
        Note that non-node dimension types have a count here of zero.
        An error results in -1 getting returned.
        """
        if dname in self:
            d = self[dname]
            return len (d.vals)
        else:
            return -1

    def load_from_jcontext(self, jcontext):
        """Given a json object, this extracts all the dimensions from the 
        "Dimensions" block and places them in this dictionary. Dimensions can 
        accumulate over multiple load files, but if any of these duplicates 
        an existing dimension, the existing dimension gets overridden.
        """
        keys = jcontext["dimensions"].keys()
        logger.info("dim keys are {}".format(keys))

        for dname in keys:
            try:
                try:
                    d = jcontext["dimensions"].get(dname)
                except:
                    logger.error(">>> problem retrieving Dimension key %s", dname)

                try:
                    logger.info("%s, %s %s", dname, d["dtype"], d["mode"])
                    logger.info("{}".format(d["vals"]))
                    dim = Dimension(dname, d["dtype"], d["mode"], d["vals"])
                except:
                    logger.error(">>> problem with Dimension() call")

                self.append(dim)
                #self.dimensions[dname] = dim

            except Exception as e:
                logger.error(">>> Could not process Dimension %s", dname)

    def load_from_jcontext_db(self, jcontext, session):
        """Appends the Dimensions from the JSON load file. Dimensions can 
        accumulate over multiple load files, but if any of these duplicate 
        existing dimensions, the existing dimension gets overridden.
        """

        keys = jcontext["dimensions"].keys()

        for dname in keys:
            try:
                d = jcontext["dimensions"].get(dname)
                # print (d)
                # print (d["Type"], d["Mode"], d["Vals"])

                dim = Dimension(dname, d["dtype"], d["mode"], d["vals"])
                self.append(dim)
                session.add(dim)
                session.flush()
                session.query(Dimension).filter_by(label=dname).first()
                valIndex = 0
                for vname in d["vals"]:
                    dv = DimVal(dname, valIndex, vname)
                    session.add(dv)
                    valIndex+=1
            except Exception as e:
                logger.error ("%s: could not process %s", e, dname)
                #print (e)

    def load_from_db(self, session):
        """Loads all values from database into dictionary.
        """

        logger.info("Parsing dimensions from database.")
        dims = session.query(Dimension).all()
        for dim in dims:
            dim.vals = json.loads(dim.valstring)
            self.append(dim)

    def deep_copy(self, org_dd):
        """Makes a clone of each Dimension found in org_dd (which must be a 
        DimensionDict) and adds it to itself. Dimensions can accumulate over 
        multiple calls, but if any of these duplicate existing dimensions, the 
        existing dimension gets overridden.
        """
        for name, dim in org_dd.items():
            new_dim = dim.clone()
            self.append(new_dim)


    @staticmethod
    def Clone(self, inp):
        """ NOT WORKING YET
        """
        clone = DimensionDict()

        for d in inp:
            print (d)
            clone.__dict__[key] = imp.__dict__[key]

        return clone

    def values_of_dim(self, dname):
        """Returns a list of possible values for the named dimension.
        Note that non-node dimension types will return an empty list.
        An error results in None getting returned.
        """
        if dname in self:
            d = self[dname]
            return d.values
        else:
            return None

    def dimnames(self):
        return list(self.keys())   # P34: Have to cast to a list

    def generate_node_vector(self):
        """ Returns the entire list of munged nodenames in insertion for purposes
        of setting up a neural net.  The munging is the dimension name, an underbar, 
        then the name of a value, in  succession.  This is only applied to "node"
        type dimensions, no others.
        """
        l = []

        for n in self:
            dim = self[n]
            if dim.type == DimensionEnum.Node:
                l.append(dim.get_node_vector())

        return l
  
    def generate_random_chunk(self):
        pass

class DimType(Base):
    __tablename__ = 'dimtypes'

    id = Column(Integer, primary_key = True)
    label = Column(String, nullable=False)
    isInt = Column(Boolean, nullable=False)
    isFloat = Column(Boolean, nullable=False)
    isTime = Column(Boolean, nullable=False)
    hasNodes = Column(Boolean, nullable=False)
    hasMinMax = Column(Boolean, nullable=False)
    desc = Column(String, nullable=False)

    def __init__(self, id, l, i, f, t, n, m, d):
        self.id = id
        self.label = l
        self.isInt = i
        self.isFloat = f
        self.isTime = t
        self.hasNodes = n
        self.hasMinMax = m
        self.desc = d

    def __repr__(self):
        return "<DimType(id='%s', label='%s', isInt='%s', isFloat='%s', isTime='%s', hasNodes='%s', hasMinMax='%s', desc='%s')>" % (
            self.id, self.label, self.isInt, self.isFloat, self.isTime, self.hasNodes, self.hasMinMax, self.desc)

class DimVal(Base):
    __tablename__ = 'dimvals'

    dim = Column(String, primary_key = True)
    val_index = Column(Integer, primary_key = True)
    label = Column(String, nullable=False)
    minval = Column(Float)
    maxval = Column(Float)

    def __init__(self, dname, vid, l, minv = None, maxv = None):
        self.dim = dname
        self.val_index = vid
        self.label = l
        self.minval = minv
        self.maxval = maxv

    def __repr__(self):
        return "<DimVal(dim='%s', val_index='%s', label='%s', minval='%s', maxval='%s')>" % (
            self.dim, self.val_index, self.label, self.minval, self.maxval)

class AcsRule(Base):
    __tablename__ = 'acs_rules'

    id = Column(Integer, primary_key = True)
    tic_stamp = Column(Integer, nullable=False)
    ruletype = Column(Integer, nullable=False)
    condchunk = Column(Integer, nullable=False)
    actionchunk = Column(Integer, nullable=False)
    activation = Column(Float, nullable=False)
    decay = Column(Float, nullable=False)
    label = Column(String, nullable=False)

    def __init__(self, tic, rule, cond, action, a, d, l):
        self.tic_stamp = tic
        self.ruletype = rule
        self.condchunk = cond
        self.actionchunk = action
        self.activation = a
        self.decay = d
        self.label = l

    def __repr__(self):
        return "<AcsRule(id='%s', tic_stamp='%s', ruletype='%s', condchunk='%s', actionchunk='%s', activation='%s', decay='%s', label='%s')>" % (
            self.id, self.tic_stamp, self.ruletype, self.condchunk, self.actionchunk, self.activation, self.decay, self.label)

class Chunk(Base):
    __tablename__ = 'chunks'

    id = Column(Integer, primary_key = True)
    chunktype = Column(Integer, nullable=False)
    chunkname = Column(String, nullable=False)
    chunktimestamp = Column(DateTime, nullable=False)
    chunktickstamp = Column(Integer, nullable=False)

    def __init__(self, ctype, name, time, tick):
        self.chunktype = ctype
        self.chunkname = name
        self.chunktimestamp = time
        self.chunktickstamp = tick

    def __repr__(self):
        return "<Chunk(id='%s', chunktype='%s', chunkname='%s', chunktimestamp='%s', chunktickstamp='%s')>" % (
            self.id, self.chunktype, self.chunkname, self.chunktimestamp, self.chunktickstamp)

class ChunkDvPair(Base):
    __tablename__ = 'chunk_dvpairs'

    cid = Column(Integer, primary_key = True)
    dim = Column(String, primary_key = True)
    valmin = Column(Float, nullable=False)
    valmax = Column(Float, nullable=False)

    def __init__(self, c, d, val):
        self.cid = c
        self.dim = d
        self.valmin = val
        self.valmax = val

    def __repr__(self):
        return "<ChunkDvPair(cid='%s', dim='%s', valmin='%s', valmax='%s')>" % (
            self.cid, self.dim, self.valmin, self.valmax)

class RuleConditions(Base):
    __tablename__ = 'ruleconditions'

    id = Column(Integer, primary_key=True)
    rule_id = Column(Integer)
    dim_id = Column(String)
    val_index = Column(Boolean)

    def __init__(self, rid, did, vid):
        self.rule_id = rid
        self.dim_id = did
        self.val_index = vid

    def __repr__(self):
        return "<RuleConditions(rule_id='%s', dim_id='%s', val_index='%s')>" % (
            self.rule_id, self.dim_id, self.val_index)


#class DimensionDatabase(Base, dict):
#	"""This is an exact copy of a dictionary used to implement a full
#	keep the language consistent with the literature. 
	    
#	We could alter this in the future if we want it to police what
#	kinds of types can be in DV-Pairs. That future change would not
#	require any changes to other wrappers as it would just act like a 
#	dictionary.
#	"""

#	__tablename__ = 'dimensions'

#	id = Column(Integer, primary_key=True)		
#	dimtype = Column(Integer, nullable=False)	# Nothing=0, Node, Ranged, TimeStamp, Integer, Float, String, Chunk, Meta
#	minval = Column(Float, nullable=True)		# only for continuous dimensions
#	maxval = Column(Float, nullable=True)		# only for continuous dimensions
#	label = Column (String(16), nullable=True)	
	
	#	DO WE NEED THIS?  valstring text not null,	-- would be a convenient tuple, not needed?
		
#	def __repr__(self):
#		return "<Dimension(label='%s', id='%i', type='%i')>" % (
#			self.label, self.id, self.dimtype)

#	def __init__(self, *args):
#		dict.__init__(self, args)
#		self.type = DimensionEnum.Nothing # TODO: FIX


#	def SetRange(self, min, max):
#		pass

def make_dvpair(dname, dval):
    return (dname, dval,)

if __name__ == '__main__':
	print (sqlalchemy.__version__)