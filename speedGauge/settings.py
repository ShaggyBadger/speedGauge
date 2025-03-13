# settings.py
import os
import sys
import importlib
import sqlite3
from pathlib import Path


'''
establish paths to various  directories for use in other parts of da program
'''

# root directory
BASE_DIR = Path(__file__).parent

# Main directories inside root
IMG_PATH = BASE_DIR / 'images'
REPORTS_PATH = BASE_DIR / 'reports'
IDR_REPORTS_PATH = BASE_DIR / 'idr_reports'

# Nested directories
IMG_ASSETS_PATH = IMG_PATH / 'assets'
WEEKLY_REPORTS_PATH = IMG_PATH / 'weeklyReports'
DATA_PATH = BASE_DIR / 'data'

# path to unprocessed directory
UNPROCESSED_PATH = DATA_PATH / 'unprocessed'

# path to processed directory
PROCESSED_PATH = DATA_PATH / 'processed'

# path to src directory
SRC_PATH = BASE_DIR / 'src'

# path to database directory
DATABASE_PATH = BASE_DIR / 'database'

# path to actual speedGuage.db
DB_PATH = DATABASE_PATH / 'speedGauge.db'

'''column names and types for db not sure if I should include id'''
# aka driverInfo
driverInfoTbl_column_info = {
	'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
	'driver_name': 'TEXT',
	'driver_id': 'INTEGER',
	'rtm': 'TEXT',
	'terminal': 'TEXT',
	'shift': 'TEXT'
}

# aka speedGaugeData
mainTbl_column_info = {
	'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
	'driver_name': 'TEXT',
	'driver_id': 'INTEGER',
	'vehicle_type': 'TEXT',
	'percent_speeding': 'REAL',
	'max_speed_non_interstate_freeway': 'REAL',
	'percent_speeding_non_interstate_freeway': 'REAL',
	'max_speed_interstate_freeway': 'REAL',
	'percent_speeding_interstate_freeway': 'REAL',
	'worst_incident_date': 'TEXT',
	'incident_location': 'TEXT',
	'speed_limit': 'INTEGER',
	'speed': 'INTEGER',
	'speed_cap': 'TEXT',
	'custom_speed_restriction': 'TEXT',
	'distance_driven': 'INTEGER',
	'url': 'TEXT',
	'location': 'TEXT',
	'percent_speeding_numerator': 'REAL',
	'percent_speeding_denominator': 'REAL',
	'incidents_interstate_freeway': 'REAL',
	'observations_interstate_freeway': 'REAL',
	'incidents_non_interstate_freeway': 'REAL',
	'observations_non_interstate_freeway': 'REAL',
	'difference': 'INTEGER',
	'start_date': 'TEXT',
	'end_date': 'TEXT',
	'formated_start_date': 'TEXT',
	'formated_end_date': 'TEXT',
	'human_readable_start_date': 'TEXT',
	'human_readable_end_date': 'TEXT',
	'percent_speeding_source': 'TEXT'
	}

imgStorageTbl_column_info = {
	'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
	'start_date': 'TEXT',
	'rtm': 'TEXT',
	'plt_type': 'TEXT',
	'plt_name': 'TEXT',
	'plt_path': 'TEXT',
	'plt_blob': 'BLOB'
}

analysisStorageTbl_column_info = {
	'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
	'start_date': 'TEXT',
	'rtm': 'TEXT',
	'stats': 'TEXT',
	'plt_paths': 'TEXT'
}

# easy color reference
red = '#ff2400'
green = '#03ac13'
warning_orange = '#ffbc37'
swto_blue = '#0b3e69'

# Unicode arrows: ↑ (2191) and ↓ (2193)
up_arrow = '&#x2191;'
down_arrow = '&#x2193;'

# univeral refrence source. handy.
speedGaugeData = 'speedGaugeData'
driverInfo = 'driverInfo'
imgStorage = 'imgStorage'
analysisStorage = 'analysisStorage'

# super common call. put this here so everyone can use it
def db_connection():
	# returns a db connection
	dbName = DB_PATH
	conn = sqlite3.connect(dbName)
	return conn

# auto-reload settings module to prevent cache issues
if 'settings' in sys.modules:
	importlib.reload(sys.modules['settings'])
