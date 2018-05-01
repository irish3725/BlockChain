
import os
import random
import threading
import time

from utils import *
import ui

class miner():
    def __init__(self):
        # genesis block gives 100 to all clients
        self.chain = []
        self.chain.append(genesis())
        # variable to decide to continue mining
        self.mine = True
        # variable to decide to generate blocks automatically
        self.auto = True

    def addToChain(self, block):
        self.chain.append(block)

#    __________________________________________
    ## generates random block
    def createBlock(self, chain, valid=True):
        # create list of balances to make sure no double spending
        balance = []
        for i in range(5):
            balance.append(getBalance(chain,i))

        # generate a random number of transactions
        num_trans = int(random.uniform(1,5))

        # create empty block
        block = []
        # fill block with num_trans number of transactions
        for i in range(num_trans):
            # get random sender
            c1 = int(random.uniform(0,5))
            # get balance of sender
            c1_max = balance[c1]

            # only add to block if client has money
            if c1_max > 0:
                # get random receiver
                c2 = int(random.uniform(0,5))
                # get amount to be sent 
                amount = int(random.uniform(1,c1_max))
                # append new block
                block.append([c1, amount, c2])
                # if we want a valid block, keep track of balances
                if valid:
                    balance[c1] = balance[c1] - amount
                    balance[c2] = balance[c2] + amount

        # ger previous block and hash
        prev_block = chain[len(chain) - 1]
        prev_hash = hashlib.sha256(blockToString(prev_block).encode()).hexdigest()
        # append hash to block
        block.append(prev_hash)
        # get a valid nonce for block
        block = self.getNonce(block)
        # return new block
        return block

    ## generates random sha256 hashes for nonce till
    ## hash of block has diff number of leading 0s
    def getNonce(self, block):
        # difficulty of this block
        diff = 4
        # create initial nonce
        nonce = '0000000000000000000000000000000000000000000000000000000000000000'
        # append new nonce
        block.append(nonce)
        # iterate til we get a correct nonce
        while self.mine:
            
            # generate random nonce
            nonce = hashlib.sha256(str(time.time()).encode()).hexdigest()
            # make the last entry in block new nonce
            block[len(block)-1] = nonce
            this_hash = hashlib.sha256(blockToString(block).encode()).hexdigest()
            if this_hash[:diff] == '0000000000000000000000000000000000000000000000000000000000000000'[:diff]:
                return block 
        return False
#    __________________________________________

    def generateBlock(self, valid=True):
        block = self.createBlock(self.chain, valid=valid)
        if block:
            print('new block:', len(self.chain))
            printBlock(block)
            if len(block) > 2 and (checkValid(self.chain, block) or not valid):
                self.addToChain(block)
            else:
                self.auto = False

    def printChain(self):
        printChain(self.chain)

    def printAllBalances(self):
        printAllBalances(self.chain)

    def run(self):
        self.generateBlock()
        while self.mine:
            if self.auto:
                self.generateBlock()

if __name__ == '__main__':
    os.system('cls' if os.name == 'nt' else 'clear')
    miner = miner()
    ui = ui.ui(miner)

    threads = []

    threads.append(threading.Thread(name='run', target=miner.run))
    threads.append(threading.Thread(name='ui', target=ui.run))

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

