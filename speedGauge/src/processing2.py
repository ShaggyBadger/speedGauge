import os
import sys
from datetime import datetime
from pathlib import Path

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Now you can import settings
import settings


'''*******************************'''









def save_plt(processing_data):
	'''
	scope is either:
		company
		RTM_{managerName}
	
	plt_type is histogram, boxPlot,
	etc. Use camelCase. underscore is
	for parsing the string if i need to
	do tgat sort of thing in the future
	
	this is to make the path string
	
	path string examples:
		company_histogram_01DEC2024.png
		RTM_chris_histogram_01DEC2024.png
	'''
	plt = processing_data['plt']
	current_date = processing_data['current_date']
	scope = processing_data['scope']
	plt_type = processing_data['plt_type']
	
	# Parse date into a datetime object
	date_obj = datetime.strptime(current_date, "%Y-%m-%d %H:%M")

	# Format it into "12Dec2024"
	formatted_date = date_obj.strftime("%d%b%Y").upper()
	
	# build path
	BASE_DIR = Path(settings.BASE_DIR)
	report_dir = BASE_DIR / 'images' / 'weeklyReports' / formatted_date
	
	
	if report_dir.exists():
		print(f'The directory {report_dir} already exists. Continuing on...')
	else:
		print(f'The directory {report_dir} does not exist. Creating it now...')
		report_dir.mkdir(parents=True, exist_ok=True)
		print(f'Directory {report_dir} has been created')
	
	# Build file path for saving the plot
	file_name = f"{scope}_{plt_type}_{formatted_date}.png"
	file_path = report_dir / file_name
	# Save the plot
	plt.savefig(file_path)
	print(f"Plot saved at: {file_path}")
	
	return file_path
