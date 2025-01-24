import settings
import sqlite3
from pathlib import Path
from src import processing3
import console

'''
this module is meant to run when making a clone or a branch or whatever. it will make the directories that
are needed, and and will build the database so it is ready to process in the spreadsheets. 
'''

def build_dirs():
	'''builds the directories the program will need but that we dont need git to track'''

	# Establish dirs that might need to be built
	dir_build_list = [
		settings.BASE_DIR,
		settings.IMG_PATH,
		settings.IMG_ASSETS_PATH,
		settings.WEEKLY_REPORTS_PATH,
		settings.DATA_PATH,
		settings.UNPROCESSED_PATH,
		settings.PROCESSED_PATH,
		settings.SRC_PATH,
		settings.DATABASE_PATH
	]

	# build the directories
	for dir in dir_build_list:
		dir.mkdir(parents=True, exist_ok=True)
		print(f'Directory {dir} created...')

def build_db():
	db = settings.DB_PATH
	driverInfo_col_info = settings.driverInfoTbl_column_info
	speedGaugeData_col_info = settings.mainTbl_column_info

	driverInfo_tblName = settings.driverInfo
	speedGaugeData_tblName = settings.speedGaugeData

	conn = sqlite3.connect(db)
	c = conn.cursor()

	# Create tables if they don't already exist
	driverInfo_columns = ', '.join([f'{col_name} {col_type}' for col_name, col_type in driverInfo_col_info.items()])
	speedGaugeData_columns = ', '.join([f'{col_name} {col_type}' for col_name, col_type in speedGaugeData_col_info.items()])
	
	# create driverInfo table
	sql = f'CREATE TABLE IF NOT EXISTS {driverInfo_tblName} ({driverInfo_columns})'
	c.execute(sql)

	# create speedGaugeData table
	sql = f'CREATE TABLE IF NOT EXISTS {speedGaugeData_tblName} ({speedGaugeData_columns})'
	c.execute(sql)

	conn.commit()
	conn.close()

def populate_db():
	'''takes in all the spreadsheets and puts them into the database'''
	processing3.main()

def special_ops():
	pass

if __name__ == '__main__':
	valid_selection = False
	while valid_selection is False:
		console.clear()
		valid_selections = ['1', '2', '3']
		print('Welcome to the speedGauge initializer module! Please select what option you want to use....\n')
		selection = input('1: Build The Database\n2: Populate The Database\nEnter selection: ')
		if str(selection) in valid_selections:
			valid_selection = True
		else:
			print('Sorry, your selection was not a valid selection. Please try again...')
			input('\nPress enter to contine...')
	if selection == '1':
		build_dirs()
		build_db()
	if selection == '2':
		populate_db()
	if selection == '3':
		special_ops()
	

	
