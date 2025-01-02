
import math
import statistics
import numpy as np






def weekly_stats_analysis(data_packets, data_packets2, date):
	'''
	data_packets is a list of
	dictionaries. each dictionary has
	the keys:
		driver_id
		driver_name
		percent_speeding
		
	used primarly to make box chart and
	stuff
	'''
	print('Begininng analysis...')
	
	speed_list = [] # this week
	speed_list2 = [] # last week
	high_outliers = []
	outlier_dicts = []
	std1 = []
	std2 = []
	std3 = []
	std4plus = []
	
	# sort this week data
	for dict in data_packets:
		speed_list.append(dict['percent_speeding'])
	
	# sort last week data
	for dict in data_packets2:
		speed_list2.append(dict['percent_speeding'])
		
	speed_list.sort()
	speed_list2.sort()
	
	# get the median and mean
	median = statistics.median(speed_list)
	avg = statistics.mean(speed_list)
	median2 = statistics.median(speed_list2)
	avg2 = statistics.mean(speed_list2)
	
	# get median percent change
	if median2 == 0:
		median_change = ((median - median2) / (median2 + 1)) * 100
	else:
		median_change = ((median - median2) / median2) * 100
	
	# get average percent change
	if avg2 == 0:
		avg_change = ((avg - avg2) / (avg2 + 1)) * 100
	else:
		avg_change = ((avg - avg2) / avg2) * 100
	
	# clean up and round the results
	round_median_change = f'{round(median_change, 2)}'
	round_avg_change = f'{round(avg_change, 2)}'
	
	# get standard deviation
	stdev = statistics.stdev(speed_list)
	
	# updata data_packets with stdev
	for dict in data_packets:
		# determine how many standard 
		# deviations from the mean this
		# driver is at
		percent_speeding = dict['percent_speeding']
		num_std_devs = math.floor(abs(percent_speeding - avg) / stdev) + 1
		
		# update dict with number of
		# standard deviations
		dict['num_stdevs'] = num_std_devs
		
		if num_std_devs == 1:
			std1.append(dict)
		elif num_std_devs == 2:
			std2.append(dict)
		elif num_std_devs == 3:
			std3.append(dict)
		else:
			std4plus.append(dict)

	# iqr stuff to find/filter outliers
	# just google what iqr is
	q1 = np.percentile(speed_list, 25)
	#q3 = np.percentile(speed_list, 75)
	t = 0.75 * (len(speed_list) + 1)
	tlow = math.floor(t)
	thigh = math.ceil(t)
	
	q3 = (speed_list[tlow]+speed_list[thigh]) /2
	
	iqr = q3 - q1
	high_range_iqr = q3 + (iqr * 1.5)
	low_range_iqr = q1 - (iqr * 1.5)
	
	# make list of outlier speeds
	for speed in speed_list:
		if speed > high_range_iqr:
			high_outliers.append(speed)
			
	# put together info on outliers
	for dict in data_packets:
		if dict['percent_speeding'] in high_outliers:
			outlier_dicts.append(dict)
			
			# update dict to indidate 
			# outlier status
			dict['outlier'] = True
		else:
			dict['outlier'] = False
		
	# get last weeks info
	
			
	
	# put stats into dict
	stats_dict = {
		'date': date,
		'sample_size': len(speed_list),
		'std': stdev,
		'1std': std1,
		'2std': std2,
		'3std': std3,
		'4stdplus': std4plus,
		'avg': avg,
		'prev_avg': avg2,
		'abs_avg_change': avg - avg2,
		'percent_avg_change': round_avg_change,
		'median': median,
		'prev_median': median2,
		'abs_median_change': median - median2,
		'percent_median_change': round_median_change,
		'q1': q1,
		'q3': q3,
		'iqr': iqr,
		'high_range_iqr': high_range_iqr,
		'low_range_iqr': low_range_iqr,
		'speed_list': speed_list,
		'num_iqr_outliers': len(outlier_dicts)
		}

		
	bundled_dicts = {
		'stats': stats_dict,
		'outliers': outlier_dicts,
		'driver_info': data_packets
	}
	
	return bundled_dicts

	







def print_stats(data_package, scope):
	'''
	an orderly way to print out the 
	stats. run this from the main file
	'''
	# print out info
	stats = data_package['stats']
	outliers = data_package['outliers']
	
	print(f'\nWeek begin date: {stats["date"]}')
	print(f'Number of drivers in this analysis: {stats["sample_size"]}\n')
	
	print(f'******{scope} Stats******')
	print(f'*****Averages Analysis*****\n')
	
	print(f'Current average percent speeding: {stats["avg"]}')
	print(f'Last week average percent Speeding: {stats["prev_avg"]}')
	print(f'Absolute change in average from last week: {stats["abs_avg_change"]}')
	print(f'Percentage change in average from last week: {stats["percent_avg_change"]}')
	print(f'Standard deviation: {stats["std"]}')
	print(f'Number of drivers per standard deviation:')
	print(f'	1 standard deviation: {len(stats["1std"])}')
	print(f'	2 standard deviations: {len(stats["2std"])}')
	print(f'	3 standard deviations: {len(stats["3std"])}')
	print(f'	4+ standard deviations: {len(stats["4stdplus"])}')
	
	selection = input('\nPrint out drivers > 4 standard deviations from the mean?\nEnter y for yes: ')
	if selection == 'y':
		print('\n*****High Standard Deviation Drivers*****\n')
		for dict in stats['4stdplus']:
			print(f'Driver Name: {dict["driver_name"]}')
			print(f'Percent Speeding: {dict["percent_speeding"]}')
			print(f'Standard Deviations from the Mean: {dict["num_stdevs"]}\n')
	
	else:
		print('\nNo printout requested. Resuming....\n')
	
	print(f'*****Median Analysis*****\n')
	print(f'Current median: {stats["median"]}')
	print(f'Previous week median: {stats["prev_median"]}')
	print(f'Absolute change in median: {stats["abs_median_change"]}')
	print(f'Percent change in median: {stats["percent_median_change"]}')
	print(f'IQR: {stats["iqr"]}')
	print(f'High-range IQR: {stats["high_range_iqr"]}')
	print(f'Number of driver outliers: {stats["num_iqr_outliers"]}\n')
	
	selection = input(f'Print out driver info for median outliers?\nEnter y to print: ')
	if selection == 'y':
		print(f'****Median Outliers****\n')
		for dict in outliers:
			print(f'Driver Name: {dict["driver_name"]}')
			print(f'Percent speeding: {dict["percent_speeding"]}')
			print(f'Distance past high-range IQR: {dict["percent_speeding"] - stats["high_range_iqr"]}\n')
		
	print('*****PRINTOUT COMPLETE*****\n')
		
	
	
	
	
	
	
	
	


	


