import settings
import sqlite3
from pathlib import Path

'''
this module is meant to run when making a clone or a branch or whatever. it will make the directories that
are needed, and and will build the database so it is ready to process in the spreadsheets. 
'''

def build_dirs():
	'''builds the directories the program will need but that we dont need git to track'''

	# Establish dirs that might need to be built
	dir_build_list = [
		BASE_DIR,
		IMG_PATH,
		IMG_ASSETS_PATH,
		WEEKLY_REPORTS_PATH,
		DATA_PATH,
		UNPROCESSED_PATH,
		PROCESSED_PATH,
		SRC_PATH,
		DATABASE_PATH
	]

	for dir in dir_build_list:
		dir.mkdir(parents=True, exists_ok=True)
		print(f'Directory {dir} created...')

if __name__ == '__main__':
	build_dirs()

	
