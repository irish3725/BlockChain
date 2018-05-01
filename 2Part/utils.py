import hashlib
import json
import random
import time

# RSA stuff
import ast
#from Crypto.PublicKey import RSA 

## generates correct genesis block
def genesis(m_id='0'):
    gen_block = [['gen', 100, 0], ['gen', 100, 1], ['gen', 100, 2], ['gen', 100, 3], ['gen', 100, 4]]
    prev_hash = hashlib.sha256(str(time.time()).encode()).hexdigest()
    gen_block.append(prev_hash)
    gen_block.append(m_id) 
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

    # ger previous block and hash
    prev_block = chain[len(chain) - 1]
    prev_hash = hashlib.sha256(blockToString(prev_block).encode()).hexdigest()
    # append hash to block
    block.append(prev_hash)
    # get a valid nonce for block
    block = getNonce(block)
    # return new block
    return block

## generates random sha256 hashes for nonce till
## hash of block has diff number of leading 0s
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
            return block 

## function so I don't have to remember if
## i need json dumps or loads
def blockToString(block):
    return json.dumps(block)

## checks to see if block is valid within chain
def checkValid(chain, block):
    diff = 4
    # check for valid chain
    for i in range(len(chain)):
        # skip genesis block
        if i != 0:
            # get current and previous block and hash
            cur_block = chain[i]
            this_hash = hashlib.sha256(blockToString(cur_block).encode()).hexdigest()
            prev_block = chain[i-1]
            prev_hash = hashlib.sha256(blockToString(prev_block).encode()).hexdigest()
            # if previous hash does not match hash of previous block
            if cur_block[len(cur_block) - 2] != prev_hash:
                print('invalid previous hash')
                return False

            # make sure hash has proper number of leading 0's
#            if this_hash[:diff] != '0000000000000000000000000000000000000000000000000000000000000000'[:diff]:
#                print('incorrect nonce:', nonce)
#                return False
           
            

    # make copy of chain
    chainCopy = list(chain)
    # append new block to chain
    chainCopy.append(block)
    # check balance of all clients
    for i in range(5):
        balance = getBalance(chainCopy, i)
        # if invalid balance, return false
        if balance < 0 or balance > 500:
            print('incorrect balance for', i, ': ', balance)
            printBlock(block)
            return False

    # make sure every transaction amount is valid
    for line in block:
        # make sure we are looking at a transaction
        if len(line) == 3:
            amount = line[1]
            if amount < 1 or amount > 500:
                print('incorrect transaction amount', amount)
                return False

    # make sure total in blockchain is still 500
    amount = getTotal(chainCopy)
    if amount != 500:
        print('incorrect total:', amount)
        printAllBalances(chainCopy)
        printChain(chainCopy)
        return False

    return True
            
## method to print all balances
def printAllBalances(chain):
    print('\n__________Balances__________')
    ## there are 5 clients, so iterate 0-4
    for i in range(5):
        print('\tclient', str(i) + ':', getBalance(chain, i))
    print('\ttotal:', getTotal(chain))

## method to return balance of client
## according to history in chain
def getBalance(chain, client):
    # set initial balance to 0
    balance = 0
    # look at each block
    for block in chain:
        # look at each transaction
        for line in block:
            if len(line) == 3:
                # get the amount traded
                amount = line[1]
                # if the money is coming from client, subtract amount
                if line[0] == client:
                    balance = balance - amount
                # if the money is coming from client, add amount
                if line[2] == client:
                    balance = balance + amount

    return balance

## returns value of transactions in block
def getBlockValue(block):
    total = 0
    # look at each line in block
    for line in block:
        # don't look at previous hash or nonce
        if len(line) == 3:
            total = total + line[1]
    return total

## returns total amount of money in chain
def getTotal(chain):
    # keep track of running total
    total = 0
    # iterate over each client
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
    print('creator:\t', block[len(block) - 1])
    print('block value:\t', getBlockValue(block))
    print('---------------------------------')

## prints entire chain
def printChain(chain):
    # keep track of block number
    i = 0
    # iterate over each block
    for block in chain:
        print('block', i)
        i = i + 1
        printBlock(block)

def gen_keys():
    print('gen_keys not implemented')
    return '0','0'
#    new_key = RSA.generate(bits, e=65537) 
#    public_key = new_key.publickey().exportKey("PEM") 
#    private_key = new_key.exportKey("PEM") 
#    return private_key, public_key
            
## RSA encryption with publickey
def encrypt(key, message):
    return key.publickey().encrypt(message, 32)

## RSA decryption with privatekey
def decrypt(key, message):
    return key.decrypt(ast.literal_eval(str(message)))
