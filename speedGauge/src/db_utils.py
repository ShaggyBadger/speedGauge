import sys
import os
import sqlite3
import console
import statistics
import math

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Now you can import settings
import settings
from src import analysis

'''
list of functions:
------------------

build_db
get_driver_ids
get_max_date
display_tbl_info
display_driver_speed
insert_data
generate_db
driver_history
collect_latest_speeding
add_new_col
update_id
get_driver_id
delete_driver
collect_all_speeding
historical_data
collet_start_dates
stats_over_time

'''


def build_db():
	conn = settings.db_connection()





def gather_driver_ids(manager='chris'):
	'''
	returns all the driver numbers for
	a given rtm 
	
	if rtm = none, then returns ALL 
	driver numbers
	'''
	dbName = settings.DB_PATH
	id_list = []
	
	conn = sqlite3.connect(dbName)
	c = conn.cursor()
	if manager != 'none':
		sql = f'SELECT driver_id FROM driverInfo WHERE rtm = ? '
		value = (manager,)
		
		c.execute(sql, value)
		results = c.fetchall()
		
		for result in results:
			id_list.append(result[0])
	
	else:
		sql = f'SELECT driver_id FROM driverInfo'
		
		c.execute()
		results = c.fetchall()
		
		for result in results:
			id_list.append(result[0])
	
	conn.close()
	
	return id_list
	








def get_max_date(tbl='speedGaugeData'):
	'''
	quick function to get the latest
	date in the db
	
	tbl is speedGaugeData by default
	
	also, this is start_date, not 
	end_date. someday ill find out how
	to make any date work, but not now
	'''
	
	dbName = settings.DB_PATH
	
	conn = sqlite3.connect(dbName)
	c = conn.cursor()
	
	sql = f'SELECT MAX (start_date) FROM {tbl}'
	c.execute(sql)
	max_date = c.fetchone()[0]
	
	return max_date








def filter_date(date=get_max_date()):
	'''
	default is to use the current
	max_date, but you can override if
	you want
	
	this takes in the date that has the
	time component attached and strips
	the time off.
	
	it returns just the date portion
	i.e., 12-03-24
	'''
	
	return date.split(' ')[0]




def display_tbl_info(tbl='speedGaugeData'):
	'''
	quick way to get a printout of
	columns etc for a given table
	'''
	dbName = settings.DB_PATH
	
	conn = sqlite3.connect(dbName)
	c = conn.cursor()
	
	c.execute(f'PRAGMA table_info({tbl})')
	results = c.fetchall()
	print(f'\n{tbl}\n-----')
	for i in results:
		col_name = i[1]
		col_type = i[2]
		
		print(f"'{col_name}': '{col_type}',")
	






def display_driver_speed(driverNum=None, return_list=False):
	'''
	quick function so i dont have to
	keep writting custom scripts to look at driver intel
	
	set driverNum to specific driver if 
	needed, otherwise this will print
	out all the drivers from most
	recent report
	
	** driverNum needs to come in as a
	string, but ill fix it in the
	function just in case **
	
	functuon returns the list of 
	dictionaries if return_list is
	set to True. otherwise it just
	prints stuff out
	'''
	# establis db connection
	dbName = settings.DB_PATH
	
	conn = sqlite3.connect(dbName)
	c = conn.cursor()
	
	# set some variables and stuff
	tbl = 'speedGaugeData'
	max_date = get_max_date()
	intel_dicts = []
	
	# sql and value to get data from
	# database
	sql = f'SELECT driver_name, driver_id, percent_speeding FROM {tbl} WHERE start_date = ?'
	value = (max_date,)
	
	# get the info from db
	c.execute(sql, value)
	results = c.fetchall()
	
	# process data into dictionaries
	for row in results:
		dict = {
			'driver_name': row[0],
			'driver_id': row[1],
			'speed_percent': row[2]
			}
		
		# append all dictionaries
		if driverNum is None:
			intel_dicts.append(dict)
		
		# append specified driver only	
		else:
			intel_dicts.append(dict) if dict['driver_id'] == str(driverNum) else None
	
	conn.close()
	
	# final processing
	# return list if that argument was
	# set to True
	if return_list is True:		
		return intel_dicts
	
	# normally we just gonna print the
	# data
	else:
		for dict in intel_dicts:
			for i in dict:
				print(f'{i}: {dict[i]}')
			
			print('-------\n')
		
		print(f'number of drivers: {len(intel_dicts)}')
			 
	
	
	
	
	










def insert_data(dict, tbl):
	'''
	takes in a dictionary full of the
	row information for db insertion
	as well as what table to insert
	into. 
	
	then it checks to see if record
	already exists, and if not then
	it goes ahead and inserts the data
	
	currently only works with inserting
	spreadsheet data. need to consider 
	updating dict to have a key that
	is used for what column to check
	i.e. dict['chk_colum'] and the
	value would be the name of the
	column we want to check
	'''
	
	# put together the data
	dbName = settings.DB_PATH
	driver_name = dict['driver_name']
	start_date = dict['start_date']
	
	# connect to db
	conn = sqlite3.connect(dbName)
	c = conn.cursor()
	
	# update columns
	for column in dict:
		c.execute(f'PRAGMA table_info ({tbl})')
		results = c.fetchall()
		
		# Extract just the column names into a list
		tbl_columns = [result[1] for result in results]
		
		if column not in tbl_columns:
			print(f'Encountered new column in the spreadsheet: {column}. Inserting into database table')
			c.execute(f'ALTER TABLE {tbl} ADD COLUMN {column} TEXT')
			
	conn.commit()
			
	
	# check if entry already exists
	sql = f'SELECT * FROM {tbl} WHERE driver_name = ? AND start_date = ?'
		
	values = (driver_name, start_date)
	
	c.execute(sql, values)
	results = c.fetchone()
	
	if results is None:	
		# build sql insertion
		columns = ', '.join(dict.keys())
		placeholders = ', '.join(['?' for _ in dict])
			
		sql = f'INSERT INTO {tbl} ({columns}) VALUES ({placeholders})'
			
		values = tuple(dict.values())
			
		# insert data
		c.execute(sql, values)
	
	# commit changes and close db
	# dont commit that dumb record 
	# named median
	if driver_name != 'median':
		conn.commit()
		
	conn.close()
	
	
	
	
	
	
	
	
	
	
	
	
	
def generate_db(debug=False):
	'''generates db and tables. 
	debug can be set to True to
	print out table column info
	to verify correct generetion
	'''
	
	# get table dict from settings
	table_dict = settings.db_column_intel
	
	# table for driver info
	driverInfo = '''
		CREATE TABLE IF NOT EXISTS
		driverInfo(
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			driverName TEXT,
			driverNumber INTEGER
			)
	'''
	
	# table for spreadsheet data
	speedGaugeData = '''
		CREATE TABLE IF NOT EXISTS
		speedGaugeData(
			id INTEGER PRIMARY KEY AUTOINCREMENT,\n
	'''
	
	# dynamically add in the column
	# names from settings
	for column_name, data_type in table_dict.items():
		speedGaugeData += f'{column_name} {data_type},\n'
	
	# removes last comma and ends sql 
	# statement
	speedGaugeData = speedGaugeData.rstrip(",\n") + "\n);"
	
	# make list of tables to create
	table_list = [
		speedGaugeData,
		driverInfo
		]
	
	# connect to the db
	conn = sqlite3.connect(settings.DB_PATH)
	c = conn.cursor()
	
	# create tables
	for table in table_list:
		c.execute(table)
	
	# commit changes and close
	conn.commit()
	
	# print out column info
	if debug is True:
		tables = [
			'driverInfo',
			'speedGaugeData'
			]
			
		for table in tables:
			c.execute(f'PRAGMA table_info({table})')
			results = c.fetchall()
			print(f'\n{table}\n-----')
			for i in results:
				print(i)
	
	conn.close()
	
	
	
	
	
	
	
	
	
	
	
	
	
	
def driver_history(driver_id):
	'''
	collects all records for a given
	driver_id. 
	
	**id should be str, but i'll mod
	it in the function to be str just
	in case**'
	
	then we bundle them up into a list
	and return that list for further
	processing
	'''
	# connect to db
	dbName = settings.DB_PATH
	tbl = 'speedGaugeData'

	conn = sqlite3.connect(dbName)
	c = conn.cursor()
	max_date = get_max_date()
	
	# make container for col_names
	col_names = [] # column names
	
	# get col names and put in list
	c.execute(f'PRAGMA table_info({tbl})')
	results = c.fetchall()
	for i in results:
		col_name = i[1]
		col_names.append(col_name)
		
	# make sql insertion
	col_str = ', '.join(col_names)
	
	# get all records for driver data
	sql = f'SELECT {col_str} FROM {tbl} WHERE driver_id = ? ORDER BY end_date ASC'
	value = (driver_id,)
	
	c.execute(sql, value)
	results = c.fetchall()

	intel_packets = []
	
	for row in results:
		test = dict(zip(col_names, row))
		intel_packets.append(test)

	
	return intel_packets

		

	
	
	
	
	
	
	
	
	
	
	
	
	
	
def collect_latest_speeding(rtm='no ne', applyFilter=True):
	'''
	builds dictionaries of driver
	info, sticks them in a list,
	and returns the list
	
	info included is:
		driver_name
		percent_speeding
		driver_id
		
	pretty straight forward. this only
	collects the data for the most
	recent entries in the db. 
	
	applyFilter will only return driver
	if belongs to chris area
	'''
	dbName = settings.DB_PATH
	tbl = 'speedGaugeData'
	
	conn = sqlite3.connect(dbName)
	c = conn.cursor()
	
	sql = f'SELECT MAX (start_date) FROM {tbl}'
	c.execute(sql)
	max_date = c.fetchone()[0]
	
	if applyFilter is False:
		sql = f'SELECT driver_name, percent_speeding, driver_id FROM {tbl} WHERE start_date = ?'
		value = (max_date,)
		c.execute(sql, value)
		results = c.fetchall()
		#print(results)
		
		data_packages = []
		
		for record in results:
			driver_name = record[0]
			percent_speeding = record[1]
			driver_id = record[2]
			
			data_package = {
				'driver_name': driver_name,
				'percent_speeding': percent_speeding,
				'driver_id': driver_id
			}
			data_packages.append(data_package)
			
		conn.close()
		
		return data_packages
	
	else:
		valid_ids = []
		sql = f'SELECT driver_id FROM driverInfo WHERE rtm = ?'
		value = ('chris',)
		c.execute(sql, value)
		results = c.fetchall()
		for result in results:
			valid_ids.append(result[0])
		
		
		sql = f'SELECT driver_name, percent_speeding, driver_id FROM {tbl} WHERE start_date = ?'
		value = (max_date,)
		c.execute(sql, value)
		results = c.fetchall()
		#print(results)
		
		data_packages = []
		
		for record in results:
			driver_name = record[0]
			percent_speeding = record[1]
			driver_id = record[2]
			
			data_package = {
				'driver_name': driver_name,
				'percent_speeding': percent_speeding,
				'driver_id': driver_id
			}
			
			if driver_id in valid_ids:
				data_packages.append(data_package)

		conn.close()
		
		return data_packages
		
	
	










def add_new_col(tbl, col_name, colType='TEXT'):
	'''
	function to easily add column
	to a table.
	
	tbl = table name
	col_name = new column to add
	'''
	
	dbName = settings.DB_PATH
	
	conn = sqlite3.connect(dbName)
	c = conn.cursor()
	
	c.execute(f'PRAGMA table_info({tbl})')
	
	columns = [col[1] for col in c.fetchall()]
	
	if col_name not in columns:
		c.execute(f'ALTER TABLE {tbl} ADD COLUMN {col_name} COLUMN TYPE {colType}')
	
		conn.commit()
	
	c.execute(f'PRAGMA table_info({tbl})')
	results = c.fetchall()
	print(f'\n{tbl}\n-----')
	for i in results:
			print(i[1])
	
	conn.close()
	









def update_id(print_report=True):
	'''
	updates all rows in db with correct
	driver number
	
	prints out a report at the end by default
	'''
	
	dbName = settings.DB_PATH
	
	conn = sqlite3.connect(dbName)
	c = conn.cursor()
	
	sql = '''UPDATE speedGaugeData
	SET driver_id = (
		SELECT driverNumber FROM driverInfo
		WHERE driverInfo.driverName = speedGaugeData.driver_name
		)
	WHERE EXISTS (
		SELECT 1 FROM driverInfo 
		WHERE driverInfo.driverName = speedGaugeData.driver_name
		)
		'''
	
	c.execute(sql)
	conn.commit()
	
	if print_report is True:
		sql = f'SELECT MAX (start_date) FROM speedGaugeData'
		c.execute(sql)
		max_date = c.fetchone()[0]
		
		sql = f'SELECT driver_name, driver_id FROM speedGaugeData WHERE start_date = ?'
		value = (max_date,)
		c.execute(sql, value)
		results = c.fetchall()
		
		for i in results:
			print(i[0], i[1])
			
	conn.close()
	
	
	
	

	
	
	
	
	
def get_driver_id(driverName):
	'''
	simple function to get driver id
	for a goven driverName
	
	currently using this to properly
	insert driver_id when processing 
	a new spreadsheet
	''' 
	dbName = settings.DB_PATH
	
	conn = sqlite3.connect(dbName)
	c = conn.cursor()
	
	sql = 'SELECT driverNumber FROM driverInfo WHERE driverName = ?'
	value = (driverName,)
	
	c.execute(sql, value)
	result = c.fetchone()
	conn.close()
	
	if result is None:
		return result
	
	else:
		return result[0]








def delete_driver(name='median', tbl='speedGaugeData'):
	'''
	deletes a driver's records from
	the database. default is set to
	that annoying median name, but
	you can override it to be any name
	you want
	
	it might be a good idea to use
	driverNum, then get name based on
	that. that way you dont have ro 
	mess around with spelling and case
	'''
	dbName = settings.DB_PATH
	
	conn = sqlite3.connect(dbName)
	c = conn.cursor()
	
	sql = f'DELETE FROM {tbl} WHERE driver_name = ?'
	value = (name,)
	
	c.execute(sql, value)
	
	conn.commit()
	conn.close()
	
	print(f'{name} has been deleted from the database')











def collect_start_dates():
	'''
	makes a sorted list of start_date 
	and returns the list
	'''
	
	dbName = settings.DB_PATH
	tbl = 'speedGaugeData'
	
	conn = sqlite3.connect(dbName)
	c = conn.cursor()
	
	sql = f'SELECT DISTINCT start_date FROM {tbl} ORDER BY start_date'
	
	c.execute(sql)
	results = c.fetchall()
	
	start_dates = []
	for i in results:
		start_dates.append(i[0])
	
	conn.close()
	
	return start_dates











def stats_over_time(print_data=False, applyFilter = False, rtm='chris'):
	dbName = settings.DB_PATH
	tbl = 'speedGaugeData'
	start_dates = collect_start_dates()
	
	conn = sqlite3.connect(dbName)
	c = conn.cursor()
	
	stat_list = []
	
	for date in start_dates:
		sql = f'SELECT driver_name, driver_id, percent_speeding FROM {tbl} WHERE start_date = ?'
		
		value = (date,)
		
		c.execute(sql, value)
		results = c.fetchall()
		
		data_packets = []
		
		for i in results:
			data_dicts = {}
			
			data_dicts['driver_name'] = i[0]
			data_dicts['driver_id'] = i[1]
			data_dicts['percent_speeding'] = i[2]
			
			if applyFilter is False:
				data_packets.append(data_dicts)
			
			else:
				valid_ids = []
				
				sql = f'SELECT driver_id FROM driverInfo WHERE rtm = ?'
				value = (rtm,)
				c.execute(sql, value)
				results = c.fetchall()
				for result in results:
					valid_ids.append(result[0])
				
				if data_dicts['driver_id'] in valid_ids:
					data_packets.append(data_dicts)
		
			
		# run analysis on data packets
		analetics = analysis.data_stats(data_packets)
		
		'''
		analetics is a dictionary with
		the following keys:
			irq_outlier
			standard_deviation
			raw_mean
			median
		'''
		
		analysis_dict = {
			'start_date': date,
			'analasis': analetics
		}
		
		# save the analysis
		stat_list.append(analysis_dict)
	
	if print_data is True:
		for date in start_dates:
			for dict in stat_list:
				if dict['start_date'] == date:
					analetic_dict = dict['analasis']
					print(f'Date: {date}')
					print(f'Median speeding percentage: {analetic_dict["median"]}')
					print(f'Average speeding score: {analetic_dict["raw_mean"]}')
					print('---------\n')
					
	conn.close()
	
	return stat_list
	










def build_local_driver_list():
	'''
	kind of a one time function to 
	update the database with chris as
	rtm for known peeps. this way i can
	run filtered queries just for our
	market
	'''
	
	dbName = settings.DB_PATH
	tbl = 'speedGaugeData'
	start_dates = collect_start_dates()
	
	conn = sqlite3.connect(dbName)
	c = conn.cursor()
	
	for date in start_dates:
		sql = f'SELECT driver_name, driver_id FROM {tbl} WHERE start_date = ?'
		value = (date,)
		
		c.execute(sql, value)
		results = c.fetchall()
		
		num_drivers = len(results)
		
		print(f'Date: {date}')
		print(f'Number of drivers: {num_drivers}')
		print('----------\n')
	
	
	driver_list = []
	
	target_date = start_dates[-2]
	sql = f'SELECT driver_name, driver_id FROM {tbl} WHERE start_date = ?'
	value = (target_date,)
	c.execute(sql, value)
	results = c.fetchall()
	for i in results:
		if i[1] != None:
			num = int(i[1])
			if num not in driver_list:
				driver_list.append(num)
			
	target_date = start_dates[-3]
	sql = f'SELECT driver_name, driver_id FROM {tbl} WHERE start_date = ?'
	value = (target_date,)
	c.execute(sql, value)
	results = c.fetchall()
	for i in results:
		if i[1] != None:
			num = int(i[1])
			if num not in driver_list:
				driver_list.append(num)
			
	print(len(driver_list))
	
	
	rtm = 'chris'
	
	for driver_id in driver_list:
		sql = f'UPDATE driverInfo SET rtm = ? WHERE driverNumber = ?'
		values = (rtm, driver_id)
		
		c.execute(sql, values)
	
	conn.commit()
	
	sql = f'SELECT driverName, driverNumber, rtm FROM driverInfo WHERE rtm = ?'
	value = (rtm,)
	
	c.execute(sql, value)
	results = c.fetchall()
	
	for i in results:
		print(i)
		print('------------\n')
	
	conn.close()









def build_driver_package(rtm='chris'):
	'''
	returns dict with keys:
		driver_name
		driver_id
		percent_speeding
	'''
	dbName = settings.DB_PATH
	tbl = 'speedGaugeData'
	target_date = get_max_date()()
	conn = sqlite3.connect(dbName)
	c = conn.cursor()
	
	




if __name__ == '__main__':
	display_tbl_info(tbl='driverInfo2')
	display_tbl_info('speedGaugeData2')
	build_db()
	#display_tbl_info()
	
	#display_driver_speed()
	#driver_history(30190385)
	#display_tbl_info()
