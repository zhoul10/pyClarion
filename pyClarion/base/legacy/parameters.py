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

__author__ = 'Mike'

# TODO: INCORPORATE REMAINING SUBSYSTEM PARAMETERS

# TODO: lemThresh has no default; LEM_THRESHOLD added
# TODO: PerformDeletionByDensity has no default; PERFORM_DELETION_BY_DENSITY added
# TODO: doDel
# TODO: UseActionPotential is new
# TODO: C3, C4, A, B, now have PARAMETER_ in front of them
# TODO: long int business
# TODO: LOCAL_EPISODIC_MEMORY_RETENTION_THRESHOLD
# TODO: Names have changed everywhere!!  The all-cap spelling must be replaced with the Pascal-case spelling
# 
# === SOME NAMES HAVE CHANGED TO COMPLY WITH CODING STANDARD, AS FOLLOWS ===
#   MCSMaximumDecisionTime --> McsMaximumDecisionTime
#   PMThreshold --> PosMatchThreshold
#   MCSblSelectionMeasure --> McsBlSelectionMeasure
#   MCSrerSelectionMeasure --> McsRerSelectionMeasure
#   MCSirlSelectionMeasure --> McsIrlSelectionMeasure
#   MCSfrSelectionMeasure" --> McsFrSelectionMeasure
#   FixedBLSelectionMeasure --> FixedBlSelectionMeasure
#   VariableBLBeta -->  --> VariableBlBeta
#   FixedRERSelectionMeasure --> FixedRerSelectionMeasure
#   VariableRERBeta --> VariableRerBeta
#   FixedIRLSelectionMeasure --> FixedIrlSelectionMeasure
#   VariableIRLBeta --> VariableIrlBeta
#   FixedFRSelectionMeasure --> FixedFrSelectionMeasure
#   VariableFRBeta --> VariableFrBeta
#   GSUpdateActionProbability --> GoalUpdateActionProbability
#   WMUpdateActionProbability --> WmUpdateActionProbability
#   NACSReasoningActionProbability --> NacsReasoningActionProbability
#   NACSRetrieveActionProbability --> NacsRetrieveActionProbability

#   PerformBLLearning --> PerformBottomLevelLearning
#   PerformRERRefinement --> PerformRerRefinement
#   PerformIRLRefinement --> PerformIrlRefinement


# ----------------------------------------------------------------------------------------------------------------------
#   BUILT-IN DEFAULT PARAMETERS
#
#   This clunky module is intended to satisy several needs:
#		-- Provide very quick access to the values, not through a dict
#		-- facilitate project serialization
#		-- Discourage idle tinkering with these params
#
# ----------------------------------------------------------------------------------------------------------------------

# The options for level selection (such as fixed or variable)
# Replaces the LevelSelectionOptions enum
LEVEL_SELECTION_OPTION_FIXED = 0			# use the fixed level selection method
LEVEL_SELECTION_OPTION_VARIABLE = 1			# use the variable level selection method

# The various methods that can be used for level selection (such as stochastic or combined)
# Replaces the LevelSelectionMethods enum
LEVEL_SELECTION_METHOD_STOCHASTIC = 0   # stochastic level selection should be performed
LEVEL_SELECTION_METHOD_COMBINED = 1		# using weighted combination from top and bottom levels 		

#The meta-info reservations for the action-centered subsystem
#This enumerator is implemented as part of the new Clarion-E emotion mechanism (a proposal
#for Nicholas Wilson's dissertation)
# Replaces the MetaInfoReservations enum

METAINFO_ACTION_POTENTIAL = 0
METAINFO_CALCULATING_ACTION_POTENTIAL = 1
METAINFO_CHOOSING_ACTION = 2 
METAINFO_LEARNING = 3 
METAINFO_PERFORMING_INTERMITTENT_RULE_DELETION = 4
METAINFO_UPDATING_WM = 5

# ----------------------------------------------------------------------------------------------------------------------
#   BUILT-IN DEFAULT PARAMETERS
#
#   These are the defaults parameters used before any other blocks of value that can override these are invoked.
#   We don't encourage changing any of these in the code. Change them downstream instead.
#
# ----------------------------------------------------------------------------------------------------------------------

LEVEL_SELECTION_METHOD = LEVEL_SELECTION_METHOD_STOCHASTIC
LEVEL_SELECTION_OPTION = LEVEL_SELECTION_OPTION_VARIABLE
TOP_LEVEL_DECISION_TIME = 500
BOTTOM_LEVEL_DECISION_TIME = 350
MAXIMUM_DECISION_TIME = 2147483647       # long.MaxValue  ; HACK
MCS_MAXIMUM_DECISION_TIME = -1
POSITIVE_MATCH_THRESHOLD = 0.5
PARAMETER_C3 = 1
PARAMETER_C4 = 2
MCS_BL_SELECTION_MEASURE = 0.5
MCS_RER_SELECTION_MEASURE = 0.5
MCS_IRL_SELECTION_MEASURE = 0.5
MCS_FR_SELECTION_MEASURE = 0.5
PARAMETER_A = 0.0
PARAMETER_B = 2.0
FIXED_BL_LEVEL_SELECTION_MEASURE = 0.7
VARIABLE_BL_BETA = 0.7
FIXED_RER_LEVEL_SELECTION_MEASURE = 0.15
VARIABLE_RER_BETA = 0.15
FIXED_IRL_LEVEL_SELECTION_MEASURE = 0.15
VARIABLE_IRL_BETA = 0.15
FIXED_FR_LEVEL_SELECTION_MEASURE = 0.0
VARIABLE_FR_BETA = 0.0
EXTERNAL_ACTION_PROBABILITY = 1.0
GS_UPDATE_ACTION_PROBABILITY = 0.0
WM_UPDATE_ACTION_PROBABILITY = 0.0
NACS_REASONING_ACTION_PROBABILITY = 0.0
NACS_RETRIEVE_ACTION_PROBABILITY = 0.0
PARAMETER_CHANGE_ACTION_PROBABILITY = 0.0
USE_ACTION_PROBABILITIES = True
PERFORM_RULE_EXTRACTION = True
PERFORM_BL_LEARNING = True
PERFORM_TOP_DOWN_LEARNING = True
PERFORM_RER_REFINEMENT = True
PERFORM_IRL_REFINEMENT = True
PERFORM_DELETION_BY_DENSITY = True
DISCOUNT = 0.9
PERSISTENCE = 0.0
SELECTION_TEMPERATURE = 0.1
SELECTION_THRESHOLD = 0.0
DELETION_FREQUENCY = 20
WORKING_MEMORY_CAPACITY = 7
LEM_THRESHOLD = 10   # NEW
USE_ACTION_POTENTIAL = False
DEFAULT_ACTION_POTENTIAL = 0.5

# TODO: Add a comment field as [2] in the tuple

# TODO: Rename these with better naming convention

ParameterInitializers = [
    ("LevelSelectionMethod", LEVEL_SELECTION_METHOD),           # LEVEL_SELECTION_METHOD_STOCHASTIC
    ("LevelSelectionOption", LEVEL_SELECTION_OPTION),           # LEVEL_SELECTION_OPTION_VARIABLE
    ("TopLevelDecisionTime", TOP_LEVEL_DECISION_TIME),          # 500
    ("BottomLevelDecisionTime", BOTTOM_LEVEL_DECISION_TIME),    # 350
    ("MaximumDecisionTime", MAXIMUM_DECISION_TIME),             # 2147483647, long.MaxValue,HACK
    ("McsMaximumDecisionTime", MCS_MAXIMUM_DECISION_TIME),      # -1
    ("PosMatchThreshold", POSITIVE_MATCH_THRESHOLD),            # 0.5
    ("ParameterC3", PARAMETER_C3),                              # 1
    ("ParameterC4", PARAMETER_C4),                              # 2
    ("McsBlSelectionMeasure", MCS_BL_SELECTION_MEASURE),        # 0.5
    ("McsRerSelectionMeasure", MCS_RER_SELECTION_MEASURE),      # 0.5
    ("McsIrlSelectionMeasure", MCS_IRL_SELECTION_MEASURE),      # 0.5
    ("McsFrSelectionMeasure", MCS_FR_SELECTION_MEASURE),        # 0.5
    ("ParameterA", PARAMETER_A),                                # 0
    ("ParameterB", PARAMETER_B),                                     # 2
    ("FixedBlSelectionMeasure", FIXED_BL_LEVEL_SELECTION_MEASURE),   # 0.7
    ("VariableBlBeta", VARIABLE_BL_BETA),                            # 0.7
    ("FixedRerSelectionMeasure", FIXED_RER_LEVEL_SELECTION_MEASURE), # 0.15
    ("VariableRerBeta", VARIABLE_RER_BETA),                          # 0.15
    ("FixedIrlSelectionMeasure", FIXED_IRL_LEVEL_SELECTION_MEASURE), # 0.15
    ("VariableIrlBeta", VARIABLE_IRL_BETA),                          # 0.15
    ("FixedFrSelectionMeasure", FIXED_FR_LEVEL_SELECTION_MEASURE),   # 0
    ("VariableFrBeta", VARIABLE_FR_BETA),                            # 0
    ("ExternalActionProbability", EXTERNAL_ACTION_PROBABILITY),      # 1
    ("GoalUpdateActionProbability", GS_UPDATE_ACTION_PROBABILITY),   # 0
    ("WmUpdateActionProbability", WM_UPDATE_ACTION_PROBABILITY),     # 0
    ("NacsReasoningActionProbability", NACS_REASONING_ACTION_PROBABILITY),       # 0
    ("NacsRetrieveActionProbability", NACS_RETRIEVE_ACTION_PROBABILITY),         # 0
    ("ParameterChangeActionProbability", PARAMETER_CHANGE_ACTION_PROBABILITY),   # 0
    ("UseActionProbabilities", USE_ACTION_PROBABILITIES),        # TRUE
    ("PerformRuleExtraction", PERFORM_RULE_EXTRACTION),          # TRUE
    ("PerformBottomLevelLearning", PERFORM_BL_LEARNING),         # TRUE
    ("PerformTopDownLearning", PERFORM_TOP_DOWN_LEARNING),       # TRUE
    ("PerformRerRefinement", PERFORM_RER_REFINEMENT),            # TRUE
    ("PerformIrlRefinement", PERFORM_IRL_REFINEMENT),            # TRUE
    ("PerformDeletionByDensity", PERFORM_DELETION_BY_DENSITY),   # TRUE
    ("Discount", DISCOUNT),                                      # 0.9
    ("Persistence", PERSISTENCE),                                # 0
    ("StochasticSelectionTemperature", SELECTION_TEMPERATURE),   # 0.1
    ("StochasticSelectionThreshold", SELECTION_THRESHOLD),       # 0
    ("DeletionFrequency", DELETION_FREQUENCY),                   # 20
    ("WorkingMemoryCapacity", WORKING_MEMORY_CAPACITY),          # 7
    ("LocalEMRetentionThreshold", LEM_THRESHOLD),                # 10
    ("UseActionPotential", USE_ACTION_POTENTIAL),                # FALSE
    ("ActionPotentialDefault", DEFAULT_ACTION_POTENTIAL)         # 0.5
]

# ----------------------------------------------------------------------------------------------------------------------
#   Class AcsParameterBlock
#
#   These are the defaults parameters used before any other blocks of value that can override these are invoked.
# ----------------------------------------------------------------------------------------------------------------------


class Parameters(object):		# formerly  ActionCenteredSubsystemParameters						
    """This is the Parameters class used by all four Clarion subsystems."""

    def __init__(self, isempty=False, isglobal=False):
        """
        Initializes a parameters class for a Clarion agent and sets the values of the parameters 
        to the values specified. Indicates the parameter values to be set for the parameters class 
        being initialized.  isGlobal (optional) specifies whether the instance of the parameters 
        class being initialized is to be used for global or local parameters. This may be going
        away

        Parameters are loaded directly into __dict__, which is why this classes doesn't need to
        subclass dict.

        @param boolean isglobal  
        """

        # The ACS with which this parameters class is affiliated.  (Name = "AffiliatedACS")
        # TODO: Not sure we need to keep this anymore
        acs = None    # ActionCenteredSubsystem

        # Used to specify whether the particular instance of the parameters class is being used for global or local
        # parameters (Name = "IsGlobal")
        # TODO: Not sure we need to keep this anymore
        self.isG = isglobal  # TODO

        # Load all the initialized parameters into the dict
        if isempty == False:
            for pi in ParameterInitializers:
                self.__dict__[pi[0]] = pi[1]


# ----------------------------------------------------------------------------------------------------------------------
#   Savers and Loaders
# ----------------------------------------------------------------------------------------------------------------------
    
    def SaveToJSON(self, path):
        """
        @parameters string  path  fully qualified path to the desired file
        """
        pass

    def LoadFromJSON(self, path):
        """
        @parameters string  path  fully qualified path to the desired file
        """
        pass

    def SaveToXML(self, path):
        """
        @parameters string  path  fully qualified path to the desired file
        """
        pass

    def LoadFromXML(self, path):
        """
        @parameters string  path  fully qualified path to the desired file
        """
        pass

    def UpdateFromINI(self, path):
        """
        This method updates only those parameters explicitly mentioned in the file and
        leaves the other parameters unchanged.

        @parameters string  path  fully qualified path to the desired file
        """
        pass

    def UpdateFromJSON(self, path):
        """
        This method updates only those parameters explicitly mentioned in the file and
        leaves the other parameters unchanged.
        
        @parameters string  path  fully qualified path to the desired file
        """
        pass

    def UpdateFromXML(self, path):
        """
        This method updates only those parameters explicitly mentioned in the file and
        leaves the other parameters unchanged.
        
        @parameters string  path  fully qualified path to the desired file
        """
        pass

    def get(self, kname):
        if kname in self.__dict__:
            return self.__dict__[kname]
        else:
            return None

    def set(self, kname, newval):
        if kname in self.__dict__:
            self.__dict__[kname] = newval
            return True
        else:
            return False
            

    @staticmethod
    def Clone(self, inp):
        clone = Parameters(True, False)

        for pi in inp.__dict__:
            print (pi)
            clone.__dict__[key] = imp.__dict__[key]

        return clone

    def copy(self):
        clone = Parameters(True, False)

        print ("INSIDE Parameters.copy")
        for key in self.__dict__:
            # print key
            clone.__dict__[key] = self.__dict__[key]

        return clone


if __name__ == "__main__":
    # Someone should automate these tests
    print ("Testing Parameters...")
    pb = Parameters()

    print (pb.MaximumDecisionTime)
    print (pb.ExternalActionProbability)
    print (pb.UseActionPotential)

    print (pb.__dict__)

    newpb = pb.copy()

    print (pb.MaximumDecisionTime)
    pb.MaximumDecisionTime = 123456789
    print (pb.MaximumDecisionTime)
    print (pb.__dict__["MaximumDecisionTime"]) 

    print (newpb.MaximumDecisionTime) 
    newpb.MaximumDecisionTime = 444444444
    print (newpb.MaximumDecisionTime)
    print (newpb.__dict__["MaximumDecisionTime"]) 

    pb.MaximumDecisionTime = 987654321
    print (pb.MaximumDecisionTime)
    print (newpb.MaximumDecisionTime)