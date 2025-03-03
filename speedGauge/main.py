import settings
import os
import importlib
from src import analysis
from src import visualizations
from src import db_utils
from src import processing
from src import reports
from src import individualDriver
from idr_src import idr_analysis
import matplotlib.pyplot as plt
import console
import json

def inspection():
	import inspect
	functions = inspect.getmembers(db_utils, inspect.isfunction)
	
	for name, func in functions:
		docstring = inspect.getdoc(func) or 'no docstring provided'
		print(f'{name}\n')
		print(docstring)
		print('\n******\n')

def idr(enter_driver=True, driver_id=30150643):
	'''
	this can work from makn seledtion
	screen, in which case enter driver 
	is True
	
	also can use this to run report on
	driver via the weekly analysis. 
	maybe send through the outliers
	and get indivual reports on them
	
	in that case enter_driver is set 
	to False and the driver_id needs
	to be overriden as well with the
	target id
	'''
	# get driver_id from user
	ids = {
		1201619: 'rodrick',
		30199025: 'perkins',
		30072074: 'jesse',
		5055241: 'brent',
		30188814: 'jamie',
		1110492: 'danny',
		30069398: 'ron',
		1152694: 'charles',
		30202984: 'john r'
	}
	
	if enter_driver is True:
		valid_input = False
		
		while valid_input is False:
			console.clear()
			for i in ids:
				print(f'{i}: {ids[i]}')
			print('********\n')

			selection = input('Enter Driver Number: ')
			
			if db_utils.verify_driver_id(selection) is True:
				valid_input = True
				driver_id = int(selection)
			else:
				console.clear()
				input(f'{selection} is not a valid input in the database. please enter another number...')
	
	# collect all driver dictionaries
	driver_dicts = db_utils.idr_driver_data(driver_id)
	
	# build stats dict
	stats = idr_analysis.idr_analytics(driver_dicts, driver_id)
		



def weekly_analysis():
	stat_packet = analysis.build_analysis()
	
	rtm_analysis = stat_packet['rtm']
	company_analysis = stat_packet['company']
	rtm_name = stat_packet['rtm_name']

	plt_paths = visualizations.controller(stat_packet)
	
	stats_json = json.dumps(stat_packet)
	plt_paths_json = json.dumps(plt_paths, default=str)
	
	# save json data in the db
	db_utils.store_json_data(stats_json, plt_paths_json, rtm_name, db_utils.get_max_date())		
	
	report_path = reports.create_report(stat_packet, plt_paths)

def run_program():
	importlib.reload(visualizations)
	importlib.reload(reports)
	importlib.reload(db_utils)
	importlib.reload(idr_analysis)
	
	selection_dict = {
		'1': 'process spreadsheets',
		'2': 'run weekly analytics',
		'3': 'Run individual driver report'
	}
	
	print('please make selection:')
	for i in selection_dict:
		print(f'\n{i}: {selection_dict[i]}')
	selection = input()
	
	console.clear()
	if str(selection) == str(1):
		processing.main()
	
	elif str(selection) == str(2):
		weekly_analysis()
	
	elif str(selection) == str(3):
		idr()

if __name__ == '__main__':
	run_program()
	#run_weekly_analyis()
	#weekly_analysis()
