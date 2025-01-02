# settings.py
import os


'''
establish paths to various 
directories for use in other parts of
da program
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
db_column_intel = {
	'driver_name': 'TEXT',
	'percent_speeding': 'INTEGER',
	'max_speed_non_interstate_freeway': 'REAL',
	'percent_speeding_non_interstate_freeway': 'REAL',
	'max_speed_interstate_freeway': 'REAL',
	'percent_speeding_interstate_freeway': 'REAL',
	'incident_location': 'TEXT',
	'speed_limit': 'INTEGER',
	'speed': 'INTEGER',
	'distance_driven': 'INTEGER',
	'location': 'TEXT',
	'percent_speeding_numerator': 'REAL',
	'percent_speeding_denominator': 'REAL',
	'incidents_interstate_freeway': 'REAL',
	'observations_interstate_freeway': 'REAL',
	'incidents_non_interstate_freeway': 'REAL',
	'observations_non_interstate_freeway': 'REAL',
	'difference': 'INTEGER',
	'start_date': 'TEXT',
	'end_date': 'TEXT'
	}
	
red = '#ff2400'
green = '#03ac13'
warning_orange = '#ffbc37'
swto_blue = '#0b3e69'

# Unicode arrows: ↑ (2191) and ↓ (2193)
up_arrow = '&#x2191;'
down_arrow = '&#x2193;'

tbl_name = 'speedGaugeData'

