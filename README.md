# REAM-Miner
This repository contains code for mining ArchiMate models. For this we use the official exchange format of ArchiMate to
extract the models into directed graphs. 

Then one can choose between different algorithms:
* RefPa (https://www.sciencedirect.com/science/article/abs/pii/S0306437918300838)
* MCC (https://aisel.aisnet.org/cgi/viewcontent.cgi?article=1350&context=ecis2013_cr) 
* REAM-Miner (comdined approach/self-designed)

The mentioned approaches automatically analyzing all single ArchiMate models to build a so-called Reference Model
which includes the best or good practices of one or more processes. For a more detailed description please read the 
linked papers.
