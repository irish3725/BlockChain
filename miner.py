
import os
import random
import threading
import time

from utils import *
import ui

class miner():
    def __init__(self):
        # genesis block gives 100 to all clients
        self.chain = [[['gen', 100, 0], ['gen', 100, 1], ['gen', 100, 2], ['gen', 100, 3], ['gen', 100, 4]]]
        # variable to decide to continue mining
        self.mine = True
        # variable to decide to generate blocks automatically
        self.auto = True

    def addToChain(self, block):
        self.chain.append(block)

    def generateBlock(self, valid=True):
        os.system('clear')
        block = generateBlock(self.chain, valid=valid)
        if block:
            self.addToChain(block)
            print('new block:')
            printBlock(block)

    def printChain(self):
        os.system('clear')
        printChain(self.chain)

    def printAllBalances(self):
        os.system('clear')
        printAllBalances(self.chain)

    def run(self):
        self.generateBlock()
        while self.mine:
            time.sleep(5)
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

