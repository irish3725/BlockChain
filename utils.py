
import random

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

    # return new block
    return block

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
    for i in range(5):
        print('client', i, getBalance(chain, i))

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
    print('---------------------------------')
    for transaction in block:
        print('client', transaction[0], 'sends $' + str(transaction[1]), 'to client', transaction[2])
    print('---------------------------------')

## prints entire chain
def printChain(chain):
    for block in chain:
        printBlock(block)
#        printAllBalances(chain)

