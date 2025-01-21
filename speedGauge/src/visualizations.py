import sys, os
# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Now you can import settings
import settings
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime



def gen_box_chart(data_packet):
	x_label = 'Speeding Percentage'
	title = 'Box Plot of Weekly Speeding Percentages'
	speed_list = data_packet['speed_list']
	
	plt.figure()
	plt.boxplot(speed_list, vert=False, showmeans=True, showfliers=True)
	plt.xlabel(x_label)
	plt.title(title)
	
	return plt
	









def gen_histogram(stats, numBins=15):
	x_label = 'Speeding Percentage'
	y_label = 'Number Of Drivers'
	title = 'Distribution Of Speeding Percentages For The Week'
	speed_list = stats['speed_list']
	
	plt.figure()
	plt.hist(speed_list, bins=numBins, edgecolor='black', color='blue', label='Rtm Stats')
	
	plt.xlabel(x_label)
	plt.ylabel(y_label)
	plt.title(title)
	
	return plt




def gen_line_chart(stat_selection, rtm_history, company_history):
	dates = []
	
	rtm_stat_list = [] # median or avg
	company_stat_list = []
	
	# build chart labels
	rtm_label = f'RTM {stat_selection.capitalize()}'
	company_label = f'Company {stat_selection.capitalize()}'
	
	# get dates list
	for dict in rtm_history:
		dates.append(dict['date'])
	dates.sort()
	
	# Convert string dates to datetime objects
	dates2 = [datetime.strptime(date, '%Y-%m-%d %H:%M') for date in dates]
	
	# organize dates(x) and stats(y)
	for date in dates:
		for dict in rtm_history:
			if dict['date'] == date:
				rtm_stat_list.append(dict[stat_selection])
		
		for dict in company_history:
			if dict['date'] == date:
				company_stat_list.append(dict[stat_selection])
				
	x_label = 'Date'
	y_label = f'{stat_selection.capitalize()} Percent Speeding'
	title = f'Historical distribution of {stat_selection.capitalize()} Percent Speeding'
	
	plt.figure(constrained_layout=True)
	plt.plot(dates2, rtm_stat_list, label=rtm_label, color='Blue', linestyle='-')
	
	plt.plot(dates2, company_stat_list, label=company_label, color='green', linestyle='-')
	
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
	
	return plt




def generate_box_chart(data_packet):
	'''
	data_packet is a dictionary with
	some keys:
		title: title for chart
		
		xlabel: label for x axis
		
		ylabel: label for y axis
		
		data_set: the data set for use in
		the box chart
		
	this returns the chart
	'''

	title = data_packet['title']
	x_label = data_packet['xlabel']
	data_set = data_packet['data_set']
	
	plt.boxplot(data_set, vert=False, showmeans=True)
	plt.xlabel(x_label)
	plt.title(title)
	#plt.style.use('ggplot')
	return plt
	
	
	
	







def generate_histogram(data_packet, numBins=15):
	'''
	data_packet is a dictionary with
	some keys:
		title: title for chart
		
		xlabel: label for x axis
		
		ylabel: label for y axis
		
		data_set: the data set for use in
		the histogram
		
	this returns the chart
	'''
	
	data_set = data_packet['data_set']
	x_label = data_packet['xlabel']
	y_label = data_packet['ylabel']
	title = data_packet['title']
	
	plt.hist(data_set, bins=numBins, edgecolor='black')
	plt.xlabel(x_label)
	plt.ylabel(y_label)
	plt.title(title)
	
	return plt
	
	




def historic_median(data_packet):
	'''
	historical_data = {
		'xlabel': 'Median Speeding Percentage',
		'ylabel': 'Date',
		'title': 'Historical distrobution of median speeding percentages',
		'data_set': historical_data_set
	}
	'''

	medians = []
	raw_means = []
	start_dates = []
	
	for dict in 		data_packet['data_set']:
		start_dates.append(dict['start_date'])
		
	start_dates.sort()
	
	# Convert string dates to datetime objects
	dates = [datetime.strptime(date, '%Y-%m-%d %H:%M') for date in start_dates]

	# extract median from dict
	for date in start_dates:
		for dict in data_packet['data_set']:
			if dict['start_date'] == date:
				# isolate dict
				analytic_dict = dict['analasis']
				
				# extract median
				median = analytic_dict['median']
				
				raw_mean = analytic_dict['raw_mean']
				
				# save the median
				medians.append(median)
				raw_means.append(raw_mean)
	
	x_label = data_packet['xlabel']
	y_label = data_packet['ylabel']
	title = data_packet['title']
	
	plt.plot(dates, medians, label='Median', color='Blue', linestyle='-')
	plt.plot(dates, raw_means, label='Average', color='green', linestyle='-')
	
	# Set major locator to one tick per month
	plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
	
	# Format the date labels to show the month and year (e.g., Jan 2024)
	plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))  # '%b' = month abbreviation, '%Y' = year
	
	# Rotate the labels for readability
	#plt.xticks(rotation=45)
	
	# Automatically adjust layout to avoid clipping
	#plt.tight_layout()
	
	plt.xlabel(x_label)
	plt.ylabel(y_label)
	plt.title(title)
	plt.legend()

	return plt
