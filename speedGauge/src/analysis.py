import sys, os
from pathlib import Path
# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Now you can import settings
import settings
import numpy as np
import math
import statistics
import sqlite3
import console

def filter_speed_list(spd_lst, max_stdev=3):
	'''
	returns a modified list that
	excludes speeds past a certain 
	standard deviation
	'''
	stdev = statistics.stdev(spd_lst)
	avg = statistics.mean(spd_lst)
	
	max_spd = avg + (max_stdev * stdev)
	
	spd = [speed for speed in spd_lst if speed < max_spd]
	
	return spd
	
def get_percent_change(val1, val2):
	if val2 == 0:
		return ((val1 - val2) / (val2 + 1)) * 100
	else:
		return ((val1 - val2) / (val2)) * 100

def build_stdev_buckets(avg, stdev, spd_list):
	'''
	returns a dictionary with key =
	stdev1, stdev2, etc. then the value
	is a list with distinct speeds from
	the speed_list that fits into those
	buckets
	'''
	
	# build dictionary keys
	stdev_buckets = {
		f'stdev{i}': [] for i in range(1, 4)
		}
	stdev_buckets['stdev4_plus'] = []
	
	# sort speeds
	for spd in spd_list:
		stdev_bucket = math.floor(((abs(spd - avg)) / stdev) + 1)
		bucket_key = f'stdev{stdev_bucket}'
		
		if bucket_key in stdev_buckets:
			stdev_buckets[f'stdev{stdev_bucket}'].append(spd)
		else:
			stdev_buckets['stdev4_plus'].append(spd)
	
	# sort the lists so they look nice	
	for bucket in stdev_buckets:
		stdev_buckets[bucket].sort()
	
	return stdev_buckets

def build_stats(cur_spd, prev_spd, date):
	'''
	returns a dictionary of stats for
	the incoming lists of speeds. so
	current_spd is the list we really
	want to know the stats for, and 
	prev_spd is last weeks speeds that
	we use for comparison.
	'''
	stdev_outlier_spd = []
	iqr_outlier_spd = []
	
	# build speed list without high stdev that mess up analysis
	filtered_cur_speed = filter_speed_list(cur_spd)
	filtered_prev_speed = filter_speed_list(prev_spd)
	
	# get mode of data
	cur_mode = statistics.mode(filtered_cur_speed)
	prev_mode = statistics.mode(filtered_prev_speed)
	
	# get avg stats
	avg1 = statistics.mean(filtered_cur_speed)
	avg2 = statistics.mean(filtered_prev_speed)
	stdev1 = statistics.stdev(filtered_cur_speed)
	stdev2 = statistics.stdev(filtered_prev_speed)
	
	avg_abs_change = avg1 - avg2
	avg_percent_change = get_percent_change(avg1, avg2)
	
	# build standard deviation buckets
	stdev_buckets = build_stdev_buckets(avg1, stdev1, cur_spd)
	
	# get median stats
	median1 = statistics.median(filtered_cur_speed)
	median2 = statistics.median(filtered_prev_speed)
	
	median_abs_change = median1 -  median2
	median_percent_change = get_percent_change(median1, median2)
	
	# iqr stuff to find/filter outliers
	# just google what iqr is
	q1 = np.percentile(filtered_cur_speed, 25)
	t = 0.75 * (len(filtered_cur_speed) + 1)
	tlow = math.floor(t)
	thigh = math.ceil(t)
	#q3 = (spd1[tlow]+spd1[thigh]) / 2
	q3 = np.percentile(filtered_cur_speed, 75)
	iqr = q3 - q1
	high_range_iqr = q3 + (iqr * 1.5)
	low_range_iqr = q1 - (iqr * 1.5)
	
	iqr_outlier_count = 0
	for spd in cur_spd:
		if spd > high_range_iqr:
			iqr_outlier_count += 1
	
	stats = {
		'date': date,
		'sample_size': len(filtered_cur_speed),
		'stdev': round(stdev1, 2),
		'stdev_buckets': stdev_buckets,
		'1std': len(stdev_buckets['stdev1']),
		'2std': len(stdev_buckets['stdev2']),
		'3std': len(stdev_buckets['stdev3']),
		'4stdplus': len(stdev_buckets['stdev4_plus']),
		'cur_avg': round(avg1, 2),
		'prev_avg': round(avg2, 2),
		'avg_abs_change': round(avg_abs_change, 2),
		'avg_percent_change': round(avg_percent_change, 2),
		'cur_median': round(median1, 2),
		'prev_median': round(median2, 2),
		'median_abs_change': round(median_abs_change, 2),
		'median_percent_change': round(median_percent_change, 2),
		'q1': round(q1, 2),
		'q3': round(q3, 2),
		'iqr': round(iqr, 2),
		'high_range_iqr': round(high_range_iqr, 2),
		'low_range_iqr': round(low_range_iqr, 2),
		'cur_mode': cur_mode,
		'prev_mode': prev_mode,
		'raw_cur_spd': cur_spd,
		'filtered_cur_spd': filtered_cur_speed,
		'raw_prev_spd': prev_spd,
		'filtered_prev_spd': filtered_prev_speed,
		'num_iqr_outliers': iqr_outlier_count
	}
	
	return stats

def prepare_speeds(date, rtm_selection='chris', max_stdev=3):
	'''
	returns a list of percent_speeding
	for rtm and company for a given 
	date. this is extra good bc now i 
	can use this for any date i want in
	da future.
	'''

	conn = settings.db_connection()
	c = conn.cursor()
	tbl = settings.speedGaugeData
	
	company_ids = []
	rtm_ids = []
	
	rtm_speed = []
	company_speed = []
	none_spds = []
	
	# get rtm and company driver ids
	company_ids = []
	rtm_ids = []
	sql = f'SELECT DISTINCT driver_id, rtm FROM {settings.driverInfo}'
	c.execute(sql)
	results = c.fetchall()
	for result in results:
		driver_id = result[0]
		rtm = result[1]
		company_ids.append(driver_id)
		
		if rtm == rtm_selection:
			rtm_ids.append(driver_id)
	
	# collect percent_speeding for the week
	for driver_id in company_ids:
		sql = f'SELECT percent_speeding FROM {tbl} WHERE start_date = ? AND driver_id = ?'
		values = (date, driver_id)
		c.execute(sql, values)
		result = c.fetchone()
		
		if result != None:
			percent_speeding = result[0]
			company_speed.append(percent_speeding)
			
			if driver_id in rtm_ids:
				rtm_speed.append(percent_speeding)
		
		else:
			none_spds.append(driver_id)
	
	rtm_speed.sort()
	company_speed.sort()
	
	# prepare the info to ship out
	data_packet = {
		'rtm': rtm_speed,
		'company': company_speed
	}
	
	# print out a report
	print('\n************************')
	print('Analysis: Prepare Speeds Report')
	print(f'Date: {date}')
	print(f'RTM driver count: {len(rtm_ids)}')
	print(f'RTM speed count: {len(rtm_speed)}')
	print(f'Company driver count: {len(company_ids)}')
	print(f'Company speed count: {len(company_speed)}')
	print('driver_id with None for percent_speeding:')
	for i in none_spds:
		sql = f'SELECT driver_name FROM {settings.driverInfo} WHERE driver_id = ?'
		value = (i,)
		c.execute(sql, value)
		result = c.fetchone()
		if result != None:
			driver_name = result[0]
		else:
			driver_name = None
		
		sql = f'SELECT DISTINCT formated_start_date FROM {settings.speedGaugeData} WHERE driver_id = ? ORDER BY formated_start_date ASC'
		value = (i,)
		c.execute(sql, value)
		result = c.fetchall()
		print(f'  {i}: {driver_name}')
		print(f'  Dates for this driver:')
		print(f'  {result}')
	print('************************\n')
	
	conn.close()
	
	# send it
	return data_packet

def get_date_list():
	'''
	returns a list of dates in the db 
	in descending order. Newest date
	will be index 0, last week will be
	index 1, etc
	'''
	
	conn = settings.db_connection()
	c = conn.cursor()
	
	sql = f'SELECT DISTINCT start_date FROM {settings.speedGaugeData} ORDER BY start_date DESC'
	c.execute(sql)
	results = c.fetchall()
	
	date_list = [date[0] for date in results]
	
	return date_list
	
def build_analysis(rtm='chris'):
	conn = settings.db_connection()
	c = conn.cursor()
	
	# get dates for analysis
	date_list = get_date_list()
	current_date = date_list[0]
	previous_date = date_list[1]
	
	# get speed lists
	current_speeds = prepare_speeds(current_date, rtm_selection=rtm)
	prev_speeds = prepare_speeds(previous_date, rtm_selection=rtm)
	
	# separate out the speed lists
	current_speeds_rtm = current_speeds['rtm']
	current_speeds_company = current_speeds['company']
	
	prev_speeds_rtm = prev_speeds['rtm']
	prev_speeds_company = prev_speeds['company']
	
	company_stats = build_stats(current_speeds_company, prev_speeds_company, current_date)
	rtm_stats = build_stats(current_speeds_rtm, prev_speeds_rtm, current_date)
	
	stats_bundle = {
		'company': company_stats,
		'rtm': rtm_stats
	}
	
	return stats_bundle

if __name__ == '__main__':
	#prepare_data()
	a = build_analysis()
	
