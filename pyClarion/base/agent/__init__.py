'''This module provides the essential Agent class and a factory class to 
generate agents. An instance of the Agent class manages all the Clarion 
subsystems and their intercommunication. That instance also loads details
of itself from JSON files in the project file system (see documentation).

Agents are generally given a name at construction time. The particular
Clarion components are also specified at construction time, either through
settings in the agent's corresponding JSON file or in code.

The AgentFactory class is the preferred way to create one or more agents in
a simulation experiment.
'''


