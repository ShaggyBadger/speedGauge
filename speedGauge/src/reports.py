from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image, Spacer, PageBreak, Frame, PageTemplate
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.platypus import HRFlowable
from reportlab.lib.units import inch

from pathlib import Path
import sys, os
from datetime import datetime

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Now you can import settings
import settings

'''
plt_paths dict has these keys:
	rtm_histo_path
	company_histo_path
	avg_plt_path
	median_plt_pth
'''
title_style = ParagraphStyle(
	name="CustomStyle",
	fontName="Helvetica-Bold",
	fontSize=24,
	leading=16,
	textColor=settings.swto_blue,
	alignment=TA_CENTER,
	spaceBefore=10,
	spaceAfter=10,
	)


def add_logo(canvas, doc):
	logo_path = Path(settings.IMG_ASSETS_PATH) / 'swto_img.png'
	
	x = doc.pagesize[0] - 1.5 * inch
	y = 0.5 * inch
	canvas.drawImage(logo_path, x, y, width=1 * inch, height=1 * inch, preserveAspectRatio=True, mask='auto')

def build_output_path(date, rtm='chris'):
	conn = settings.db_connection()
	c = conn.cursor()
	
	sql = f'SELECT formated_start_date FROM {settings.speedGaugeData} WHERE start_date = ?'
	value = (date,)
	c.execute(sql, value)
	formatted_date = c.fetchone()[0]

	conn.close()
	
	report_dir = settings.REPORTS_PATH / formatted_date
	report_dir.mkdir(parents=True, exist_ok=True)
	
	file_name = f'{formatted_date}_{rtm}.pdf'
	
	file_path = report_dir / file_name
	
	return file_path

def create_overview_frame(data_packet):
	page_width = letter[0]
	stats = data_packet['stats']

	rtm_stats = stats['rtm']
	rtm = stats['rtm_name']
	start_date = rtm_stats['date']

	company_stats = stats['company']
	date = rtm_stats['date']
	
	plt_paths = data_packet['plt_paths']
	styles = data_packet['styles']
	doc = data_packet['doc']
	
	content = []
	
	rtm_histogram_path = str(plt_paths['rtm_histo_path'])
	company_histogram_path = str(plt_paths['company_histo_path'])
	
	content.append(Paragraph(f'Overview for {rtm}', title_style))
	content.append(Paragraph(f'Week begin date: {start_date}', title_style))
	content.append(Spacer(1, 20))
	
	content.append(Paragraph(f'Number of drivers for RTM {stats["rtm_name"].capitalize()} in this analysis: {rtm_stats["sample_size"]}\n', styles['BodyText']))
	content.append(Paragraph(f'Number of drivers for the whole company in this analysis: {company_stats["sample_size"]}'))
	
	content.append(Spacer(1,10))
	content.append(HRFlowable(width="75%", thickness=1, color="black", spaceBefore=10, spaceAfter=10))
	
	rtm_img = Image(str(rtm_histogram_path), width=3.5*inch, height=2.1*inch)

	company_img = Image(company_histogram_path, width=3.5*inch, height=2.1*inch)
	
	rtm_hist_head = Paragraph(f'RTM Histogram Of Speeding Percents', styles['centeredText'])
	comp_hist_head = Paragraph(f'Company-Wide Histogram Of Speeding Percents', styles['centeredText'])
	
	tbl_data = [
		[
			'',
			rtm_hist_head,
			comp_hist_head,
			''
			],
		[
			'',
			rtm_img,
			company_img,
			''
			]
		]
	col1_w = page_width * .05
	col2_w = page_width * .45
	col3_w = page_width * .45
	col4_w = page_width * .05
	table = Table(
		tbl_data,
		colWidths = [
			col1_w,
			col2_w,
			col3_w,
			col4_w
			]
		)
	style = TableStyle([
		('VALIGN', (0,0), (1,1), 'MIDDLE')
		])
	table.setStyle(style)
	content.append(table)

	content.append(Spacer(1,0.5*inch))
	
	return content

def bld_stat_color(value, threshold=None, arrow=False, percentage=True):
	"""
	Format a statistic with color and optional arrows.

	Args:
		value (float): The numeric value to evaluate.
		threshold (float, optional): A static threshold for comparison.
		arrow (bool, optional): Whether to add an up/down arrow for percent change.

	Returns:
		Paragraph: A styled paragraph with the appropriate color and symbol.
		"""
	color = colors.black
	symbol = ""
	styles = getSampleStyleSheet()
	
	if threshold is not None:
		# Static threshold check (green if below, red if above)
		color = colors.green if value < threshold else colors.red
	else:
		# Percent change logic
		color = colors.green if value < 0 else colors.red
		if arrow:
			symbol = "&#x2193;" if value < 0 else "&#x2191;"  # Unicode arrows ↓ (2193) and ↑ (2191)
			if value == 0:
				symbol = '-'
	
	# Format the value with 2 decimal places
	formatted_value = f"{value:.2f}% {symbol}".strip() if percentage is True else f'{value:.2f} {symbol}'.strip()
	
	# Create styled paragraph
	return Paragraph(f'<font color="{color}"><strong>{formatted_value}</strong></font>', styles['BodyText'])

def stdev_tbl(data_packet):
	stats = data_packet['stats']
	page_width = letter[0]
	rtm_stats = stats['rtm']
	rtm = stats['rtm_name']
	start_date = rtm_stats['date']
	company_stats = stats['company']
	date = rtm_stats['date']
	plt_paths = data_packet['plt_paths']
	styles = data_packet['styles']
	doc = data_packet['doc']
	
	centered_style = ParagraphStyle(name='CenteredText', parent=styles['BodyText'], alignment=1)
	
	''' tbl data stuff? '''
	col1_w = page_width * .3
	col2_w = page_width * .1
	
	'''stdev data'''
	a1 = Paragraph(f'Standard Deviation:')
	b1 = Paragraph(f'<font color="{colors.black}"><strong>{rtm_stats["stdev"]}</strong></font>')
	a2 = Paragraph(f'Number of drivers within 1 standard deviation of the mean:')
	b2 = Paragraph(f'<font color="{colors.green}"><strong>{rtm_stats["1std"]}</strong></font>')
	a3 = Paragraph(f'Number of drivers within 2 standard deviations of the mean:')
	b3 = Paragraph(f'<font color="{colors.green}"><strong>{rtm_stats["2std"]}</strong></font>')
	a4 = Paragraph(f'Number of drivers within 3 standard deviations of the mean:')
	b4 = Paragraph(f'<font color="{colors.red}"><strong>{rtm_stats["3std"]}</strong></font>')
	a5 = Paragraph(f'Number of drivers 4+ standard deviations from the mean:')
	b5 = Paragraph(f'<font color="{colors.red}"><strong>{rtm_stats["4stdplus"]}</strong></font>')
	stdev_explain = Paragraph(f'Standard deviation (STDEV) measures how much something varies from the average. STDEV helps identify these extremes — 1 STDEV is typical in a data set, 2 is unusual, and 3+ indicates a major outlier. Either someone has a heavy foot or there might be something weird going on with the tracking system.', styles['Code'])
	
	sub_tbl_data = [
		[a1, b1],
		[a2, b2],
		[a3, b3],
		[a4, b4],
		[a5, b5]
		]
	
	sub_tbl = Table(
		sub_tbl_data,
		colWidths = [col1_w, col2_w]
		)
		
	style = TableStyle([
		('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
		('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.lightgrey, colors.white])])
	sub_tbl.setStyle(style)

	''' build the main table '''
	col1_w = page_width * .05
	col2_w = page_width * .45
	col3_w = page_width * .45
	col4_w = page_width * .05
		
	col2_head = Paragraph(f'<strong>Standard Deviation Primer</strong>', styles['centeredText'])
	col3_head = Paragraph(f'<strong>Standard Deviation Stats</strong>', styles['centeredText'])
	
	# each row of data gets a list in tbl_data
	tbl_data = [
	[
		'',
		col2_head,
		col3_head,
		''
		],
	[
		'',
		stdev_explain,
		sub_tbl,
		''
		]
	]
	
	table = Table(
		tbl_data,
		colWidths = [
			col1_w,
			col2_w,
			col3_w,
			col4_w
			]
		)
	style = TableStyle([
		('VALIGN', (0,0), (1,1), 'MIDDLE')
		])
	table.setStyle(style)
	
	return table
	

def create_avg_frame(data_packet):
	content = []
	spacer = Spacer(1, 0.2*inch)
	hr = HRFlowable(width='50%', thickness=5, color=settings.swto_blue)
	page_width = letter[0]
	stats = data_packet['stats']

	rtm_stats = stats['rtm']
	rtm = stats['rtm_name']
	start_date = rtm_stats['date']
	company_stats = stats['company']
	date = rtm_stats['date']
	plt_paths = data_packet['plt_paths']
	styles = data_packet['styles']
	doc = data_packet['doc']
	
	centered_style = ParagraphStyle(name='CenteredText', parent=styles['BodyText'], alignment=1)
	red = settings.red
	green = settings.green
	warning_orange = settings.warning_orange
	
	'''title for page'''
	page_title = Paragraph('Averages Analyitics', title_style)
	content.append(page_title)
	content.append(spacer)
	
	
	''' tbl data stuff? '''
	col1_w = page_width * .3
	col2_w = page_width * .1
	
	''' build the sub_tbl for col2 '''
	# mk one row per stat for averages with 2 columns

	# a1 is column a row 1 etc
	a0 = Paragraph(f'<font color={colors.white}>Rtm Average Stats</font>')
	b0 = Paragraph('')
	a1 = Paragraph(f'Current Rtm Average:')
	b1 = bld_stat_color(rtm_stats['cur_avg'], threshold=0.4)
	a2 = Paragraph(f'Last Week Rtm Average:')
	b2 = bld_stat_color(rtm_stats['prev_avg'], threshold=0.4)
	a3 = Paragraph(f'Absolute Change in percent_speeding:')
	b3 = bld_stat_color(rtm_stats['avg_abs_change'], arrow=True, percentage=False)
	a4 = Paragraph(f'Percent Change In percent_speeding:')
	b4 = bld_stat_color(rtm_stats['avg_percent_change'], arrow=True)

	a5 = Paragraph('')
	b5 = Paragraph('')
	a6 = Paragraph(f'<font color={colors.white}>Company Average Stats</font>')
	b6 = Paragraph('')
	a7 = Paragraph(f'Current Company Average:')
	b7 = bld_stat_color(company_stats['cur_avg'], threshold=0.4, arrow=False, percentage=False)
	a8 = Paragraph(f'Previous Week Company Average:')
	b8 = bld_stat_color(company_stats['prev_avg'], threshold=0.4, arrow=False, percentage=False)
	a9 = Paragraph(f'Absolute Value of Change in Company Average:')
	b9 = bld_stat_color(company_stats['avg_abs_change'], threshold=None, arrow=True, percentage=False)
	a10 = Paragraph(f'Percent Change in Company Average:')
	b10 = bld_stat_color(company_stats['avg_percent_change'], threshold=None, arrow=True, percentage=True)
	

	sub_tbl_data = [
		[a0, b0],
		[a1, b1],
		[a2, b2],
		[a3, b3],
		[a4, b4],
		[a5, b5],
		[a6, b6],
		[a7, b7],
		[a8, b8],
		[a9, b9],
		[a10, b10]
		]
	sub_tbl = Table(
		sub_tbl_data,
		colWidths = [
			col1_w,
			col2_w
			]
		)
	style = TableStyle([
		('VALIGN', (0,0), (1,1), 'MIDDLE'),
		('TEXTCOLOR', (0,0), (-1,0), colors.white),
		('ROWBACKGROUNDS', (0,0), (-1, 0), [settings.swto_blue]),
		('ROWBACKGROUNDS', (0,6), (-1, 6), [settings.swto_blue])])
	sub_tbl.setStyle(style)

	
	''' build the main table '''
	col1_w = page_width * .05
	col2_w = page_width * .45
	col3_w = page_width * .45
	col4_w = page_width * .05
	
	avg_line_path = str(plt_paths['avg_plt_path'])
	
	avg_img = Image(str(avg_line_path), width=3.5*inch, height=2.1*inch)
		
	col2_head = Paragraph(f'<font><strong>Average Statistics</strong></font>', styles['centeredText'])
	col3_head = Paragraph(f'<font><strong>Line Graph of Averages</strong></font>', styles['centeredText'])
	
	# each row of data gets a list in tbl_data
	tbl_data = [
	[
		'',
		col2_head,
		col3_head,
		''
		],
	[
		'',
		sub_tbl, # table inside this cell
		avg_img, # avg line graph
		''
		]
	]
	
	table = Table(
		tbl_data,
		colWidths = [
			col1_w,
			col2_w,
			col3_w,
			col4_w
			]
		)
	style = TableStyle([
		('VALIGN', (0,0), (1,1), 'MIDDLE'),
		('VALIGN', (2,1), (2,1), 'MIDDLE')
		])
	table.setStyle(style)
	content.append(table)
	content.append(spacer)
	content.append(spacer)
	content.append(hr)
	content.append(spacer)
	content.append(spacer)
	content.append(stdev_tbl(data_packet))
	
	return content

def median_sub_tbl(data_packet):
	page_width = letter[0]
	stats = data_packet['stats']

	rtm_stats = stats['rtm']
	rtm = stats['rtm_name']
	start_date = rtm_stats['date']
	company_stats = stats['company']
	date = rtm_stats['date']
	plt_paths = data_packet['plt_paths']
	styles = data_packet['styles']
	doc = data_packet['doc']
	
	centered_style = ParagraphStyle(name='CenteredText', parent=styles['BodyText'], alignment=1)
	red = settings.red
	green = settings.green
	warning_orange = settings.warning_orange
	
	''' tbl data stuff? '''
	col1_w = page_width * .3
	col2_w = page_width * .1
	
	'''Median data'''
	a0 = Paragraph(f'<font color={colors.white}><strong>Rtm Median Stats</strong></font>')
	b0 = Paragraph('')
	a1 = Paragraph(f'Current RTM Median:')
	b1 = bld_stat_color(rtm_stats['cur_median'], threshold=0.4, arrow=False, percentage=True)
	a2 = Paragraph(f'Last Week RTM Median')
	b2 = bld_stat_color(rtm_stats['prev_median'], threshold=0.4, arrow=False, percentage=True)
	a3 = Paragraph(f'Absolute Value of Change in Median')
	b3 = bld_stat_color(rtm_stats['median_abs_change'], threshold=None, arrow=True, percentage=True)
	a4 = Paragraph(f'Percentage Change in Median')
	b4 = bld_stat_color(rtm_stats['median_percent_change'], threshold=None, arrow=True, percentage=True)

	a5 = Paragraph('')
	b5 = Paragraph('')
	a6 = Paragraph(f'<font color={colors.white}><strong>Company Median Stats</strong></font>')
	b6 = Paragraph('')
	a7 = Paragraph(f'Current Company Median:')
	b7 = bld_stat_color(company_stats['cur_median'], threshold=0.4, arrow=False, percentage=False)
	a8 = Paragraph(f'Previous Week Company Median:')
	b8 = bld_stat_color(company_stats['prev_median'], threshold=0.4, arrow=False, percentage=False)
	a9 = Paragraph(f'Absolute Value of Change in Company Median:')
	b9 = bld_stat_color(company_stats['median_abs_change'], threshold=None, arrow=True, percentage=False)
	a10 = Paragraph(f'Percent Change in Company Median:')
	b10 = bld_stat_color(rtm_stats['median_percent_change'], threshold=None, arrow=True, percentage=True)
	
	sub_tbl_data = [
		[a0, b0],
		[a1, b1],
		[a2, b2],
		[a3, b3],
		[a4, b4],
		[a5, b5],
		[a6, b6],
		[a7, b7],
		[a8, b8],
		[a9, b9],
		[a10, b10]
		]
	sub_tbl = Table(
		sub_tbl_data,
		colWidths = [
			col1_w,
			col2_w
			]
		)
	style = TableStyle([
		('VALIGN', (0,0), (1,1), 'MIDDLE'),
		('TEXTCOLOR', (0,0), (-1,0), colors.white),
		('ROWBACKGROUNDS', (0,0), (-1, 0), [settings.swto_blue]),
		('ROWBACKGROUNDS', (0,6), (-1, 6), [settings.swto_blue])])
	sub_tbl.setStyle(style)
	
	return sub_tbl

def iqr_tbl(data_packet):
	stats = data_packet['stats']
	page_width = letter[0]
	rtm_stats = stats['rtm']
	rtm = stats['rtm_name']
	start_date = rtm_stats['date']
	company_stats = stats['company']
	date = rtm_stats['date']
	plt_paths = data_packet['plt_paths']
	styles = data_packet['styles']
	doc = data_packet['doc']
	
	centered_style = ParagraphStyle(name='CenteredText', parent=styles['BodyText'], alignment=1)
	
	''' tbl data stuff? '''
	col1_w = page_width * .3
	col2_w = page_width * .1
	
	'''iqr data'''
	a1 = Paragraph(f'<font color={colors.white}><strong>IQR:</strong></font>')
	b1 = Paragraph(f'<font color="{colors.white}"><strong>{rtm_stats["iqr"]}</strong></font>')
	a2 = Paragraph(f'Q1:')
	b2 = Paragraph(f'<font color="{colors.green}"><strong>{rtm_stats["q1"]}</strong></font>')
	a3 = Paragraph(f'Q3:')
	b3 = Paragraph(f'<font color="{colors.green}"><strong>{rtm_stats["q3"]}</strong></font>')
	a4 = Paragraph(f'High Range of IQR:')
	b4 = Paragraph(f'<font color="{colors.red}"><strong>{rtm_stats["high_range_iqr"]}</strong></font>')
	a5 = Paragraph(f'Number of RTM IQR outliers:')
	b5 = Paragraph(f'<font color="{colors.red}"><strong>{rtm_stats["num_iqr_outliers"]}</strong></font>')
	a6 = Paragraph(f'Number of Company IQR outliers:')
	b6 = Paragraph(f'<font color="{colors.red}"><strong>{company_stats["num_iqr_outliers"]}</strong></font>')
	stdev_explain = Paragraph(f'Interquartile Range (IQR) measures the spread of the middle 50% of your data. It’s the difference between the first quartile (25th percentile) and the third quartile (75th percentile), showing where the bulk of the data lies.<br/><br/>  •	1 IQR means data is typical and falls within the expected range.<br/>  •	2 IQRs suggests that the data is somewhat unusual.<br/>  •	3+ IQRs means the data point is an outlier, likely indicating something noteworthy, like a major change in behavior or a flaw in the system.<br/><br/>Typically, values beyond 1.5 times the IQR (<font color={colors.red}><strong>{round(rtm_stats["iqr"] * 1.5, 2)}</strong></font> in this case) are generally considered extreme outliers, so you might want to keep an eye on those.', styles['Code'])
	
	sub_tbl_data = [
		[a1, b1],
		[a2, b2],
		[a3, b3],
		[a4, b4],
		[a5, b5],
		[a6, b6]
		]
	
	sub_tbl = Table(
		sub_tbl_data,
		colWidths = [col1_w, col2_w]
		)
		
	style = TableStyle([
		('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
		('ROWBACKGROUNDS', (0,0), (1,0), [settings.swto_blue]),
		('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.lightgrey])])
	sub_tbl.setStyle(style)

	''' build the main table '''
	col1_w = page_width * .05
	col2_w = page_width * .45
	col3_w = page_width * .45
	col4_w = page_width * .05
		
	col2_head = Paragraph(f'<strong>InterQuartile Range Primer</strong>', styles['centeredText'])
	col3_head = Paragraph(f'<strong>Standard Deviation Stats</strong>', styles['centeredText'])
	
	# each row of data gets a list in tbl_data
	tbl_data = [
	[
		'',
		col2_head,
		col3_head,
		''
		],
	[
		'',
		stdev_explain,
		sub_tbl,
		''
		]
	]
	
	table = Table(
		tbl_data,
		colWidths = [
			col1_w,
			col2_w,
			col3_w,
			col4_w
			]
		)
	style = TableStyle([
		('VALIGN', (0,0), (2,1), 'MIDDLE')
		])
	table.setStyle(style)
	
	return table

def create_median_frame(data_packet):
	content = []
	spacer = Spacer(1, 0.2*inch)
	hr = HRFlowable(width='50%', thickness=5, color=settings.swto_blue)
	page_width = letter[0]
	stats = data_packet['stats']

	rtm_stats = stats['rtm']
	rtm = stats['rtm_name']
	start_date = rtm_stats['date']
	company_stats = stats['company']
	date = rtm_stats['date']
	plt_paths = data_packet['plt_paths']
	styles = data_packet['styles']
	doc = data_packet['doc']
	
	centered_style = ParagraphStyle(name='CenteredText', parent=styles['BodyText'], alignment=1)
	red = settings.red
	green = settings.green
	warning_orange = settings.warning_orange
	
	'''Page title part'''
	page_title = Paragraph('Median Analitics', title_style)
	content.append(page_title)
	content.append(spacer)
	
	''' build the main table '''
	col1_w = page_width * .05
	col2_w = page_width * .45
	col3_w = page_width * .45
	col4_w = page_width * .05
	median_line_path = str(plt_paths['median_plt_path'])
	median_img = Image(str(median_line_path), width=3.5*inch, height=2.1*inch)
		
	col2_head = Paragraph(f'<strong>Median Statistics</strong>', styles['centeredText'])
	col3_head = Paragraph(f'<strong>Line Graph of Median Data</strong>', styles['centeredText'])
	
	sub_tbl = median_sub_tbl(data_packet)
	
	# each row of data gets a list in tbl_data
	tbl_data = [
	[
		'',
		col2_head,
		col3_head,
		''
		],
	[
		'',
		sub_tbl, # table inside this cell
		median_img, # avg line graph
		''
		]
	]
	
	table = Table(
		tbl_data,
		colWidths = [
			col1_w,
			col2_w,
			col3_w,
			col4_w
			]
		)
	style = TableStyle([
		('VALIGN', (0,0), (1,1), 'MIDDLE')
		])
	table.setStyle(style)
	content.append(table)
	content.append(spacer)
	content.append(spacer)
	content.append(hr)
	content.append(spacer)


	content.append(iqr_tbl(data_packet))
	
	
	return content

def create_outlier_frame(data_packet):
	content = []
	centered_style = ParagraphStyle(
		name="CenteredStyle",
		alignment=TA_CENTER
		)
	spacer = Spacer(1, 0.2*inch)
	hr = HRFlowable(width='50%', thickness=5, color=settings.swto_blue)
	page_width = letter[0]
	styles = data_packet['styles']
	doc = data_packet['doc']
	stats = data_packet['stats']
	
	rtm_stats = stats['rtm']
	rtm_outlier_list = rtm_stats['outlier_dict_list']['rtm']
	
	company_stats = stats['company']
	company_outlier_list = company_stats['outlier_dict_list']['company']
	
	#test_dict = rtm_outlier_list[0]
	#for i in test_dict:
		#print(f'{i}: {test_dict[i]}')
		
	section_title = Paragraph('Outliers', title_style)
	
	content.append(section_title)
	
	# build the table
	''' build the main table '''
	# build column names
	column_names = [
		'Driver Id',
		'Percent Speeding',
		'Standard Deviation',
		'IQR Outlier',
		'IQR Differential'
		]
	column_keys = [
		'driver_id',
		'percent_speeding',
		'driver_stdev',
		'high_iqr_status',
		'iqr_differential'
		]
	
	# build data for rtm table
	rtm_table_data = [column_names]
	
	for dict in rtm_outlier_list:
		driver_id_data = Paragraph(f'<font color={colors.black}><strong>{dict["driver_id"]}</strong></font>', centered_style)
		
		percent_speeding_data = Paragraph(f'<font color={colors.black}><strong>{dict["percent_speeding"]}</strong></font>', centered_style)
		
		stdev_color = colors.green if dict['stdev'] < 4 else colors.red
		driver_stdev_data = Paragraph(f'<font color={stdev_color}><strong>{dict["driver_stdev"]}</strong></font>', centered_style)
		
		iqr_outlier_color = colors.green if dict['high_iqr_status'] is False else colors.red
		iqr_outlier_data = Paragraph(f'<font color={iqr_outlier_color}><strong>{dict["high_iqr_status"]}</strong></font>', centered_style)
		
		iqr_differential_color = colors.green if dict['iqr_differential'] < 0 else colors.red
		iqr_differential_data = Paragraph(f'<font color={iqr_differential_color}><strong>{dict["iqr_differential"]}</strong></font>', centered_style)
		
		new_row = [
			driver_id_data,
			percent_speeding_data,
			driver_stdev_data,
			iqr_outlier_data,
			iqr_differential_data
			]
		
		rtm_table_data.append(new_row)

	# build data for company table
	company_table_data = [column_names]
	
	for dict in company_outlier_list:
		driver_id_data = Paragraph(f'<font color={colors.black}><strong>{dict["driver_id"]}</strong></font>', centered_style)
		
		percent_speeding_data = Paragraph(f'<font color={colors.black}><strong>{dict["percent_speeding"]}</strong></font>', centered_style)
		
		stdev_color = colors.green if dict['stdev'] < 4 else colors.red
		driver_stdev_data = Paragraph(f'<font color={stdev_color}><strong>{dict["driver_stdev"]}</strong></font>', centered_style)
		
		iqr_outlier_color = colors.green if dict['high_iqr_status'] is False else colors.red
		iqr_outlier_data = Paragraph(f'<font color={iqr_outlier_color}><strong>{dict["high_iqr_status"]}</strong></font>', centered_style)
		
		iqr_differential_color = colors.green if dict['iqr_differential'] < 0 else colors.red
		iqr_differential_data = Paragraph(f'<font color={iqr_differential_color}><strong>{dict["iqr_differential"]}</strong></font>', centered_style)
		
		new_row = [
			driver_id_data,
			percent_speeding_data,
			driver_stdev_data,
			iqr_outlier_data,
			iqr_differential_data
			]
		
		company_table_data.append(new_row)
	
	# build the tables
	rtm_table = Table(rtm_table_data)
	company_table = Table(company_table_data)
	
	style = TableStyle([
		('ALIGN', (0,0), (-1,-1), 'CENTER'),
		('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
		('TEXTCOLOR', (0,0), (-1,0), colors.white),
		('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.lightgrey]),
		('ROWBACKGROUNDS', (0,0), (-1, 0), [settings.swto_blue]),
		])
		
	rtm_table.setStyle(style)
	company_table.setStyle(style)
	
	'''
	info for later formatting
	
	frame_height = doc.height
	table_height = my_table.wrap(doc.width, doc.height)[1]  # Get table height

	if table_height > (frame_height - 100):  # Adjust 100 to your graphic's height
    content.append(PageBreak())  # Move table to the next page

	content.append(my_table)
	'''
	
	rtm_header = Paragraph('Statistical Outliers: <strong>RTM</strong> Edition', centered_style)
	company_header = Paragraph('Statistical Outliers: <strong>Company</strong> Edition', centered_style)
	content.append(spacer)
	content.append(rtm_header)
	content.append(spacer)
	content.append(rtm_table)
	content.append(spacer)
	content.append(spacer)
	content.append(company_header)
	content.append(spacer)
	content.append(company_table)
	
	
	
	

	
	return content
	

def create_report(stats, plt_paths):
	rtm_stats = stats['rtm']
	output_path = build_output_path(rtm_stats['date'])
	
	frame = Frame(0.5 * inch, 0.5 * inch, 7.5 * inch, 10 * inch, id='main_frame')
	
	doc = SimpleDocTemplate(
		str(output_path),
		pagesize=letter,
		)
	styles = getSampleStyleSheet()
	
	# Add the custom PageTemplate with the logo
	doc.addPageTemplates([
		PageTemplate(id='main_frame', frames=[frame], onPage=add_logo),])
	styles.add(ParagraphStyle(name='centeredText', alignment=TA_CENTER))
	
	data_packet = {
		'stats': stats,
		'plt_paths': plt_paths,
		'styles': styles,
		'doc': doc
	}
	
	content = []
	content.extend(create_overview_frame(data_packet))
	content.append(PageBreak())	
	content.extend(create_avg_frame(data_packet))
	content.append(PageBreak())
	content.extend(create_median_frame(data_packet))
	
	content.append(PageBreak())
	content.extend(create_outlier_frame(data_packet))

	doc.build(content, onLaterPages=add_logo)
	
if __name__ == '__main__':
	import json
	conn = settings.db_connection()
	c = conn.cursor()
	sql = f'SELECT start_date, rtm, stats, plt_paths FROM {settings.analysisStorage} ORDER BY start_date'
	c.execute(sql)
	result = c.fetchone()
	stats = json.loads(result[2])
	rtm_stats = stats['rtm']
	
	plt_paths = json.loads(result[3])
	
	# temporary adjustment to fix my mistake from visualizatikns. mistake is saved in the db, so we fix it here
	#median_plt_path = plt_paths['median_plt_pth']
	#plt_paths['median_plt_path'] = median_plt_path
	conn.close()

	
	create_report(stats, plt_paths)
