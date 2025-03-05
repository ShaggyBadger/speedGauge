import sys, os
import platform
import statistics
# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Now you can import settings
import settings
import matplotlib.pyplot as plt
from matplotlib import style
style.use('seaborn-darkgrid')
import matplotlib.dates as mdates
from datetime import datetime
from pathlib import Path
from src import db_utils

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

def build_line_chart(stats, stat_selection, rtm='chris'):
	if stat_selection == 'average':
		stat_function = statistics.mean
	else:
		stat_function = statistics.median
	
	rtm_stats = stats['rtm']
	company_stats = stats['company']
	driver_stats = stats['driver']
	
	dates = driver_stats['date_list']
	dates2 = [datetime.strptime(date, '%Y-%m-%d %H:%M') for date in dates]
	
	x_label = 'Date'
	y_label = f'{stat_selection.capitalize()} Percent Speeding'
	title = f'Historical Distribution of {stat_selection.capitalize()} Percent Speeding'
	rtm_label = f'Rtm {stat_selection.capitalize()}'
	company_label = f'Company {stat_selection.capitalize()}'
	
	company_line_data = []
	rtm_line_data = []
	driver_line_data = driver_stats['speed_list']
	
	for date in dates:	
		target_dict = None
		for dict in rtm_stats:
			if dict['date'] == date:
				rtm_line_data.append(dict[stat_selection])
		
		for dict in company_stats:
			if dict['date'] == date:
				company_line_data.append(dict[stat_selection])
		
	plt.figure(constrained_layout=True)
	#plt.figure(figsize=(6,2))
	plt.tight_layout()

	plt.plot(dates2, rtm_line_data, label=rtm_label, color=settings.swto_blue, linestyle='--', linewidth=1)
	
	plt.plot(dates2, company_line_data, label=company_label, color='green', linestyle='--', linewidth=1)
	
	plt.plot(dates2, driver_line_data, label='Driver Speeds', color='black', linestyle='-', linewidth=3)
	
	if stat_selection == 'average':
		plt.axhline(y=0.4, color='red', linewidth=1, label='percent_speeding Objective: 0.4%')
	
	# Set major locator to one tick per month
	plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
	
	# Format the date labels to show the month and year (e.g., Jan 2024)
	plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
	
	
	# Rotate the labels for readability
	plt.xticks(rotation=45)
	
	ax = plt.gca()
	ax.yaxis.set_label_position("right")
	ax.yaxis.tick_right()
	#ax.set_title(title, fontsize=8)
	#ax.legend(["Line 1"], fontsize=8, loc="upper left", bbox_to_anchor=(1, 1))
	
	# Automatically adjust layout to avoid clipping
	#plt.tight_layout()
	#plt.subplots_adjust(bottom=0.15, left=0.15)  # Adjust bottom and left margins
	
	plt.xlabel(x_label)
	plt.ylabel(y_label)
	plt.title(title)
	plt.legend()
	#plt.figure(figsize=(6,4))
	#plt.tight_layout()
	
	plt_type = f'LineChart_{stat_selection.capitalize()}'
	#plt_path = save_plt(plt, dates[-1], plt_type)
	
	plt.show()
	plt.close()
	plt.clf()
	
	#return plt_path

def controller(stats, driver_id, rtm='chris'):
	rtm_stats = stats['rtm']
	company_stats = stats['company']
	driver_stats = stats['driver']
	
	'''build histograms'''
	# build rtm histogram
	#rtm_histo_path = build_histogram(stats, rtm, log_setting=False)
	#company_histo_path = build_histogram(stats, 'company', log_setting=False)
	
	'''build scatter plt'''
	#rtm_scatter = build_scatter(rtm_stats)
	
	'''build line charts'''
	avg_plt_path = build_line_chart(stats, 'average', rtm='chris')
	#median_plt_path = build_line_chart(stats, 'median', rtm='chris')
	

