import settings
import os
from src import analysis3
from src import visualizations
from src import visualizations2
from src import db_utils2
from src import analysis2
from src import processing2
from src import processing3
from src import reports
from src import individualDriver
from src import idrReport
import matplotlib.pyplot as plt
import console





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
	if enter_driver is True:
		data_package = individualDriver.main(enter_driver=True, print_out=True)
	
		idrReport.generate_report(data_package['stats'])
	
	else:
		data_package = individualDriver.main(enter_driver=False, driver_num=driver_id, print_out=True)
		
		idrReport.generate_report(data_package['stats'])




def process_spreadsheet(file):
	# get path for incoming file
	file_path = os.path.join(folder_path, file)
	
	# extract date from spreadsheet
	date_dict = data_processing.extract_date(file_path)

	# get dicts for each row of file
	data_dicts = data_processing.data_to_dict(file_path)
	
	# insert file data into db
	for dictionary in data_dicts:
		# insert dates into dictionary
		dictionary['start_date'] = date_dict['start_date']
		
		dictionary['end_date'] = date_dict['end_date']
		
		# get accurate driver_id for dict
		driver_id = db_utils.get_driver_id(dictionary['driver_name'])
		
		dictionary['driver_id'] = driver_id
		
		# send completed dictionary to db
		tbl = 'speedGaugeData'
		db_utils.insert_data(dictionary, tbl)
		
		# delete the name median from db
		db_utils.delete_driver()
	data_processing.mv_completed_file(file_path)
	













def db_setup():
	'''
	pretty straightforward. This just
	tells the db_utils to run the 
	generate_db function. this here is
	just a way to use it from the main
	file.
	'''
	db_utils.generate_db(debug=True)
	






def run_weekly_analyis(manager='chris'):
	'''
	main function to run analysis
	
	manager can be rtm name or it can
	be "none" in order to get ALL
	drivers ids. 
	'''
	# dict to hold paths to the plots
	plt_paths = {}
	
	# build up this week's data'
	current_date = db_utils2.get_max_date()
	date_list = db_utils2.get_all_dates()
	previous_date = date_list[-2]
	
	# gather id numbers to analyze
	rtm_id_set = db_utils2.gather_driver_ids(rtm=manager)
	company_id_set = db_utils2.gather_driver_ids(rtm='none')
	
	rtm_driver_data = db_utils2.gather_driver_data(rtm_id_set, current_date)
	rtm_driver_data2 = db_utils2.gather_driver_data(rtm_id_set, previous_date)
	company_driver_data = db_utils2.gather_driver_data(company_id_set, current_date)
	company_driver_data2 = db_utils2.gather_driver_data(company_id_set, previous_date)
	
	# median and mean historical data
	rtm_historical_data = db_utils2.gather_historical_driver_data(rtm_id_set)
	company_historical_data = db_utils2.gather_historical_driver_data(company_id_set)
	
	# analyize this week data
	rtm_stats_analysis = analysis2.weekly_stats_analysis(rtm_driver_data, rtm_driver_data2, current_date)
	company_stats_analysis = analysis2.weekly_stats_analysis(company_driver_data, company_driver_data2, current_date)
	
	
	# print out info
	analysis2.print_stats(rtm_stats_analysis, f'RTM: {manager}')
	analysis2.print_stats(company_stats_analysis, 'Company')
	
	rtm_stats = rtm_stats_analysis['stats']
	company_stats = company_stats_analysis['stats']
	
	
	rtm_box_plot = visualizations.gen_box_chart(rtm_stats)
	processing_data = {
		'plt': rtm_box_plot,
		'current_date': current_date,
		'scope': f'RTM_{manager}',
		'plt_type': 'boxPlot'
	}
	rbp =processing2.save_plt(processing_data)
	plt_paths['rtm_boxPlot'] = rbp
	rtm_box_plot.show()
	rtm_box_plot.close()
	
	company_box_plot = visualizations.gen_box_chart(company_stats)
	processing_data = {
		'plt': company_box_plot,
		'current_date': current_date,
		'scope': f'company',
		'plt_type': 'boxPlot'
	}
	cbp = processing2.save_plt(processing_data)
	plt_paths['company_boxPlot'] = cbp
	company_box_plot.show()
	company_box_plot.close()
	
	rtm_histogram = visualizations.gen_histogram(rtm_stats)
	processing_data = {
		'plt': rtm_histogram,
		'current_date': current_date,
		'scope': f'RTM_{manager}',
		'plt_type': 'histogram'
	}
	rh = processing2.save_plt(processing_data)
	plt_paths['rtm_histogram'] = rh
	rtm_histogram.show()
	rtm_histogram.close()

	company_histogram = visualizations.gen_histogram(company_stats)
	processing_data = {
		'plt': company_histogram,
		'current_date': current_date,
		'scope': 'company',
		'plt_type': 'histogram'
	}
	ch = processing2.save_plt(processing_data)
	plt_paths['company_histogram'] = ch
	company_histogram.show()
	company_histogram.close()

	median_line_chart = visualizations.gen_line_chart('median', rtm_historical_data, company_historical_data)
	processing_data = {
		'plt': median_line_chart,
		'current_date': current_date,
		'scope': f'RTM_{manager}',
		'plt_type': 'medianLineChart'
	}
	medianlc = processing2.save_plt(processing_data)
	plt_paths['median_lineChart'] = medianlc
	median_line_chart.show()
	median_line_chart.close()

	mean_line_chart = visualizations.gen_line_chart('mean', rtm_historical_data, company_historical_data)
	processing_data = {
		'plt': mean_line_chart,
		'current_date': current_date,
		'scope': f'RTM_{manager}',
		'plt_type': 'avgLineChart'
	}
	meanlc = processing2.save_plt(processing_data)
	plt_paths['mean_lineChart'] = meanlc
	median_line_chart.show()
	median_line_chart.close()
	
	report = reports.create_report(rtm_stats_analysis, manager, plt_paths)
	
	

	


	
	
	
	

	



def driver_analysis(manager='chris'):
	driver_id = input('Please enter driver id: ')
	
	
	
	# build up this week's data'
	current_date = db_utils2.get_max_date()
	date_list = db_utils2.get_all_dates()
	previous_date = date_list[-2]
	
	# gather id numbers to analyze
	rtm_id_set = db_utils2.gather_driver_ids(rtm=manager)
	company_id_set = db_utils2.gather_driver_ids(rtm='none')
	
	rtm_driver_data = db_utils2.gather_driver_data(rtm_id_set, current_date)
	rtm_driver_data2 = db_utils2.gather_driver_data(rtm_id_set, previous_date)
	company_driver_data = db_utils2.gather_driver_data(company_id_set, current_date)
	company_driver_data2 = db_utils2.gather_driver_data(company_id_set, previous_date)
	
	# median and mean historical data
	rtm_historical_data = db_utils2.gather_historical_driver_data(rtm_id_set)
	company_historical_data = db_utils2.gather_historical_driver_data(company_id_set)






def weekly_analysis():
	analysis = analysis3.build_analysis()
	plt_paths = visualizations2.controller(analysis)









def run_program():
	folder_path = settings.UNPROCESSED_PATH
	files = os.listdir(folder_path)
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
		processing3.main()
	
	elif str(selection) == str(2):
		run_weekly_analyis()
		run_weekly_analyis(manager='none')
	
	elif str(selection) == str(3):
		idr()
	

run_program()
#run_weekly_analyis()
#weekly_analysis()
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

