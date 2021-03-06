
import os
import random
import threading
import time

from utils import *
#from Raft import Server
import ui

class miner():
    def __init__(self, m_id='0'):
        # genesis block gives 100 to all clients
        self.chain = [genesis()]
        self.leader = False
        # variable to decide to continue mining
        self.mine = True
        # variable to decide to generate blocks automatically
        self.auto = True
        # chance of generating a block
        self.p = 2
        # miner id
        self.id = m_id

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
        num_trans = int(random.uniform(1,6))

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
        block = self.sign(block)
        # return new block
        return block

    ## signs block and returns finished block
    def sign(self, block):
        block.append(self.id)
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
        wait = 2
        next_gen = time.time() + wait
        while self.mine:
            if next_gen < time.time():
                next_gen = time.time() + wait
                roll = int(random.uniform(0,self.p))
                if self.auto:
                    if roll == 0:
                        self.generateBlock()

if __name__ == '__main__':
    # clear terminal
    os.system('cls' if os.name == 'nt' else 'clear')
    # create list of threads
    threads = []

#    if len(sys.argv) > 1:
#        raft = Server(sys.argv[1])
#        threads.append(threading.Thread(name='raft', target=raft.run))

    miner = miner()
    ui = ui.ui(miner)


    threads.append(threading.Thread(name='run', target=miner.run))
    threads.append(threading.Thread(name='ui', target=ui.run))

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

