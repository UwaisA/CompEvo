# CompEvo
Imperial Physics Computational Evolution Project

This is the code supporting the 3rd Year BSc Project of Uwais Ashraf and Charlie Ugo, supervised by Dr David Clements and is a work in progress.

In order to see the simulation in action run Environment.py on a system with PyGame and PyTMX installed and run the 'DisplaySavedSim()' method, then choose a simulation from the list formatted as 'sim_[time]_[sim length in time steps].dat'.

The code sets up a 2D world (Environment.py) and adds creatures (Creature.py) which have certain properties representing their genetics. As the simulation of the world progresses it can be seen that with each generation the genetics of the creatures in the system tend to optimise themselves to the environment.

To see this in action we have provided a display tool (Test_Graphics_2.py) which uses PyGame and PyTMX to show a visualisation of the creatures and how they move in this 2D world.

Our overall aim for the project is to investigate significant events in evolutionary history e.g. the Cambrian Explosion, Extinction of the Dinosaurs or Primordial Mars.
