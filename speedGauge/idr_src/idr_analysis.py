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
from src.analysis import build_analysis
	
def get_percent_change(val1, val2):
	if val2 == 0:
		return ((val1 - val2) / (val2 + 1)) * 100
	else:
		return ((val1 - val2) / (val2)) * 100

def idr_analytics(stats=build_analysis(), driver_id=30150643):
	rtm_stats = stats['rtm']
	company_stats = stats['company']
	
	idr_dicts = db_utils.idr_driver_data(driver_id)

# auto-reload module to prevent cache issues
if 'analysis' in sys.modules:
	importlib.reload(sys.modules['analysis'])

if __name__ == '__main__':
	
	a = idr_analytics()
