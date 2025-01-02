'''
This module has functions related to 
processing the spreadsheet data. 
Ideally we will call them as needed
from the main.py file in the root
directory.
'''

import sys, os
# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Now you can import settings
import settings
import pandas as pd
import re
from datetime import datetime
import shutil
import console




	
	
	
	
	
	

def parse_date_range(date_string):
	'''
	this is chatGPT wizardry. idk how 
	it works, but it does so dont mess
	with it
	'''
	
	# Define a regex to capture the two date components
	date_pattern = r"(\w+, \w+ \d{1,2}, \d{4}, \d{2}:\d{2})"
	matches = re.findall(date_pattern, date_string)
	
	if len(matches) == 2:
		# Parse the matched date strings
		start_date_str, end_date_str = matches
		
		# Define the format matching the date string
		date_format = "%A, %B %d, %Y, %H:%M"
		
		# Convert to datetime objects
		start_date = datetime.strptime(start_date_str, date_format)
		end_date = datetime.strptime(end_date_str, date_format)
		
		# Format as "YYYY-MM-DD HH:MM" for storage in SQL
		start_date_formatted = start_date.strftime("%Y-%m-%d %H:%M")
		end_date_formatted = end_date.strftime("%Y-%m-%d %H:%M")
		
		return start_date_formatted, end_date_formatted
		
	else:
		raise ValueError("Date string format did not match expected pattern.")


	
	
	
	
	
	
	
	






def data_to_dict(intel_packet):
	'''
	this takes the spreadsheet, aka
	intel_report, and puts it into a
	dictionary. Much easier to work
	with that way.
	'''
	def sanitize_keys(row_dict):
		# Create a new dictionary with sanitized keys
		sanitized_dict = {}
		for key, value in row_dict.items():
			# Replace / and - with _
			sanitized_key = re.sub(r"[/-]", "_", key)
			sanitized_dict[sanitized_key] = value
		
		return sanitized_dict
		
		'''------------------'''
			
	df = pd.read_csv(intel_packet)
	
	# make list to hold dictionaries
	data_list = []
	
	# convert rows to dictionaries
	for index, row in df.iterrows():
		row_dict = row.to_dict()
		driver_name = row_dict['driver_name']

		# break once we get to this part
		# of spreadsheet
		if driver_name == '---':
			break
		
		# check if name starts with num,
		# if not, then its good	
		if not driver_name[0].isdigit():
			# adjust column names for db
			sanitized_dict = sanitize_keys(row_dict)
			
			# put dictionary into list
			unique = True
			
			for dict in data_list:
				if dict['driver_name'] == sanitized_dict['driver_name']:
					unique = False
				
			if unique is True:
				data_list.append(sanitized_dict)
	
	# quick check for duplicate driver 
	# names
	driver_list = []
	
	# build list of driver names
	for dict in data_list:
		driver = dict['driver_name']
		driver_list.append(driver)
		
	# quit program if duplicates exist
	if len(driver_list) != len(set(driver_list)):
		print('duplicates detected in data set')
		duplicate_list = []
		dName = None
		for i in driver_list:
			count = 0
			for j in driver_list:
				if i == j:
					count += 1
					if count > 1:
						duplicate_list.append(i)
		for i in duplicate_list:
			print(i)
			dName = i
		for dict in data_list:
			if dict['driver_name'] == dName:
				print(f'{dict["driver_name"]}: {dict["driver_id"]}')
		input()
	
	# assuming all is well, deploy data
	# package
	return data_list












def extract_date(intel_packet):
	'''
	this function gets the date string
	out of the spreadsheet and puts
	it into a usable format for python
	'''
	
	df = pd.read_csv(intel_packet)
	
	# Find the index of the row with '---'
	separator_index = df[df.iloc[:, 0] == '---'].index[0]
	
	# Date is 3ish rows below the
	# separator
	date_range = df.iloc[separator_index + 3, 0]
	
	# send the string to a cleaning
	# function
	cleaned_date = parse_date_range(date_range)
	
	# put dates into dict. much cleaner
	# that way
	date_dict = {
		'start_date': cleaned_date[0],
		'end_date': cleaned_date[1]
	}
	
	return date_dict
	















def store_img(data_packet, img_packet):
	'''
	data_packet is dict with keys:
		data_date
		scope:
			chris
			company
			
			******
			this tells if the incoming data
			is for our market only or if
			it is company wide. key of
			company is company wide,
			otherwise it will be rtm name
			******
	
	the idea is to include any needed
	supplementary information in this
	dict
	
	img_packet is dict with keys coresponding to the plots:
		histogram
		box_chart
		historic_mean
	
	the idea will be to cycle through
	the keys and use them to build the
	path for the file
		
	'''
	
	img_dir = settings.IMG_PATH
	
	weekly_report_dir = settings.WEEKLY_REPORTS_PATH
	
	data_date = data_packet['data_date']
	
	# make the directory for the week
	new_dir_path = os.path.join(weekly_report_dir, data_date)
	
	if not os.path.exists(new_dir_path):
		new_dir = os.mkdir(new_dir_path)
		console.clear()
		print(f'generated dir: {new_dir_path}')
	else:
		console.clear()
		print(f'Dir already exists: {new_dir_path}')
	
	# save the images
	for img_name in img_packet:
		plt = img_packet[img_name]
		
		file_name = f'{data_packet["scope"]}_{img_name}'
			
		file_path = os.path.join(new_dir_path, file_name)
		
		if os.path.exists(file_path):
			os.remove(file_path)
		
		plt.savefig(file_path)
		
		
		
		
		











def mv_completed_file(file_path):
	'''
	moves processed files out of
	unprocessed folder and into the
	processed folder
	'''
	
	processed_folder = settings.PROCESSED_PATH
	
	# get list of files in processed
	# folder
	files = os.listdir(processed_folder)
	print(files)
	
	# get date of file to check against
	# files in processed folder to chk
	# for duplicates
	file_date = extract_date(file_path)
	
	unique_file = True
	
	# check if there are files in the
	# processed folder
	if len(files) != 0:
		for file in files:
			file = os.path.join(processed_folder, file)
			date_dict = extract_date(file)
			
			if file_date['start_date'] == file_date['start_date']:
				unique_file = False
	
	if unique_file is True:
		# go ahead and move the file
		shutil.move(file_path, processed_folder)
		
	else:
		# prompt user to save or to
		# overwrite
		response_valid = False
		
		while response_valid is False:
			console.clear()
			
			print('File already exists in the processed folder')
			
			response = input('Enter selection for what to do:\n1 - Overwrite file\n2 - Enter file with name modifier\nEnter selection: ')
			
			valid_responses = ['1', '2']
			if response in valid_responses:
				response_valid = True
				
		if response == '1':
			# shutil.move overwrites
			# existing file with same name
			shutil.move(file_path, processed_folder)
			
			# remove file from unprocessed
			# directory
			#os.remove(file_path)
			
		else:
			file_name = os.path.basename(file_path)
			
			base_name, ext = os.path.splitext(file_name)
			
			# Construct the initial destination path
			dest_path = os.path.join(processed_folder, file_name)
			
			# Initialize a counter
			counter = 1
			
			# Check if a file with the same name already exists
			while os.path.exists(dest_path):
				# Update the file name with a numbered suffix
				new_file_name = f"{base_name}({counter}){ext}"
				dest_path = os.path.join(processed_folder, new_file_name)
				counter += 1

			# Move the file to the destination path with the updated name
			os.rename(file_path, dest_path)
			print(f"File moved to: {dest_path}")

	
