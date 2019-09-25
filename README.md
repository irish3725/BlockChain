# Blockchain
Blockchain is a simple implementation of a blockchain in python 3. The final implementation exists as minter.py, utils.py, and ui.py in the Blockchain directory. The directories 1Part and 2Part hold earlier versions of this project. 

This implementation uses proof of work to generate new blocks. Only one miner exists, and it generates a nonce until the sha256 hash of that block begins with five 0's. 

Each block contains a list of transactions between five simulated clients that each begin with $100. 
### Running OSQuery

This implementation must be run from the Blockchain directory, and it is run using the following command:

    python miner.py

