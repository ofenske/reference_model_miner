# REAM-Miner
This repository contains code for the project "Automatic construction of reference models". The project is structured as
follows:
* "core/": contains all the core functionality of the used graph structure.
* "mcc/": contains the code for the MCC algorithm and its variants.
* "ream_miner/": contains the code for our own developed approach, which combines the MCC and RefPa approach.
* "refpa/": contains the code for the refpa approach.

To run the algorithm you have to specifiy the path to the folder which contains the ArchiMate models you want to use as 
input and the location where you want to save the output file. For the MCC and combined algorithm you have additionally 
specifiy a threshold.
