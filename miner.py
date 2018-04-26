
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

    def generateBlock(self, valid=True):
        block = generateBlock(self.chain, valid=valid)
        print('new block:')
        printBlock(block)
        if block and (checkValid(self.chain, block) or not valid):
            os.system('clear')
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

