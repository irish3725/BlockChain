
# python imports
import random
import sys
import json
import boto3
import threading
import time

# my file imports
import raft_ui
from raft_utils import *

class Server: 
    # init with a server id
    # @param s_id - server id (letter a-e)
    def __init__(self, s_id='0'):
        # boolean for polling
        self.poll = True
        # boolean for simulating clients
        self.simulate = False

        # get info about client for sqs queue and s3 stable storage
        self.region = 'us-west-2'
        self.secret = ''
        self.public = 'AKIAIVCVGBRSVQKRNB3Q'

        # create list of queue urls
        self.q_url = list()
        self.q_url.append('https://sqs.us-east-2.amazonaws.com/044793243766/queue0')
        self.q_url.append('https://sqs.us-east-2.amazonaws.com/044793243766/queue1')
        self.q_url.append('https://sqs.us-east-2.amazonaws.com/044793243766/queue2')
        self.q_url.append('https://sqs.us-east-2.amazonaws.com/044793243766/queue3')
        self.q_url.append('https://sqs.us-east-2.amazonaws.com/044793243766/queue4')
        self.q_url.append('https://sqs.us-east-2.amazonaws.com/044793243766/queue5')
        self.q_url.append('https://sqs.us-east-2.amazonaws.com/044793243766/queue6')

        # get access to sqs queue
        self.sqs = boto3.client('sqs', self.region, aws_secret_access_key=self.secret, aws_access_key_id=self.public)

        # create list of sqs queues
        self.q = list()

        # create queue with timeout
        for i in range(7):
            queue_name = 'queue' + str(i)
            self.q.append(self.sqs.create_queue(QueueName=queue_name))

        # number of running processes
        self.processes = 5

        # get sqs queue
        # id of this server
        self.id = s_id
        # timeout for starting a new election as random time between 150ms and 300ms
        # will be set after clearing queue
        self.timeout = time.time()
        # counting timeouts for debugging
        self.timeout_count = 0
        # id of server that this server is voting for in current election
        self.voted_for = None
        # number of known votes for this server in current election
        self.votes = 0
        # current state of this server
        # possible states = {follower, leader, candidate}
        self.state = 'follower'
        # id of leader of this current term
        self.leader = None
        # current known term
        self.term = 0
        # known log of events
        self.log = [] 
        # count of known adds for commiting
        self.adds = []
        # index of last commit on this machine
        self.commit_index = -1

        # client things
        self.players = [[0,0], [0,0]]
        self.ko_rate = 5 

    ## function to randomly decide to generate client request
    def generate_cleint_request(self):
        # roll random number between 0 and 1000
        roll = int(random.uniform(0,100))
        if roll == 1 and self.leader != None:
#            print('\n!!!!!!!creating client request!!!!!!!\n')
            # choose a random action 
            action = int(random.uniform(0,4))
            if action == 0:
                action = 'q'
            elif action == 1:
                action = 'w'
            elif action == 2:
                action = 'a'
            elif action == 3:
                action = 's'

            # choose a random player
            player = 'p' + str(int(random.uniform(1,3)))
           
            # create client request and send to leader
            message = create_client_request(self.leader, player, action)
            self.send_message(message)

    ## function to simulate a failure of this server node
    def fail(self):
        if self.state != 'failed':
            print('\nnode failed\n')
            self.state = 'failed'

    ## function to simulate a recover of this server node after failure
    def recover(self):
        self.clear_queue()
        if self.state == 'failed':
            print('\nnode recovered. Going back to follower state\n')
            self.timeout = time.time() + get_timeout()
            self.state = 'follower'

    # begin election by setting voted_for to self,
    # incrementing current term, and setting state
    # to candidate
    def begin_election(self):
        self.state = 'election'
        self.voted_for = self.id
        self.votes = 1
        print('Beginning election')
        # create proposed term
        new_term = self.term + 1
        # if there are committed values in the log
        if self.log and self.commit_index != -1:
            # get last committed entry
            log_entry = self.log[self.commit_index]
            log_index = self.commit_index 
        # else send empyt entry and -1 for commit index
        else:
            log_entry = []
            log_index = -1

        for i in range(self.processes):
            if str(i) != self.id:
                message = create_request_message(str(i), self.id, log_index, log_entry, new_term)
                self.send_message(message)
        
    ## receive reply for vote request
    def receive_election_reply(self, election_reply_message):
        if self.state == 'election' and self.voted_for == self.id:
            # turn message back into list
            election_reply_message = json.loads(election_reply_message[1:])
            # get sender
            message_sender = election_reply_message[1]
            # get vote
            vote = election_reply_message[2]
            # if vote is true, increment vote
            if vote:
#                print('got vote from', message_sender)
                self.votes += 1
#                print('I now have', self.votes, 'votes of', int(self.processes / 2 + 1))
            # if we have majority of votes, become leader
            if self.votes > int(self.processes / 2):
                self.votes = 0
                self.leader = self.id
                self.voted_for = None
                self.term += 1
                self.state = 'leader'
                
                # initialize new adds list of size of committed log and filled with 0s
                self.adds = [0 for x in range(self.commit_index + 1)]
                # remove all noncommitted values from our log
                while len(self.log) - 1 > self.commit_index:
                    self.log.pop()

                
#                self.send_append_entries()
                print('\nI am leader now')
        else:
            return

    # handle the receiving of request vote message
    def receive_request_vote(self, request_vote_message):
        # turn message back into list
        request_vote_message = json.loads(request_vote_message[1:])
        # get sender 
        message_sender = request_vote_message[1]
        # get index of last entry
        message_log_index = int(request_vote_message[2])
        # get last entry
        message_log_entry = request_vote_message[3]
        # get new term
        message_term = int(request_vote_message[4])
        # create empty reply message
        reply = ''

        # separate if to handle vote before first commit
        if (self.voted_for == None and self.term < message_term and
                self.commit_index == -1):

            self.voted_for = message_sender
            self.state = 'election'
            reply += create_request_reply(message_sender, self.id, True)
            self.timeout = time.time() + get_timeout()
        # make sure we haven't voted yet, this is a new term, 
        # and the proposed largest committed index is at least
        # large as ours also check for if our commit_index is 
        # behind or they have the same last committed value
        elif (self.voted_for == None and self.term < message_term and 
                self.commit_index <= message_log_index and 
                (self.commit_index < message_log_index or 
                self.log[message_log_index] == message_log_entry)): 

            self.voted_for = message_sender
            self.state = 'election'
            reply += create_request_reply(message_sender, self.id, True)
            self.timeout = time.time() + get_timeout()
        # if we have already voted, send false reply
        else:
            reply += create_request_reply(message_sender, self.id, False)
    
        self.send_message(reply)
#        print('\tReply:', reply)

    ## send append_entries message to all followers
    ## @param index, index of last seen entry
    def send_append_entries(self, index=None):

        # reset timeout
        self.timeout = time.time() + get_timeout()
        
        # if index not given, set index to before newest message
        if index == None:
            index= len(self.log) - 2

        # if new index is less than 0, set to 0 to send all entries
        if index < 0:
            index = 0

        # create and send messages to all other processes
        for i in range(0,self.processes):
            if str(i) != self.id:
                message = create_append_message(str(i), self.id, index, self.log[index:], self.term)
                self.send_message(message)

    # handle receiving append_entries message by comparing
    # the last index of received log to local log
    def receive_append_entries(self, append_message):

        # get message
        append_message = json.loads(append_message[1:])
        # get sender
        message_sender = append_message[1]
        # get term
        message_term = append_message[4]

        # if we are in an election, set new leader,
        if message_term > self.term or (message_term == self.term and self.state == 'election'):
            self.leader = message_sender
            self.state = 'follower'
            self.voted_for = None
            self.votes = 0
            self.term = message_term
            print('my new leader is', message_sender)

        # get log_index
        message_log_index = int(append_message[2])
        # get log_after_index
        message_log_after_index = append_message[3] 

        # make sure doesn't have an empty log
        if message_log_after_index:

            # boolean for if we have to reply (we did add something or we need more info)
            reply = False
            # check to see if we have this entry
#            print('local last index:', len(self.log) - 1, 'rec log index:', message_log_index, 'log:', self.log, 'message_log:', message_log_after_index)

            # index of last add for reply message
            index = 0

            # handle having an empty log.
            if len(self.log) == 0 and message_log_index == 0:
                # if there actually is something in the log
                for entry in message_log_after_index:    
                    term = entry[0]
                    player = entry[1]
                    action = entry[2]
                    self.add_to_log(term, player, action)
                    reply = True

            # if we have seen the first value in message_log_index
            elif len(self.log) > message_log_index and self.log[message_log_index] == message_log_after_index[0]:
                # get index that we are adding at
                index = message_log_index
                # add all following values 
                for entry in message_log_after_index:    
                    # ignore entry if we already have it, write if we dont
                    if index > len(self.log) - 1 or entry != self.log[index]:
                        term = entry[0]
                        player = entry[1]
                        action = entry[2]
                        self.add_to_log(term, player, action, index)
                        reply = True
                    # increment index in our log for comparing
                    index += 1
                # decrement index once after loop
                index -= 1
            # if we haven't seen that value yet, tell sender
            # the last value that we know that we have seen
            else:
                index = self.commit_index
                reply = True

            # only reply if we have added any entries
            if reply:
                # create reply message
                reply = create_append_reply(message_sender, self.id, index)
                # send reply to sender of append
                self.send_message(reply)

    ## handle append reply
    def receive_append_reply(self, message):

        message = json.loads(message[1:])
        sender = message[1]
        index = message[2]

        # if we know of value greater than returned index
        if len(self.log) - 1 > index:
            # send new append entries starting at that index
            self.send_append_entries(index)

        # we only care about index if we haven't committed yet
        if index > self.commit_index:
            # increment that spot in self.adds to count add
            self.adds[index] += 1

            # if we have seen a majority of adds, commit
            if self.adds[index] > self.processes / 2:
                self.commit_entry(index)
#                print('committed entry, new commit_index =', self.commit_index)
            
    ## handle committing an entry
    def commit_entry(self, index):
        # change commit_index to index
        self.commit_index = index
        for i in range(5):
            if str(i) != self.id:
                message = create_commit_message(str(i), self.id, self.commit_index, self.log[self.commit_index])
                self.send_message(message)
        self.player_state()

    ## handle receiving commit message
    def receive_commit_message(self, commit_message):
        commit_message = json.loads(commit_message[1:])
        index = commit_message[2]
        entry = commit_message[3]
        # if we have this entry, commit it
        if len(self.log) > index and self.log[index] == entry:
            self.commit_index = index
#            print('!! new commit index is', self.commit_index, '!!')

    ## check to see if a player has won
    def player_state(self):
        player = self.log[self.commit_index][1]
        # get index of player in self.players
        player = int(player[1:]) - 1
        action = self.log[self.commit_index][2]
       
        # get new state if changed
        if action == 'a':
            # change timestamp for left block to current time
            self.players[player][0] = int(time.time())
            print('\nSTATE CHANGE\n', self.log[self.commit_index][1], ':', self.players[player], '\n')

            message = '\tblocking left\n'
            m = create_server_message(str(player + 5), 'action', [player, message])
            self.send_message(m)

        elif action == 's':
            self.players[player][1] = int(time.time())
            print('\nSTATE CHANGE\n', self.log[self.commit_index][1], ':', self.players[player], '\n')

            message = '\tblocking left\n'
            m = create_server_message(str(player + 5), 'action', [player, message])
            self.send_message(m)

        else:
            self.check_win(player, action)


                
    ## rolls for a player to win (1/10)
    def check_win(self, player, action):
        print('\nPUNCH:')
        roll = int(random.uniform(0,self.ko_rate + 1))
        # if 0, 1   if 1, 0
        other_player = (player + 1) % 2
        # message to send back to player
        message = ''
        # type of message
        message_type = 'action'
        # if action is punch left
        if action == 'q': 
            # change block left time to 0
            self.players[player][0] = 0
            # if other player is blocking left
            if self.players[other_player][0] + 3 < time.time():
                # if we roll a 5, hit
                if roll == 5:
                    message = '\tp' + str(player + 1) + ' land left punch\n'
                    self.quit(True, player)
                    message_type = 'win'
                # if not, miss
                else:
                    message = '\tp' + str(player + 1) + ' miss left punch\n'
            # if other player is blocking right, blocked
            else:
                message = '\tp' + str(player + 1)  + ' left punch blocked\n'
        # if action is punch right
        else:
            self.players[player][1] = 0
            # if other player is blocking right
            if self.players[other_player][1] + 3 < time.time():
                # if we roll a 5, hit
                if roll == 5:
                    message = '\tp' + str(player + 1) + ' land right punch\n'
                    self.quit(True, player)
                    message_type = 'win'
                # if not, miss
                else:
                    message = '\tp' + str(player + 1) + ' miss right punch\n'
            # if other player is blocking left, blocked
            else:
                message = '\tp' + str(player + 1)  + ' right punch blocked\n'

        # print message on leader 
        print(message)
        print('\nCURRENT TIME: \t', int(time.time()))
        print('\n[LEFT, RIGHT] TIMESTAMPS:\n p1:\t', self.players[0], '\n p2:\t', self.players[1], '\n')

        # send message to all clients
        for i in range(5,7):
            m = create_server_message(str(i), message_type, [player, message])
            self.send_message(m)

    ## end all processes
    def quit(self, win=False, player=None):
        self.poll = False

        if win:
            print('\n\n !!! p' + str(player + 1), 'WINS !!!\n\n')
            for i in range(self.processes):
                if str(i) != self.id:
                    message = create_end_message(str(i))
#                    print('sending message to', i, ':', message)
                    self.send_message(message)

#        else:
#            for i in range(5,7):
#                message = create_server_message(str(i), 'quit', '')
#                self.send_message(message)

        while len(self.log) - 1 > self.commit_index:
            self.log.pop()

        print('final committed log:', self.log)
        return

    ## handle request from client
    def receive_client_request(self, client_request):
#        print('\nclient request:', client_request)
        client_request = json.loads(client_request[1:])
        player = client_request[1]
        action = client_request[2]
        self.add_to_log(self.term, player, action)
        self.send_append_entries()

    ## add to log
    def add_to_log(self, term, player, action, index=None):
        entry = [term, player, action] 
#        print('\nnew entry:', entry)

        # if the index is right after the log or no index given, append
        if index == len(self.log) or index == None:
            self.log.append(entry)
            self.adds.append(1)
        # else if index is before end of log, replace entry
        elif index < len(self.log):
            self.log[index] = entry
        else:
            self.log.append(entry)
            print('log is missing an entry')

#        print('\nnew log:', self.log)

    ## clear queue of messages from last run
    ## @param del_all - if False, only delete messages for this process
    def clear_queue(self, del_all=False):
        my_queue = int(self.id)

        print('clearing queue', end='')
        if del_all:
            print(' of all messages.')
        else:
            print(' of messages for this process.')

        # clear queue for 5 seconds
        clear_timeout = time.time() + 5 
        # receive message
        while time.time() < clear_timeout:
            response = self.sqs.receive_message(QueueUrl=self.q_url[my_queue],)
            if 'Messages' in response.keys():
                # get message from queue as string
                message = response['Messages'][0]
                # get receipt handle for deletion
                receipt_handle = message['ReceiptHandle']
                # get message text
                message = message.get('Body')

                if message[:1] == self.id or del_all:
                    # if we see a new message, increment timeout
                    clear_timeout = time.time() + 5 
                    # print received message
#                    print('\nmessage to delete:', message)
                    # delete received message
                    self.sqs.delete_message(QueueUrl=self.q_url[int(self.id)], ReceiptHandle=receipt_handle)

    def poll_queue(self):
        my_queue = int(self.id)
        heartbeat_time = time.time() + 15
        self.clear_queue()
        print('Begin polling...')
        self.timeout = time.time() + random.uniform(0, 10)
        while self.poll:

            if self.state != 'failed':

                if self.simulate:
                    self.generate_cleint_request()

                if self.state == 'leader' and time.time() > heartbeat_time:
#                    print('sending  heartbeat')
                    heartbeat_time = time.time() + 15
                    self.send_append_entries()

                # check for timeout
                if time.time() > self.timeout:
                    # if timeout, call timeout 
                    self.to()
                    self.timeout_count += 1
                    if self.timeout_count > 10:
                        self.poll = False
                        
                # receive message
                response = self.sqs.receive_message(QueueUrl=self.q_url[my_queue],)
                if 'Messages' in response.keys():
                    # get message from queue as string
                    message = response['Messages'][0]
                    # get receipt handle for deletion
                    receipt_handle = message['ReceiptHandle']
                    # get message text
                    message = message.get('Body')

                    # check to see if this message is for me
                    if message[:1] == self.id:
                        self.timeout = time.time() + get_timeout()
 #                       print('This message is for me:')
                        # check to see if it is a request election
                        if json.loads(message[1:])[0] == "0":
#                            print('received request_vote')
                            self.receive_request_vote(message)
                        elif json.loads(message[1:])[0] == "1":
#                            print('received request_vote reply')
                            self.receive_election_reply(message)
                        elif json.loads(message[1:])[0] == "2":
#                            print('received append entries')
                            self.receive_append_entries(message)
                        elif json.loads(message[1:])[0] == "3":
#                            print('received append reply')
                            self.receive_append_reply(message)
                        elif json.loads(message[1:])[0] == "4" and self.state == 'leader':
#                            print('received client_request')
                            self.receive_client_request(message)
                        elif json.loads(message[1:])[0] == "5":
#                            print('received commit_message')
                            self.receive_commit_message(message)
                        elif json.loads(message[1:])[0] == "6":
#                            print('received end_message')
                            self.quit()
                        else:
#                            print('this message is not for me:\n\t' + message[1:])
                            pass
                        # print received message
#                        print('\nmessage:', message)
                        # delete received message
                        self.sqs.delete_message(QueueUrl=self.q_url[my_queue], ReceiptHandle=receipt_handle)

    ## timeout method
    def to(self):
        # if timeout, reset these values
        self.votes = 0
        self.voted_for = None
        self.leader = None
        # reset timeout
        self.timeout = time.time() + get_timeout()

        # if we were in an election, wait for a bit
        if self.state == 'election':
            print('this election failed, going back to follower')
            # add an extra 20 seconds to allow for more time in follower than election
            self.timeout += 20
            self.state = 'follower'
        # if we were not in an election, start an election
        elif self.state != 'failed':
            self.state = 'election'
            self.begin_election()

    ## sends current log
    def send_message(self, message):
        # for each process in entry, create message
#        print('sending message:', message)
        address = int(message[:1])
        response = self.sqs.send_message(QueueUrl=self.q_url[address], MessageBody=message)

if __name__ == '__main__':

    # if given input, set as id
    if len(sys.argv) > 1 and sys.argv[1] != 'clear':
        server = Server(sys.argv[1])
        ui = ui.ui(server)
        
        # grab that simulate flag if it exits
        if len(sys.argv) > 2:
            server.simulate = True

        # create list of threads
        threads_L = []

        # create thread for polling
        threads_L.append(threading.Thread(name='poll', target=server.poll_queue))
        threads_L.append(threading.Thread(name='ui', target=ui.run))
            
        # start threads
        for thread in threads_L:
            thread.start()

        # join threads
        for thread in threads_L:
            thread.join()

        time.sleep(5)
        server.clear_queue()
    elif len(sys.argv) > 1 and sys.argv[1] == 'clear':
        server = Server()
        server.clear_queue(True)
    else:
        print('I need some input (0/1/2/3/4/clear)')

