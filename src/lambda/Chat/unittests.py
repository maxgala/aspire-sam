import unittest
import json

import CreateChat as create
import DeleteChatById as delete
import EditChatById as edit
import GetAllChats as get_all
import GetChatById as get
import ReserveChatById as reserve
import UnreserveChatById as unreserve

class TestCreateChat(unittest.TestCase):
    ''' Test case for CreateChat endpoint
    '''

    event = json.dump({
            })
