
import os

import miner
import utils

class ui:

    ## @param cal - calendar object that will be interated with
    def __init__(self, miner):
        self.miner = miner

    ## main ui loop
    def run(self):  
        # value to read input into 
        val = ''

        while val != 'q' and val != 'quit' and val != 'exit' and self.miner.mine:
            val = input('automine: ' + str(self.miner.auto) + '\nWould you like to:\nhault/resume autogeneration (a)\ngenerate a new block (n)\nprint the whole blockchain (p)\nprint all clients\' balances (b)\nor quit (q)\n(a,n,p,b,q) > ').lower()

            # adding an event
            if val == 'gen' or val == 'n' or val == 'g' or val == 'generate' or val == 'new':
                self.miner.generateBlock()
            elif val == 'print' or val == 'p':
                self.miner.printChain()
            elif val == 'balance' or val == 'b':
                self.miner.printAllBalances()
            elif val == 'a':
                if self.miner.auto:
                    self.miner.auto = False
                    print('automine: False')
                else:
                    self.miner.auto = True
                    print('automine: True')
                    

        self.miner.mine = False

