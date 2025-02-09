import sys, os
import platform
import statistics
# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Now you can import settings
import settings
import matplotlib.pyplot as plt
from matplotlib import style
style.use('seaborn-talk')
import matplotlib.dates as mdates
from datetime import datetime
from pathlib import Path

# check if system is pythonista. if not then use tkinter for visualizations
system = platform.system()
is_pythonista = sys.platform == 'ios'

if system != 'Darwin' and is_pythonista:
	plt.switch_backebd('TkAgg')

'''*****Begin The Functions!****'''

def save_plt(plt, date, plt_type, rtm='chris'):
	scope = f'RTM_{rtm}'
	conn = settings.db_connection()
	c = conn.cursor()
	sql = f'SELECT DISTINCT formated_start_date FROM {settings.speedGaugeData} WHERE start_date = ?'
	value = (date,)
	c.execute(sql, value)
	formated_date = c.fetchone()[0]
	
	# build directory for images
	dir_name = 'charts_' + str(formated_date)
	chart_dir = settings.WEEKLY_REPORTS_PATH / dir_name
	chart_dir.mkdir(parents=True, exist_ok=True)
	
	img_name = f'{rtm.capitalize()}_{plt_type}_{str(formated_date)}.png'
	img_path = chart_dir / img_name
	
	plt.savefig(img_path, dpi=300, bbox_inches='tight')
	
	# build the blob
	with open(img_path, "rb") as file:
		blob_data = file.read()
	
	# update the db
	sql = f'SELECT id FROM {settings.imgStorage} WHERE start_date = ? AND plt_name = ?'
	values = (date, img_name)
	c.execute(sql, values)
	existing_record = c.fetchone()
	
	if existing_record is not None:
		sql = f'UPDATE {settings.imgStorage} SET start_date = ?, rtm = ?, plt_type = ?, plt_name = ?, plt_path = ?, plt_blob = ? WHERE id = ?'
		values = (date, rtm, plt_type, img_name, str(img_path), blob_data, existing_record[0])
		c.execute(sql, values)
	else:
		sql = f'INSERT INTO {settings.imgStorage} (start_date, rtm, plt_type, plt_name, plt_path, plt_blob) VALUES (?, ?, ?, ?, ?, ?)'
		values = (date, rtm, plt_type, img_name, str(img_path), blob_data)
		c.execute(sql, values)
	
	conn.commit()
	conn.close()
	return img_path

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
	
	plt.axvline(filtered_mean, label=f'{title_scope}: Average ({round(filtered_mean, 2)})', color='red')
	
	plt.xlabel(x_label)
	plt.ylabel(y_label)
	plt.title(title)
	plt.legend()
	
	plt_type = f'Histogram_{scope.capitalize()}'
	plt_path = save_plt(plt, stats['date'], plt_type)
	
	plt.show()
	plt.close()
	plt.clf()
	
	return plt_path
	
def build_scatter(stats):
	plt.figure()
	plt.scatter(
		stats['filtered_cur_spd']
		)
	plt.show()
	plt.close()
	
	return plt

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
	
	rtm_lifetime_avg = round(statistics.mean(rtm_line_data), 2)

	plt.figure(constrained_layout=True)
	plt.plot(dates2, rtm_line_data, label=rtm_label, color=settings.swto_blue, linestyle='-', linewidth=3)
	
	plt.plot(dates2, company_line_data, label=company_label, color='green', linestyle='-', linewidth=3)
	
	if stat_selection == 'average':
		plt.axhline(y=0.4, color='red', linewidth=1, label='percent_speeding Objective: 0.4%')
	
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
	
	plt_type = f'LineChart_{stat_selection.capitalize()}'
	plt_path = save_plt(plt, dates[-1], plt_type)
	
	plt.show()
	plt.close()
	plt.clf()
		
	conn.close()
	return plt_path
	
def controller(stats, rtm='chris'):
	rtm_stats = stats['rtm']
	company_stats = stats['company']
	
	'''build histograms'''
	# build rtm histogram
	rtm_histo_path = build_histogram(rtm_stats, rtm, log_setting=False)
	company_histo_path = build_histogram(company_stats, 'company', log_setting=False)
	
	'''build scatter plt'''
	#rtm_scatter = build_scatter(rtm_stats)
	
	'''build line charts'''
	avg_plt_path = build_line_chart('average', rtm='chris')
	median_plt_path = build_line_chart('median', rtm='chris')
	
	plt_paths = {
		'rtm_histo_path': rtm_histo_path,
		'company_histo_path': company_histo_path,
		'avg_plt_path': avg_plt_path,
		'median_plt_path': median_plt_path
	}
	
	return plt_paths
	

if __name__ == '__main__':
	#prepare_line_data()
	#temp()
	#build_line_chart('average', rtm='chris')
	print(style.available)
	for s in style.available:
		style.use(s)
		print(f'\n\n******{s}******')
		build_line_chart('average', rtm='chris')
	


