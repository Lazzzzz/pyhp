import sys
import json
import os
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import helper

CURRENT_PATH = os.path.dirname(sys.path[0])
STATUS_PATH  = CURRENT_PATH + '/status/'
DATA_PATH    = CURRENT_PATH + '/data/'
SCRIPT_PATH  = CURRENT_PATH + '/scripts/'
QUEUE_PATH   = CURRENT_PATH + '/queue/'

class ScriptHandler:
	def __init__(self):
		self.instanceId = sys.argv[1]
		self.dataHandler = helper.jsonHandler(DATA_PATH, 'data', self.instanceId)

	def run(self):
		pass


