# Minimising Reachability Times in Temporal Graphs

This repository contains the Integer Linear Programming (ILP) implementation for computing optimal edge labellings in temporal graphs. The model schedules time labels to minimise the maximum reachability time with an imposed cap on the number of labels, ensuring that a designated set of sources can reach all vertices, and all vertices can reach a designated set of sinks. This uses the Gurobi Python to evaluate network topologies.

## Prerequisites and Installation

The solver requires a working installation of Python 3 and a valid Gurobi Optimiser license. You will need to install the Gurobi Python interface by running `pip install gurobipy` in your terminal.

## Usage and Configuration

To evaluate a different graph topology, you must modify three core variables within the script. You need to define `nodes`, `connections`and `ke` as a dictionary mapping each physical edge tuple to its maximum number of labels.

The script currently includes several topologies and defaults to a dual-hub routing network with two sources and two sinks. Once the graph is defined, run the script directly from the terminal. If an optimal solution is found, the console will output the minimised deadline and print the active temporal labels assigned to each utilised edge.
