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

'''
List of functions
-----------------

build_imgStorage_tbl
get_manager
get_max_date
get_all_dates
gather_driver_ids
gather_driver_data
gather_historical_driver_data

'''

def build_imgStorage_tbl():
	'''creates the imgStorage table used for storing plots and stuff'''
	conn = settings.db_connection()
	c = conn.cursor()
	
	# Create tables if they don't already exist
	imgStorage_tblName = settings.imgStorage
	
	imgStorage_columns = ', '.join([f'{col_name} {col_type}' for col_name, col_type in settings.imgStorageTbl_column_info.items()])
	
	# build table
	sql = f'CREATE TABLE IF NOT EXISTS {imgStorage_tblName} ({imgStorage_columns})'
	c.execute(sql)
	
	# commit and close
	conn.commit()
	conn.close()

def get_manager(driver_id):
	conn = settings.db_connection()
	c = conn.cursor()
	
	sql = f'SELECT manager FROM {settings.driverInfo} WHERE driver_id = ?'
	value = (driver_id,)
	c.execute(sql, value)
	result = c.fetchone()
	conn.close()
	
	if result != None:
		manager = result[0]
		return manager
	else:
		return None

def get_max_date():
	'''
	returns the highest start_date in
	the database
	'''
	conn = settings.db_connection()
	
	c = conn.cursor()
	sql = f'SELECT MAX (start_date) FROM {settings.speedGaugeData}'
	c.execute(sql)
	result = c.fetchone()[0]
	
	conn.close()
	return result

def get_all_dates():
	'''
	returns list of each start_date in
	the database
	'''
	date_list = []
	
	conn = settings.db_connection()
	c = conn.cursor()
	
	sql = f'SELECT DISTINCT start_date FROM {settings.speedGaugeData} ORDER BY start_date ASC'
	
	c.execute(sql)
	results = c.fetchall()
	for date in results:
		date_list.append(date[0])
		
	conn.close()
	return date_list

def gather_driver_ids(rtm='chris'):
	'''
	returns all the driver numbers for
	a given rtm 
	
	if rtm = none, then returns ALL 
	driver numbers
	'''
	
	id_list = []
	
	conn = settings.db_connection()
	c = conn.cursor()
	
	if rtm != 'none':
		sql = f'SELECT driver_id FROM {settings.driverInfo} WHERE rtm = ? '
		value = (rtm,)
		
		c.execute(sql, value)
		results = c.fetchall()
		
		for result in results:
			id_list.append(result[0])
	
	else:
		sql = f'SELECT driver_id FROM {settings.driverInfo}'
		
		c.execute(sql)
		results = c.fetchall()
		
		for result in results:
			id_list.append(result[0])
	
	conn.close()
	return id_list

def gather_driver_data(id_list, date):
	'''
	takes in a list of driver_ids and 
	returns a list full of dictionaries
	
	dictionary keys:
		driver_id
		driver_name
		percent_speeding
	
	this is limited to most recent
	date in the database
	'''
	
	print('Gathering driver data...')
	
	tbl = settings.speedGaugeData
	data_packets = []
	#max_date = get_max_date()
	conn = settings.db_connection()
	c = conn.cursor()
	
	for driver_id in id_list:
		sql = f'SELECT driver_name, percent_speeding FROM {tbl} where driver_id = ? AND start_date = ?'
		values = (driver_id, date)
		
		c.execute(sql, values)
		result = c.fetchone()
		
		if result != None:
			driver_name = result[0]
			percent_speeding = result[1]
			
			data_packet = {
				'driver_id': driver_id,
				'percent_speeding': percent_speeding,
				'driver_name': driver_name
			}
			
			data_packets.append(data_packet)

	conn.close()
	return data_packets

def gather_historical_driver_data(id_list):
	'''
	takes in a list of driver_id and
	returns mean and avg for each date
	in the db
	
	returns dict with these keys:
		date
		mean
		median
	
	use this to make line plot showing
	historical trends.
	
	there should be one dictionary per
	date
	'''
	print('Gathering historical driver data...')
	
	tbl = settings.speedGaugeData
	stats = []
	date_list = get_all_dates()
	
	conn = settings.db_connection()
	c = conn.cursor()
	
	for date in date_list:
		speed_list = []
		
		for driver_id in id_list:
			sql = f'SELECT percent_speeding FROM {tbl} WHERE start_date = ? AND driver_id = ?'
			values = (date, driver_id)
			
			c.execute(sql, values)
			results = c.fetchone()
			
			if results != None:
				percent_speeding = results[0]
				
				speed_list.append(percent_speeding)

		mean = statistics.mean(speed_list)
		median = statistics.median(speed_list)
		
		stats_dict = {
			'date': date,
			'mean': mean,
			'median': median
		}
		
		stats.append(stats_dict)
	
	conn.close()
	return stats

def get_info(driver_id):
	conn = settings.db_connection()
	c = conn.cursor()
	tbl = settings.driverInfo
	
	sql = f'SELECT * FROM {tbl} WHERE driver_id = ?'
	value = (driver_id,)
	c.execute(sql, value)

	result = c.fetchone()
	for i in result:
		print(i)

if __name__ == '__main__':
	#build_imgStorage_tbl()
	pass
