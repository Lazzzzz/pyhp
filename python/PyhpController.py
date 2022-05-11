import sys
import json
import os
import threading
import helper
import time
import subprocess
import mysql.connector

from os import listdir
from os.path import isfile, join

from pathlib import Path
from datetime import datetime
from datetime import timedelta

CURRENT_PATH = sys.path[0]
STATUS_PATH  = CURRENT_PATH + '/status/'
DATA_PATH    = CURRENT_PATH + '/data/'
SCRIPT_PATH  = CURRENT_PATH + '/scripts/'
QUEUE_PATH   = CURRENT_PATH + '/queue/'
CONFIG_PATH  = join(CURRENT_PATH, ".env")

if not os.path.exists(CONFIG_PATH):
	file = open(CONFIG_PATH, "w")
	
	baseConfig = {
		"db_name" : "laravel",
		"table_name" : "pyphlog",
		"host" : "localhost",
		"user" : "root",
		"password" : ""
	}
	
	file.write(json.dumps(baseConfig, indent=4, sort_keys=True))
	file.close()

file = open(CONFIG_PATH, 'r')
data = json.load(file)

DB_NAME 	 = data["db_name"]
TABLE_NAME   = data["table_name"]

Path(STATUS_PATH).mkdir(parents=True, exist_ok=True)
Path(DATA_PATH).mkdir(parents=True, exist_ok=True)
Path(SCRIPT_PATH).mkdir(parents=True, exist_ok=True)
Path(QUEUE_PATH).mkdir(parents=True, exist_ok=True)

class DatabaseHandler():
	def __init__(self, host, user, password=""):
		dbConnected = False
		self.mydb = None;

		while not dbConnected:
			try:
				self.mydb = mysql.connector.connect(
					host= host,
					user= user,
					password = password
				)
				dbConnected = True
		
			except mysql.connector.Error as err:
				print("Something went wrong: {}".format(err))

		self.cursor = self.mydb.cursor()
		self.cursor.execute("USE {0};".format(DB_NAME))

		self.cursor.execute(
			"CREATE TABLE IF NOT EXISTS {0} (instanceId INT(10), name VARCHAR(128), executionStart DATETIME, executionEnd DATETIME, executionTime FLOAT(10), returncode ENUM('SUCCESS', 'ERROR'), stdout TEXT(32764), stderr TEXT(32764));"
			.format(TABLE_NAME))

	def executeCmd(self, cmd):
		self.cursor.execute(cmd)



class ScriptHandler(threading.Thread):
	def __init__(self, name, instanceId, args, db):
		super().__init__()
		self.name = name
		self.args = args
		self.instanceId = instanceId

		self.statusHandler = helper.jsonHandler(STATUS_PATH, 'status', self.instanceId)
		
		self.statusHandler.modifData('scriptName', self.name, True)
		self.statusHandler.modifData('isRunning', False, True)

		self.db = db
		self.startTime = datetime.today()

		self.db.executeCmd(
			"INSERT INTO {0} (instanceId, name, executionStart) VALUES ('{1}', '{2}', '{3}')"
			.format(TABLE_NAME, instanceId, name, self.startTime.strftime('%Y-%m-%d %H:%M:%S'))
		)


	def run(self):
		cmd = [sys.executable, join(SCRIPT_PATH, self.name + '.py ')]
		cmd.append(self.instanceId)
		
		for arg in self.args:
			cmd.append(arg)

		self.statusHandler.modifData('isRunning', True, True)
		
		result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

		resultErr = result.stderr.decode('utf-8').replace("'", "")[:32764]
		resultOut = result.stdout.decode('utf-8').replace("'", "")[:32764]

		if (result.returncode != 0):
			self.statusHandler.modifData('isRunning', False, True)
			self.setInfoDb(result.returncode, resultOut, resultErr)

			print("Requete erreur : \n  Nom -> {0}\n  Args -> {1}\n  stdout -> {3}\n  stderr -> {2}\n".format(self.name, self.args, resultOut, resultErr))
			self.isRunning = False
			return

		self.statusHandler.modifData('isRunning', False, True)
		self.setInfoDb(result.returncode, resultOut, resultErr)
		print("Requete finis : \n  Nom -> {0}\n  Args -> {1} \n".format(self.name, self.args))
		self.isRunning = False

	def setInfoDb(self, code, resultOut, resultErr):
		endTime = datetime.today();
		deltaTime = (endTime - self.startTime)

		returncode = None

		if (code == 0):
			returncode = "SUCCESS"
		else:
			returncode = "ERROR"

		self.db.executeCmd(
				"UPDATE {0} SET executionEnd = '{1}', executionTime = '{2}', returncode = '{3}', stdout = '{4}', stderr = '{5}' WHERE instanceId = '{6}';"
				.format(TABLE_NAME, endTime.strftime('%Y-%m-%d %H:%M:%S'), deltaTime.total_seconds(), returncode, resultOut, resultErr, self.instanceId)
			)

def handleNewRequest():
	return [f for f in listdir(QUEUE_PATH) if isfile(join(QUEUE_PATH, f))]

def update(dbHandler):
	queueScript = handleNewRequest()

	if queueScript:
		print("Scripts : " + str(queueScript) + "\n")

	for fileStr in queueScript:
		try:
			path = join(QUEUE_PATH, fileStr)
			file = open(path, 'r')
			data = json.load(file)
			name = data['name']
			args = data['args']
			
			file.close()
			
			scriptHandler = ScriptHandler(name, fileStr.replace(".json", ""), args, dbHandler)
			scriptHandler.start()
			os.remove(path)

			print("Requete accepter : \n  Nom -> {0}\n  Args -> {1} \n".format(name, args))

		except Exception as e:
			print(e)


def controller():
	print("Init Pyhp controller ...\n")

	dbHandler   = DatabaseHandler("localhost", "root") 

	print("Starting listening ...\n")

	while True:
		time.sleep(1)
		update(dbHandler)
		

if __name__ == "__main__":
	controller()


