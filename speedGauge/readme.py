'''

here is the project directory
structure:

speedGuage/
├── data/
│   ├── unprocessed/
│   ├── processed/
├── database/
│   └── speed_data.db
├── settings.py
├── main.py
├── src/
│   ├── data_processing.py
│   ├── db_utils.py
│   ├── analysis.py
│   └── visualization.py
└── process.log

*** working with dates ***
i want to make the starting_date be
the standard for date selection. 

so the max_date variable for findkng
the most recent entries in the db
should *always* reference start_date
NOT end_date. keep it consistent. 



****** ideas to impliment ******
in analytic portion, identify drivers
who fall outside the box plot area. 
these are the outliers who need some
attention

maybe make a table in db to hold the
outlier intel. possible columns:
	id
	date
	driver_id
	peer_median
	peer_average
	driver_speed
	standard_devations_from_average
	
'''
