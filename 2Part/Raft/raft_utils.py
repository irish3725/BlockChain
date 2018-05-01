
import json
import random

# returns a random number between 8 and 10
def get_timeout():
    timeout = random.uniform(20,40)
    #print('new timeout in', int(timeout), 'seconds.')
    return timeout

# creates log entry (list) in the form of:
#   [<term>, <requestor>, <action>]
def create_log_entry(term, requestor, action):
    return([term, requestor, action, '0'])

# returns request_vote (string) message in the form of:
#   <receiver_id>[0, <sender_id>, <log_index>, <log_entry>, <new_term>]
def create_request_message(receiver, sender, log_index, log_entry, new_term):
    message_contents = json.dumps(['0', sender, log_index, log_entry, new_term])
    return(receiver + message_contents)

# returns request_vote_reply (string) message in the form of:
#   <receiver_id>[1, <sender_id>, <voted_for (true, false)>]
def create_request_reply(receiver, sender, vote):
    message_contents = json.dumps(['1', sender, vote])
    return(receiver + message_contents)

# returns append_entries (string) message in the form of:
#   <receiver_id>[2, <sender_id>, <log_index>, <log_after(and including)_index>, <term>]
def create_append_message(receiver, sender, log_index, log_after_index, term):
    message_contents = json.dumps(['2', sender, log_index, log_after_index, term])
    return(receiver + message_contents)

# returns append_entries_reply (string) message in the form of:
# returns append_entries_reply (string) message in the form of:
#   <receiver_id>[3, <sender_id>, <last_add_index(last commit if no add)>]
def create_append_reply(receiver, sender, last_add_index):
    message_contents = json.dumps(['3', sender, last_add_index])
    return(receiver + message_contents)

#   <receiver_id>[4, <sender_id>, <action(q/w/a/s)>]
def create_client_request(receiver, sender, action):
    message_contents = json.dumps(['4', sender, action])
    return(receiver + message_contents)

#   <receiver_id>[4, <sender_id>, <commit_index>, <entry_to_commit>]
def create_commit_message(receiver, sender, index, entry):
    message_contents = json.dumps(['5', sender, index, entry])
    return(receiver + message_contents)

#   <receiver_id>[4, <sender_id>, <commit_index>, <entry_to_commit>]
def create_end_message(receiver):
    message_contents = json.dumps(['6'])
    return(receiver + message_contents)

#   <receiver_id>[4, <sender_id>, <message_type>, <message>]
def create_server_message(receiver, message_type, message):
    message_contents = json.dumps(['7', message_type, message])
    return(receiver + message_contents)

