import sys, os
import statistics
# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Now you can import settings
import settings
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

def save_plt(plt, date, plt_type, rtm='chris'):
	scope = f'RTM_{rtm}'
	
	# Parse date into a datetime object
	date_obj = datetime.strptime(date, "%Y-%m-%d %H:%M")

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
	
	rtm_speed.sort()
	company_speed.sort()
	
	# prepare the info to ship out
	data_packet = {
		'rtm': rtm_speed,
		'company': company_speed
	}
	
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
	
	sql = f'SELECT DISTINCT start_date FROM {settings.speedGaugeData} ORDER BY start_date ASC'
	c.execute(sql)
	results = c.fetchall()
	
	date_list = [date[0] for date in results]
	
	return date_list
	
def prepare_line_data(rtm='chris'):
	'''
	gathers all speed data, sorts it by
	date, and gets avg and median speed
	for each date. 
	
	it does this for both raw speeds
	and filtered speeds. filtered 
	speeds remove anomylous speeds
	greater than 3 stdev from mean
	
	it also organized by company and
	rtm. then its returned in a dict
	'''
	conn = settings.db_connection()
	c = conn.cursor()
	tbl1 = settings.driverInfo
	tbl2 = settings.speedGaugeData
	driver_ids = {}
	company_spd_dict = {}
	rtm_spd_dict = {}
	
	# build driver_id and rtm list
	sql = f'SELECT driver_id, rtm FROM {tbl1}'
	c.execute(sql)
	results = c.fetchall()
	for result in results:
		driver_id = result[0]
		rtm = result[1]
		driver_ids[driver_id] = rtm
	
	# get date list
	dates = get_date_list()
	for date in dates:
		company_spd_dict[date] = []
		rtm_spd_dict[date] = []
	
	# get percent_speed intel
	sql = f'SELECT DISTINCT driver_id, percent_speeding, start_date FROM {tbl2}'
	c.execute(sql)
	results = c.fetchall()
	
	# sort everything out
	temp_counter = 0
	id_list = []
	for result in results:
		driver_id = int(result[0])
		percent_speeding = result[1]
		start_date = result[2]
		driver_rtm = driver_ids[driver_id]
		company_spd_dict[start_date].append(percent_speeding)

		if driver_rtm == rtm:
			rtm_spd_dict[start_date].append(percent_speeding)
	
	for date in dates:
		company_spd_dict[date].sort()
		rtm_spd_dict[date].sort()
	
	# filter out high stdev
	filtered_company_spd_dict = {}
	filtered_rtm_spd_dict = {}
	
	for date, speeds in company_spd_dict.items():
		avg = statistics.mean(speeds)
		stdev = statistics.stdev(speeds)
		threshold = avg + (3 * stdev)
		
		filtered_company_spd_dict[date] = [speed for speed in speeds if speed < threshold]
	
	for date, speeds in rtm_spd_dict.items():
		avg = statistics.mean(speeds)
		stdev = statistics.stdev(speeds)
		threshold = avg + (3 * stdev)
		
		filtered_rtm_spd_dict[date] = [speed for speed in speeds if speed < threshold]
	
	# build dictionary for export
	data_packet = {
		'raw_company': company_spd_dict,
		'filtered_company': filtered_company_spd_dict,
		'raw_rtm': rtm_spd_dict,
		'filtered_rtm': filtered_rtm_spd_dict
	}
	
	return data_packet




def gen_line_chart(stat_selection):
	'''
	stat_function is either average or 
	median
	'''
	if stat_selection == 'average':
		stat_function = statistics.mean
	else:
		stat_function = statistics.median
	
	dates = get_date_list()
	stat_packet = prepare_line_data()
	
	raw_company = stat_packet['raw_company']
	raw_rtm = stat_packet['raw_rtm']
	filtered_company = stat_packet['filtered_company']
	filtered_rtm = stat_packet['filtered_rtm']
	
	filtered_rtm_avg_lst = []
	filtered_company_avg_lst = []
	raw_rtm_avg_lst = []
	raw_company_avg_lst = []
	
	for date in dates:
		raw_company_avg = stat_function(raw_company[date])
		filtered_company_avg = stat_function(filtered_company[date])
		raw_rtm_avg = stat_function(raw_rtm[date])
		filtered_rtm_avg = stat_function(filtered_rtm[date])
		print(f'{date}')
		print(f'stat_function: {stat_function}')
		print(f'  f_rtm_avg: {round(filtered_rtm_avg, 2)}')
		print(f'  f_comp_avg: {round(filtered_company_avg, 2)}')
		
		filtered_rtm_avg_lst.append(filtered_rtm_avg)
		filtered_company_avg_lst.append(filtered_company_avg)
		raw_company_avg_lst.append(raw_company_avg)
		raw_rtm_avg_lst.append(raw_rtm_avg)
		
	# Convert string dates to datetime objects
	dates2 = [datetime.strptime(date, '%Y-%m-%d %H:%M') for date in dates]
				
	x_label = 'Date'
	y_label = f'{stat_selection.capitalize()} Percent Speeding'
	title = f'Historical Distribution of {stat_selection.capitalize()} Percent Speeding'
	rtm_label = f'Filtered Rtm {stat_selection.capitalize()}'
	company_label = f'Filtered Company {stat_selection.capitalize()}'
	
	plt.figure(constrained_layout=True)
	plt.plot(dates2, filtered_rtm_avg_lst, label=rtm_label, color=settings.swto_blue, linestyle='-', linewidth=1)
	
	plt.plot(dates2, filtered_company_avg_lst, label=company_label, color='green', linestyle='-', linewidth=1)
	
	# Set major locator to one tick per month
	plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
	
	# Format the date labels to show the month and year (e.g., Jan 2024)
	plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
	
	# Rotate the labels for readability
	plt.xticks(rotation=45)
	
	# Automatically adjust layout to avoid clipping
	#plt.tight_layout()
	#plt.subplots_adjust(bottom=0.15, left=0.15)  # Adjust bottom and left margins
	
	plt.xlabel(x_label)
	plt.ylabel(y_label)
	plt.title(title)
	plt.legend()
	
	plt_type = f'{stat_selection.capitalize()}LineChart'
	plt_path = save_plt(plt, dates[-1], plt_type)
	
	plt.show()
	plt.close()
	
	return plt_path

def build_histogram(stats, scope, numBins=15, log_setting=False):
	'''
	build a histogram with raw speed list settled behind the filtered
	speed list. 
	
	set name of histogram to either Company or to RTM - rtm_name. Default rtm is chris.
	'''
	# collect speed lists
	raw_cur_spd = stats['raw_cur_spd']
	filtered_cur_spd = stats['filtered_cur_spd']
	raw_mean = sum(raw_cur_spd) / len(raw_cur_spd)
	filtered_mean = sum(filtered_cur_spd) / len(filtered_cur_spd)
	
	# build histo name
	if scope == 'company':
		title_scope = 'Company-Wide'
	else:
		title_scope = f'RTM - {scope.capitalize()}'
	
	x_label = 'Speeding Percentage'
	y_label = 'Number Of Drivers'
	title = f'{title_scope}: Weekly Distribution Of Speeding Percentages'
	
	plt.figure()
	plt.hist(
		filtered_cur_spd,
		bins=numBins,
		edgecolor='black',
		color=settings.swto_blue,
		label=f'{title_scope} percent_speeding list',
		log=log_setting
		)
	
	plt.axvline(filtered_mean, label=f'{title_scope}: Average', color='red')
	
	plt.xlabel(x_label)
	plt.ylabel(y_label)
	plt.title(title)
	plt.legend()
	plt.show()
	plt.close()
	
	return plt
	
def build_scatter(stats):
	plt.figure()
	plt.scatter(
		stats['filtered_cur_spd']
		)
	plt.show()
	plt.close()
	
	return plt

def build_line_data(date, rtm='chris'):
	conn = settings.db_connection()
	c = conn.cursor()
	company_spds = []
	rtm_spds = []
	
	# build list if driver id for rtm
	sql = f'SELECT DISTINCT driver_id FROM {settings.driverInfo} WHERE rtm = ?'
	value = (rtm,)
	c.execute(sql, value)
	results = c.fetchall()
	rtm_ids = [result[0] for result in results]
	
	# gather speeds
	sql = f'SELECT DISTINCT percent_speeding, driver_id FROM {settings.speedGaugeData} WHERE start_date = ?'
	value = (date,)
	c.execute(sql, value)
	results = c.fetchall()
	
	for i in results:
		percent_speeding = i[0]
		driver_id = i[1]
		company_spds.append(percent_speeding)
		
		if driver_id in rtm_ids:
			rtm_spds.append(percent_speeding)
	
	conn.close()
	
	# filter speeds
	company_avg = statistics.mean(company_spds)
	company_stdev = statistics.stdev(company_spds)
	max_spd = company_avg + (3 * company_stdev)
	filtered_company_spd = [speed for speed in company_spds if speed < max_spd]
	
	rtm_avg = statistics.mean(rtm_spds)
	rtm_stdev = statistics.stdev(rtm_spds)
	max_spd = rtm_avg + (3 * rtm_stdev)
	filtered_rtm_spd = [speed for speed in rtm_spds if speed < max_spd]
	
	raw_comp_avg = statistics.mean(company_spds)
	raw_rtm_avg = statistics.mean(rtm_spds)
	
	
def build_line_chart(stat_selection, rtm='chris', filtered=True):
	if stat_selection == 'average':
		stat_function = statistics.mean
	else:
		stat_function = statistics.median
	
	dates = get_date_list()
	dates2 = [datetime.strptime(date, '%Y-%m-%d %H:%M') for date in dates]
	x_label = 'Date'
	y_label = f'{stat_selection.capitalize()} Percent Speeding'
	title = f'Historical Distribution of {stat_selection.capitalize()} Percent Speeding'
	rtm_label = f'Rtm {stat_selection.capitalize()}'
	company_label = f'Company {stat_selection.capitalize()}'
	
	conn = settings.db_connection()
	c = conn.cursor()

	# build rtm driver id list
	rtm_id_lst = []
	
	sql = f'SELECT DISTINCT driver_id FROM {settings.driverInfo} WHERE rtm = ?'
	value = (rtm,)
	c.execute(sql, value)
	results = c.fetchall()
	for i in results:
		rtm_id_lst.append(i[0])
	
	company_line_data = []
	rtm_line_data = []
	
	for date in dates:	
		sql = f'SELECT DISTINCT percent_speeding, driver_id FROM {settings.speedGaugeData} WHERE start_date = ?'
		value = (date,)
		c.execute(sql, value)
		results = c.fetchall()
		
		company_spd_lst = [result[0] for result in results]
		rtm_spd_lst = [result[0] for result in results if result[1] in rtm_id_lst]
		
		company_avg = statistics.mean(company_spd_lst)
		company_stdev = statistics.stdev(company_spd_lst)
		company_max = company_avg + (3 * company_stdev)
		
		rtm_avg = statistics.mean(rtm_spd_lst)
		rtm_stdev = statistics.stdev(rtm_spd_lst)
		rtm_max = rtm_avg + (3 * rtm_stdev)
		
		filtered_company_spd_lst = [spd for spd in company_spd_lst if spd < company_max]
		
		filtered_rtm_spd_lst = [spd for spd in rtm_spd_lst if spd < rtm_max]
			
		company_stat = round(
			stat_function(
				filtered_company_spd_lst
				), 2
			)
		company_line_data.append(company_stat)
		rtm_stat = round(
			stat_function(
				filtered_rtm_spd_lst
				),2
			)
		rtm_line_data.append(rtm_stat)


		


	plt.figure(constrained_layout=True)
	plt.plot(dates2, rtm_line_data, label=rtm_label, color=settings.swto_blue, linestyle='-', linewidth=3)
	
	plt.plot(dates2, company_line_data, label=company_label, color='green', linestyle='-', linewidth=3)
	
	# Set major locator to one tick per month
	plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
	
	# Format the date labels to show the month and year (e.g., Jan 2024)
	plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
	
	# Rotate the labels for readability
	plt.xticks(rotation=45)
	
	# Automatically adjust layout to avoid clipping
	#plt.tight_layout()
	#plt.subplots_adjust(bottom=0.15, left=0.15)  # Adjust bottom and left margins
	
	plt.xlabel(x_label)
	plt.ylabel(y_label)
	plt.title(title)
	plt.legend()
	
	plt_type = f'{stat_selection.capitalize()}LineChart'
	plt_path = save_plt(plt, dates[-1], plt_type)
	
	plt.show()
	plt.close()
		
		
	conn.close()
	
def controller(stats, rtm='chris'):
	rtm_stats = stats['rtm']
	for i in rtm_stats:
		if not isinstance(rtm_stats[i], list):
			print(f'{i}: {rtm_stats[i]}')
	for i in rtm_stats:
		print(i)
	company_stats = stats['company']
	date = rtm_stats['date']
	
	all_dates = get_date_list()
	
	'''build histograms'''
	# build rtm histogram
	rtm_histo = build_histogram(rtm_stats, rtm, log_setting=False)
	company_histo = build_histogram(company_stats, 'company', log_setting=False)
	
	# build scatter plt
	#rtm_scatter = build_scatter(rtm_stats)
	
	
	
	# build line charts
	#build_avg_line()
	gen_line_chart('average')
	gen_line_chart('median')
	

if __name__ == '__main__':
	#prepare_line_data()
	#temp()
	build_line_chart('average', rtm='chris')
	build_line_chart('median', rtm='chris')
