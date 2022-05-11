import sys
import os
import PyhpScript as pyhp
import time

class exempleScript(pyhp.ScriptHandler):
	def __init__(self, valueToSave):
		super().__init__()
		self.valueToSave = valueToSave

	def run(self):
		self.dataHandler.modifData('valueExemple', self.valueToSave)



time.sleep(10)
sh = exempleScript({"yo" : 10, "test2" : "Slt", "test4" : False});
sh.run()
print("Sortie stdout")