import sys, os
from pathlib import Path
import importlib
# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Now you can import settings
import settings
import numpy as np
import math
import statistics
import sqlite3
import console
from src import db_utils

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


def build_analysis(rtm='chris'):
	date_list = db_utils.get_all_dates()
	rtm_ids = db_utils.gather_driver_ids(rtm='chris')
	company_ids = db_utils.gather_driver_ids(rtm='company')
	
	# make list of dicts. key is date, value is filtered speed_list
	rtm_data = []
	company_data = []
	
	# build filtered speed list for company and rtm for each date
	for date in date_list:
		rtm_drivers = db_utils.gather_driver_data(rtm_ids, date)
		company_drivers = db_utils.gather_driver_data(company_ids, date)
		
		rtm_spd_lst = filter_speed_list([dict['percent_speeding'] for dict in rtm_drivers])
		rtm_avg = round(statistics.mean(rtm_spd_lst), 2)
		rtm_median = round(statistics.median(rtm_spd_lst), 2)
		
		if len(rtm_data) == 0:
			rtm_avg_percent_change = get_percent_change(rtm_avg, 0)
		else:
			prev_avg = rtm_data[-1]['average']
			rtm_avg_percent_change = get_percent_change(rtm_avg, prev_avg)
		
		company_spd_lst = filter_speed_list([dict['percent_speeding'] for dict in company_drivers])
		company_avg = round(statistics.mean(company_spd_lst), 2)
		company_median = round(statistics.median(company_spd_lst), 2)
		
		if len(company_data) == 0:
			company_avg_percent_change = get_percent_change(rtm_avg, 0)
		else:
			prev_avg = company_data[-1]['average']
			company_avg_percent_change = get_percent_change(company_avg, prev_avg)
		
		rtm_data.append(
			{
				'date': date,
				'rtm_name': rtm.capitalize(),
				'spd_lst': rtm_spd_lst,
				'average': rtm_avg,
				'median': rtm_median,
				'avg_percent_change': round(rtm_avg_percent_change,2)
			}
		)
		
		company_data.append(
			{
				'date': date,
				'spd_lst': company_spd_lst,
				'average': company_avg,
				'median': company_median,
				'avg_percent_change': round(company_avg_percent_change, 2)
			}
		)
	
	data_packet = {
		'rtm': rtm_data,
		'company': company_data,
		'rtm_name': db_utils.get_manager(rtm_ids[0])
	}
	
	return data_packet
		
		
	
		


# auto-reload module to prevent cache issues
if 'analysis' in sys.modules:
	importlib.reload(sys.modules['analysis'])

if __name__ == '__main__':
	
	a = build_analysis()

