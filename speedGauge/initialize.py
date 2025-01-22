import settings
import sqlite3
from pathlib import Path

'''
this module is meant to run when
making a clone or a branch or what-
ever. it will make the directories
that are needed, and and will build 
the database so it is ready to
process in the spreadsheets. 
'''

def build_dirs():
	'''
	builds the directories the program
	will need but that we dont need git
	to track
	'''
	
