import calendar
import utils

class ui:

    ## @param cal - calendar object that will be interated with
    def __init__(self, server):
        self.server = server 

    ## main ui loop
    def run(self):  
        # value to read input into 
        val = ''

        while val != 'q' and val != 'quit' and val != 'exit' and self.server.poll:
            val = input('(fail/recover/timeout/quit) > ').lower()

            # adding an event
            if val == 'fail':
                self.server.fail()
                val = ''
            if val == 'recover':
                self.server.recover()
                val = ''
            if val == 'timeout' or val == 'to':
                self.server.to()
                val = ''

        self.server.poll = False

