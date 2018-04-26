import hashlib
import json
import random
import time

def genesis():
    gen_block = [['gen', 100, 0], ['gen', 100, 1], ['gen', 100, 2], ['gen', 100, 3], ['gen', 100, 4]]
    prev_hash = hashlib.sha256(str(time.time()).encode()).hexdigest()
    gen_block.append(prev_hash)
    gen_block = getNonce(gen_block)
    return gen_block

## generates random block
def generateBlock(chain, valid=True):
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
        c1 = int(random.uniform(0,4))
        # get balance of sender
        c1_max = balance[c1]

        # only add to block if client has money
        if c1_max > 0:
            # get random receiver
            c2 = int(random.uniform(0,4))
            # get amount to be sent 
            amount = int(random.uniform(1,c1_max))
            # append new block
            block.append([c1, amount, c2])
            # if we want a valid block, keep track of balances
            if valid:
                balance[c1] = balance[c1] - amount
                balance[c2] = balance[c2] + amount

    
    prev_block = chain[len(chain) - 1]
    prev_hash = hashlib.sha256(blockToString(prev_block).encode()).hexdigest()
    block.append(prev_hash)
    block = getNonce(block)
    # return new block
    return block

def getNonce(block):
    # difficulty of this block
    diff = 4
    # create initial nonce
    nonce = '0000000000000000000000000000000000000000000000000000000000000000'
    # append new nonce
    block.append(nonce)
    # iterate til we get a correct nonce
    while True:
        
        # generate random nonce
        nonce = hashlib.sha256(str(time.time()).encode()).hexdigest()
        # make the last entry in block new nonce
        block[len(block)-1] = nonce
        this_hash = hashlib.sha256(blockToString(block).encode()).hexdigest()
        if this_hash[:diff] == '0000000000000000000000000000000000000000000000000000000000000000'[:diff]:
            print('new nonce:', nonce)
            return block 

def blockToString(block):
    return json.dumps(block)

## checks to see if block is valid within chain
def checkValid(chain, block):
    # make copy of chain
    chainCopy = list(chain)
    # append new block to chain
    chainCopy.append(block)
    # check balance of all clients
    for i in range(5):
        balance = getBalance(chainCopy, i)
        # if invalid balance, return false
        if balance < 0 or balance > 500:
            return False

    # make sure every transaction amount is valid
    for transaction in block:
        amount = transaction[1]
        if amount < 1 or amount > 500:
            return False

    # make sure total in blockchain is still 500
    amount = getTotal(chainCopy)
    if amount != 500:
        return False

    return True
            
## method to print all balances
def printAllBalances(chain):
    print('\n__________Balances__________')
    for i in range(5):
        print('\tclient', str(i) + ':', getBalance(chain, i))
    print()

## method to return balance of client
## according to history in chain
def getBalance(chain, client):
    # set initial balance to 0
    balance = 0
    # look at each block
    for block in chain:
        # look at each transaction
        for transaction in block:
            # get the amount traded
            amount = transaction[1]
            # if the money is coming from client, subtract amount
            if transaction[0] == client:
                balance = balance - amount
            # if the money is coming from client, add amount
            if transaction[2] == client:
                balance = balance + amount

    return balance

## returns total amount of money in chain
def getTotal(chain):
    total = 0
    for i in range(5):
        total = total + getBalance(chain, i)
    return total
        
## prints single block in chain
def printBlock(block):
    i = 0
    print('---------------------------------')
    for line in block:
        if len(line) == 3:
            print('transaction', str(i) + ': \t client', line[0], 'sends $' + str(line[1]), 'to client', line[2])
            i = i + 1
    print('previous hash:\t', block[len(block) - 2])
    print('nonce:\t\t', block[len(block) - 1])
    print('---------------------------------')

## prints entire chain
def printChain(chain):
    for block in chain:
        printBlock(block)
            
#        printAllBalances(chain)

