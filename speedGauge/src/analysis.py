import sys, os
# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Now you can import settings
import settings
import math
import statistics
import numpy as np
import matplotlib.pyplot as plt
import sqlite3










def data_stats(data_packet, printData=False):
	'''
	data_packet should be a dictionary
	with one of the keys being 
	speeding_percentage. also included
	in the keys is driver_name so we
	can see who is doing what
	
	maybe i should include driver
	number instead. idk. that part
	is still a little bit of a mess
	
	set printData to True to print out
	the info
	'''
	
	# all speeds for raw calculations
	data_list = []
	
	# sort the data
	for dict in data_packet:
		# p_s = percent speeding
		p_s = dict['percent_speeding']
		driver = dict['driver_name']
		
		'''
		note: please just purge this
		from the database and when
		processing spreadsheet dont
		include median with the drivers
		'''
		if driver != 'median':
			data_list.append(p_s)
		
		
	# get standard deviation
	sd = statistics.stdev(data_list)
		
	raw_mean = statistics.mean(data_list)
	
	median = statistics.median(data_list)
	
	# iqr stuff to find/filter outliers
	# just google what iqr is
	q1 = np.percentile(data_list, 25)
	q3 = np.percentile(data_list, 75)
	iqr = q3 - q1
	high_range_iqr = q3 + (iqr * 1.5)
	low_range_iqr = q1 - (iqr * 1.5)
	
	# List comprehension to get high
	# outliers only
	high_outliers = [value for value in data_list if value > high_range_iqr]
	
	if printData is True:
		print('IQR high outliers: ', high_outliers)
		print('standard deviation: ', sd)
		print('raw mean: ', raw_mean)
		print('median: ', median)
		
	analytic_package = {
		'iqr_outlier': high_outliers,
		'standard_deviation': sd,
		'raw_mean': raw_mean,
		'median': median
	}
	
	return analytic_package










def driver_comparative(analytic_package):
	'''
	compares a driver to rest of the 
	spreadsheet
	
	analyitic_package is dictionary
	with a few keys:
		
	** data_package: statistical info 
	from the data_stats function
	
	** driver_id: the driver we want to
	compare
	
	i think thats it
	'''
	
	analytic_package = data_packet['data_package']
	driver_id = data_packet['driver_id']
	
	# extract data from analytic_packag
	iqr_outlier = analytic_package['iqr_outlier']
	standard_deviation = analytic_package['standard_deviation']
	mean = analytic_package['raw_mean']
	median = analytic_package['median']
	
	










def driver_ranking(bundled_data):
	'''
	bundled data is a dictionary with
	the following keys:
		
		** data_packet: list full of 
		dicts that hold driver data
		
		** analytic_packet: a dictionary
		that holds all the statistical
		findings derived from that driver
		data
	
	we gonna take that info and develop
	a ranking system that we can
	compare our target driver with
	'''
	dict_list = bundled_data['data_packet']
	analytic_dict = ['analyitic_packet']
	
	speed_list = []
	for dict in dict_list:
		speed_list.append(dict['percent_speeding'])
	
	speed_list.sort()
	
	'''
	plt.boxplot(speed_list, vert=False, showmeans=True)
	plt.xlabel('Speeding Percentage')
	plt.title('Box Plot of Weekly Speeding Percentages')
	plt.show()
	'''
	'''
	plt.hist(speed_list, bins=15, edgecolor='black')
	plt.xlabel('Speeding Percentage')
	plt.ylabel('Number of Drivers')
	plt.title('Distribution of Speeding Percentages for the Week')
	plt.show()
	'''
	
	'''
	cdf = np.linspace(0, 1, len(speed_list))

	# Plot the CDF
	plt.plot(speed_list, cdf, marker='o', linestyle='-', color='b')
	plt.title("Cumulative Distribution of Speeding Percentages")
	plt.xlabel("Speeding Percentage")
	plt.ylabel("Cumulative Probability")
	plt.grid()
	plt.show()
	'''
	
	




'''
****************
here are a couple functions to get
intel from db to aid in my analysis
****************
'''

def get_max_date(tbl='speedGaugeData'):
	dbName = settings.DB_PATH
	
	conn = sqlite3.connect(dbName)
	c = conn.cursor()
	
	sql = f'SELECT MAX (start_date) FROM {tbl}'
	c.execute(sql)
	max_date = c.fetchone()[0]
	
	return max_date













def get_all_dates(tbl='speedGaugeData'):
	'''
	returns a list of all distinct
	dates in ascending order - oldest
	to newest
	'''
	
	dbName = settings.DB_PATH
	
	conn = sqlite3.connect(dbName)
	c = conn.cursor()
	
	sql = f'SELECT DISTINCT start_date FROM {tbl} ORDER BY start_date ASC'
	c.execute(sql)
	dates = c.fetchall()
	
	date_list = []
	for date in dates:
		date_list.append(date[0])
	
	return date_list
	
	










def retrieve_rtm_driver_ids(rtm='chris', tbl='driverInfo'):
	dbName = settings.DB_PATH
	
	conn = sqlite3.connect(dbName)
	c = conn.cursor()
	
	sql = f'SELECT driver_id FROM {tbl} WHERE rtm = ?'
	value = (rtm,)
	c.execute(sql, value)
	ids = c.fetchall()
	
	id_list = []
	for id in ids:
		id_list.append(id[0])
	
	return id_list






def retrieve_rtm_speed(date, tbl='speedGaugeData'):
	dbName = settings.DB_PATH
	
	conn = sqlite3.connect(dbName)
	c = conn.cursor()
	
	rtm_driver_ids = retrieve_rtm_driver_ids()
	
	data_packets = []
	
	for driver_id in rtm_driver_ids:
		sql = f'SELECT percent_speeding, driver_name FROM {tbl} WHERE driver_id = ? AND start_date = ?'
		value = (driver_id, date)
		c.execute(sql, value)
		result = c.fetchone()
		
		if result != None:
			data_packet = {
				'driver_id': driver_id,
				'percent_speeding': result[0],
				'driver_name': result[1]
			}
			
			data_packets.append(data_packet)
	
	return data_packets

	

	






def gather_driver_name(driver_id, tbl='speedGaugeData'):
	
	dbName = settings.DB_PATH
	
	conn = sqlite3.connect(dbName)
	c = conn.cursor()
	
	sql = f'SELECT driver_name FROM {tbl} WHERE driver_id = ?'
	value = (driver_id,)
	
	c.execute(sql, value)
	result = c.fetchone()
	
	data_packets = []
	
	try:
		driver_name = result[0]
	
	except:
		input('Weird. this driver_id does not have a driver_name assosiated with it. press any key to continue')
	
	return driver_name
	
	
	
	
	
	
	
	
	
	
	
	
def retrieve_avg_data(driver_ids, target_date):
	'''
	collects dictionaries with these
	keys:
		driver_id
		driver_name
		percent_speeding
	'''
	
	tbl = 'speedGaugeData'
	dbName = settings.DB_PATH
	
	conn = sqlite3.connect(dbName)
	c = conn.cursor()
	
	data_packets = []
	
	for driver_id in driver_ids:
		sql = f'SELECT driver_name, percent_speeding FROM {tbl} WHERE driver_id = ? AND start_date = ?'
		value = (driver_id, target_date)
	
		c.execute(sql, value)
		result = c.fetchone()
		
		data_packet = {
			'driver_id': driver_id,
			'driver_name': result[0],
			'percent_speeding': result[1]
		}
		
		data_packets.append(data_packet)
	
	conn.close()
	
	return data_packets
	
	
'''
******************
end db retreival functions
******************


|---------------------------------|


*****************
supplimental analysis functions
****************+
'''


def build_avg_analytics(driver_ids, target_date):
	'''
	this function will return intel on
	averages. average speeding, as well as intel on standard deviation for
	each driver
	
	driver_ids is a list of driver_id
	that we gonna use to build the avg
	package
	'''
	
	avg_data = retrieve_avg_data(driver_ids, target_date)
	'''
	this gets a list full of 
	dictionaries with keys:
		driver_name
		driver_id
		percent_speeding
	'''
	
	speed_list = []
	for dict in avg_data:
		speed_list.append(dict['percent_speeding'])
	
	avg_speed = statistics.mean(speed_list)
	std_deviation = statistics.stdev(speed_list)
	
	for dict in avg_data:
		# organize data from dict
		driver_name = dict['driver_name']
		driver_id = dict['driver_id']
		percent_speeding = dict['percent_speeding']
		
		# determine how many standard 
		# deviations from the mean this
		# driver is at
		num_std_devs = math.floor(abs(percent_speeding - avg_speed) / std_deviation) + 1
		
		# update dict with number of
		# standard deviations
		dict['num_std_deviations'] = num_std_devs
	
	return avg_data
		
	
	
	
	
def gather_driver_info(id_list):
	'''
	returns list of dicts with keys:
		driver_id
		driver_name
		percent_speeding
	'''
	tbl = 'speedGaugeData'
	dbName = settings.DB_PATH
	start_date = get_max_date()
	
	conn = sqlite3.connect(dbName)
	c = conn.cursor()
	
	data_packets = []
	
	for driver_id in id_list:
		sql = f'SELECT driver_name, percent_speeding FROM {tbl} WHERE start_date = ? AND driver_id = ?'
		values = (start_date, driver_id)
		c.execute(sql, values)
		result = c.fetchone()
		
		driver_name = result[0]
		percent_speeding = result[1]
		
		data_packet = {
			'driver_id': driver_id,
			'driver_name': driver_name,
			'percent_speeding': percent_speeding
		}

	
	conn.close()
	
	return data_packets
	

	
	
	
	









'''
***************
end supplimental analysis functions
***************
'''
		



def full_rtm_stats(rtm='chris'):
	'''
	returns a dictionary with three
	dicrionaries in it
	
	keys:
		outlier_dicts
		avg_analytics
		data_stats
		
	'''
	max_date = get_max_date()
	all_dates = get_all_dates()
	
	data_packets = retrieve_rtm_speed(max_date)
	'''
	data_packets is list of dictionarys
	with keys:
		percent_speeding
		driver_id
		driver_name
	'''

	speed_list = []
	driver_ids = []
	outlier_dicts = []
	high_outliers = []
	
	# fill out speed_lists and 
	# driver_ids
	for data_packet in data_packets:
		percent_speeding = data_packet['percent_speeding']
		driver_id = data_packet['driver_id']
		speed_list.append(percent_speeding)
		driver_ids.append(driver_id)
		
	speed_list.sort()
	
	# get avg analysis packet
	avg_analytics = build_avg_analytics(driver_ids, max_date)
	
	# get standard deviation
	sd = statistics.stdev(speed_list)
		
	raw_mean = statistics.mean(speed_list)
	
	median = statistics.median(speed_list)
	
	# iqr stuff to find/filter outliers
	# just google what iqr is
	q1 = np.percentile(speed_list, 25)
	q3 = np.percentile(speed_list, 75)
	iqr = q3 - q1
	high_range_iqr = q3 + (iqr * 1.5)
	low_range_iqr = q1 - (iqr * 1.5)
	
	# bundle stats into a dict
	stats_dict = {
		'standard_deviation': sd,
		'average': raw_mean,
		'median': median,
		'q1': q1,
		'q3': q3,
		'iqr': iqr,
		'high_range_iqr': high_range_iqr,
		'low_rsnge_iqr': low_range_iqr
	}
	
	# make list of outlier speeds
	for speed in speed_list:
		if speed > high_range_iqr:
			high_outliers.append(speed)
	 
	
	# put together info on outliers

	for dict in data_packets:
		if dict['percent_speeding'] in high_outliers:
			outlier_dicts.append(dict)
	
	bundled_data = {
		'outlier_dicts': outlier_dicts,
		'avg_analytics': avg_analytics,
		'data_stats': stats_dict
	}
	
	return bundled_data
	
	

	


	
	
	
	



	
	
	
