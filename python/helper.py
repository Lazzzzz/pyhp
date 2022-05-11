import sys
import json
import time
import os

def modifJsonValue(jsonDic, name, value):
	jsonDic[name] = value

class jsonHandler:
	def __init__(self, path, name, scriptId):
		self.scriptId 	= str(scriptId)
		self.name 		= name
		self.path		= path
		self.data 		= {}

	def getFullPathName(self):
		return self.path + self.scriptId + '.' + self.name + '.json'

	def modifDataAux(self, name, value):
		try:
			file = open(self.getFullPathName(), 'w')

			modifJsonValue(self.data, name, value)

			file.write(json.dumps(self.data, indent=4, sort_keys=True))
			file.close()
			return True

		except Exception as e:
			print(e)
			return False

	def modifData(self, name, value, force = False, tryCount = 10, waitInterval = 2):
		if force:
			counter = 0
			while (counter < tryCount):
				if self.modifDataAux(name, value) is False:
					print("Echec numero : {0} sur fichier : {1}".format(counter, name))
				else:
					return True

				counter += 1
				time.sleep(waitInterval)

			return False
		
		else:
			return self.modifDataAux(name, value)