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
from src import analysis

def get_percent_change(val1, val2):
	if val2 == 0:
		return ((val1 - val2) / (val2 + 1)) * 100
	else:
		return ((val1 - val2) / (val2)) * 100
		

def idr_analytics(driver_dicts, driver_id):
	rtm_stats = stats['rtm']
	company_stats = stats['company']
	
	idr_dicts = db_utils.idr_driver_data(driver_id)


if __name__ == '__main__':
	
	#a = idr_analytics()
	pass
