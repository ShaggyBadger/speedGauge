# settings.py
import os
import sqlite3
import Path


'''
establish paths to various 
directories for use in other parts of
da program

TODO: change os.path to Path objects
'''

# root directory
BASE_DIR = os.path.dirname(__file__)
IMG_PATH = os.path.join(BASE_DIR, 'images')

REPORTS_PATH = os.path.join(BASE_DIR, 'reports')

IMG_ASSETS_PATH = os.path.join(IMG_PATH, 'assets')

WEEKLY_REPORTS_PATH = os.path.join(IMG_PATH, 'weeklyReports')

# path to data i.e. the csv files
DATA_PATH = os.path.join(BASE_DIR, 'data')

# path to unprocessed directory
UNPROCESSED_PATH = os.path.join(DATA_PATH, 'unprocessed')

# path to processed directory
PROCESSED_PATH = os.path.join(DATA_PATH, 'processed')

# path to src directory
SRC_PATH = os.path.join(BASE_DIR, 'src')

# path to database directory
DATABASE_PATH = os.path.join(BASE_DIR, 'database')

# path to actual speedGuage.db
DB_PATH = os.path.join(DATABASE_PATH, 'speedGauge.db')

# column names and types for db
# not sure if i should include id

# aka driverInfo
driverInfoTbl_column_info = {
	'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
	'driver_name': 'TEXT',
	'driver_id': 'INTEGER',
	'rtm': 'TEXT'
	'terminal': 'TEXT',
	'shift': 'TEXT'
}

# aka speedGaugeData
mainTbl_column_intel = {
	'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
	'driver_name': 'TEXT',
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
	'driver_id': 'INTEGER',
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

	
red = '#ff2400'
green = '#03ac13'
warning_orange = '#ffbc37'
swto_blue = '#0b3e69'

# Unicode arrows: ↑ (2191) and ↓ (2193)
up_arrow = '&#x2191;'
down_arrow = '&#x2193;'

tbl_name = 'speedGaugeData2'

# univeral refrence source. handy.
speedGaugeData_tbl = 'speedGaugeData'
driverInfo_tbl = 'driverInfo'

# super common call. put this here so everyone can use it
def db_connection():
	# returns a connection
	dbName = DB_PATH
	conn = sqlite3.connect(dbName)
	return conn
