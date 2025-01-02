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

def db_connection():
	# returns a connection
	dbName = settings.DB_PATH
	conn = sqlite3.connect(dbName)
	
	return conn

def get_all_dates():
	'''
	returns list of each start_date in
	the database
	'''
	
	tbl = 'speedGaugeData'
	date_list = []
	
	conn = db_connection()
	c = conn.cursor()
	
	sql = f'SELECT DISTINCT start_date FROM {tbl} ORDER BY start_date ASC'
	
	c.execute(sql)
	results = c.fetchall()
	for date in results:
		date_list.append(date[0])
		
	conn.close()
	return date_list

def update_ids():
	'''
	used to check for new drivers and 
	update the driverInfo table. 
	Sometimes the new id's come in as
	strings instead of integers, so we
	gotta clean that up first
	'''
	conn = db_connection()
	c = conn.cursor()
	
	id_list = []
	new_ids = []
	
	# get list of known, good ids
	sql = f'SELECT DISTINCT driver_id FROM driverInfo'
	c.execute(sql)
	results = c.fetchall()
	for i in results:
		id_list.append(i[0])
	
	# check for any new ids in db
	sql = f'SELECT DISTINCT driver_id FROM {settings.tbl_name}'
	c.execute(sql)
	results = c.fetchall()
	for i in results:
		if i[0] not in id_list:
			new_ids.append(i[0])
	
	# print out update
	console.clear()
	print('New driver_ids found.')
	for i in new_ids:
		print(i)
	
	# make sure to change from str to 
	# int
	id_dict = {}
	for i in new_ids:
		sql = f'SELECT driver_id FROM {settings.tbl_name} WHERE driver_id = ?'
		value = (i,)
		c.execute(sql, value)
		result = c.fetchone()
		if result != None:
			cleaned_id = int(float(result[0]))
			id_dict[result[0]] = cleaned_id
	
	for i in id_dict:
		sql = f'UPDATE {settings.tbl_name} SET driver_id = ? WHERE driver_id = ?'
		values = (id_dict[i], i)
	
	conn.commit()
	conn.close()
	return id_list











def fill_missing_speeds():
	conn = db_connection()
	c = conn.cursor()
	
	dates = get_all_dates()
	
	
	
	
	
	
	conn.close()



if __name__ == '__main__':
	update_ids()
