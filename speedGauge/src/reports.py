from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image, Spacer, PageBreak, Frame, PageTemplate
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import HRFlowable
from pathlib import Path
import sys, os
from datetime import datetime
from reportlab.lib.units import inch
# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Now you can import settings
import settings




def add_logo(canvas, doc):
	logo_path = Path(settings.IMG_ASSETS_PATH) / 'swto_img.png'
	
	x = doc.pagesize[0] - 1.5 * inch
	y = 0.5 * inch
	canvas.drawImage(logo_path, x, y, width=1 * inch, height=1 * inch, preserveAspectRatio=True, mask='auto')






def insert_swto_icon(content, doc):
	icon_content = []
	icon_dimention = 50
	hLine_width = '50%'
	hLine_thickness = 3
	
	#page_height = 11 * 72
	#top_margin = doc.topMargin
	#bottom_margin = doc.bottomMargin
	#content_height = sum([elem.wrap(doc.width, doc.height)[1] for elem in content])
	
	#remaining_space = page_height - content_height - top_margin - bottom_margin
	#spacer_height = remaining_space / 2 - icon_dimention
	
	#if spacer_height > 0:
		#content.append(Spacer(1, spacer_height))
	
	spacer_height = icon_dimention
	icon_content.append(Spacer(1, spacer_height))
	icon_content.append(HRFlowable(
		width=hLine_width,
		thickness=hLine_thickness,
		color=settings.swto_blue,
		spaceBefore=0,
		spaceAfter=5
		))
	
	icon_path = Path(settings.IMG_ASSETS_PATH) / 'swto_img.png'
	
	icon = Image(
		icon_path,
		width = icon_dimention,
		height = icon_dimention
		)
	
	icon.hAlign = 'CENTER'
	icon_content.append(icon)
	
	icon_content.append(HRFlowable(width=hLine_width,
	thickness=hLine_thickness,
	color=settings.swto_blue,
	spaceBefore=5,
	spaceAfter=0
	))
	
	icon_content.append(PageBreak())
	
	return icon_content
	
	







def build_output_path(processing_data, scope):
	REPORTS_PATH = Path(settings.REPORTS_PATH)
	stats = processing_data['stats']
	red = settings.red
	green = settings.green
	
	
	
	current_date = stats['date']
	
	# Parse date into a datetime object
	date_obj = datetime.strptime(current_date, "%Y-%m-%d %H:%M")

	# Format it into "12Dec2024"
	formatted_date = date_obj.strftime("%d%b%Y").upper()
	
	report_dir = REPORTS_PATH / formatted_date
	report_dir.mkdir(parents=True, exist_ok=True)
	
	file_name = f'{formatted_date}_{scope}.pdf'
	
	file_path = report_dir / file_name
	
	return file_path
	
	







def create_overview_frame(stats_package, scope, plt_paths, styles, doc):
	stats = stats_package['stats']
	content = []
	
	rtm_histogram_path = str(plt_paths['rtm_histogram'])
	company_histogram_path = str(plt_paths['company_histogram'])
	
	content.append(Paragraph(f'Overview for {scope}', styles['Heading1']))
	content.append(Paragraph(f'Week begin date: {stats["date"]}', styles['Heading2']))
	content.append(Spacer(1, 20))
	
	content.append(Paragraph(f'Number of drivers in this analysis: {stats["sample_size"]}\n', styles['BodyText']))
	
	content.append(Spacer(1,10))
	
	content.append(HRFlowable(width="75%", thickness=1, color="black", spaceBefore=10, spaceAfter=10))
	
	content.append(Paragraph(f'RTM Histogram Of Speeding Percents', styles['centeredText']))
	rtm_img = Image(str(rtm_histogram_path), width=4*inch, height=2.4*inch)
	content.append(rtm_img)
	content.append(Spacer(1,0.5*inch))
	
	content.append(Paragraph(f'Company-Wide Histogram Of Speeding Percents', styles['centeredText']))
	
	company_img = Image(company_histogram_path, width=4*inch, height=2.4*inch)
	content.append(company_img)
	
	
	return content
	
	





def create_avg_frame(stats_package, scope, plt_paths, styles, doc):
	stats = stats_package['stats']
	driver_dicts = stats_package['driver_info']
	high_std_list = []
	centered_style = ParagraphStyle(name='CenteredText', parent=styles['BodyText'], alignment=1)
	
	content = []
	red = settings.red
	green = settings.green
	warning_orange = settings.warning_orange
	
	avg = round(stats['avg'], 3)
	prev_avg = round(stats['prev_avg'], 3)
	
	abs_avg_change = stats['abs_avg_change']
	abs_avg_change = float(abs_avg_change)
	if abs_avg_change >= 0:
		aac_indicator = '+'
	else:
		aac_indicator = '-'
	abs_avg_change = round(abs_avg_change, 3)
	abs_color = green if abs_avg_change < 0 else red
	abs_arrow = "&#x2193;" if abs_avg_change < 0 else "&#x2191;"  # Unicode arrows: ↑ (2191) and ↓ (2193)
	
	percent_avg_change = float(stats['percent_avg_change'])
	if percent_avg_change >= 0:
		pac_indicator = '+'
	else:
		pac_indicator = '-'
	percent_avg_change = round(percent_avg_change, 3)
	percent_change_color = green if percent_avg_change < 0 else red
	percent_arrow = "&#x2193;" if percent_avg_change < 0 else "&#x2191;"  # Unicode arrows: ↑ (2191) and ↓ (2193)
	
	std = round(stats['std'], 4)
	std1 = stats['1std']
	std2 = stats['2std']
	std3 = stats['3std']
	std4plus = stats['4stdplus']
	
	# sort dictionarys in the list
	std4plus.sort(key=lambda x: x['percent_speeding'])
	
	# build std4 table
	tbl_data = [['Driver Name', 'Speeding Percentage', 'Standard Deviations']]
	
	# populate table info
	for driver in std4plus:
		tbl_data.append([driver['driver_name'], Paragraph(f'<font color={red}><strong>{driver["percent_speeding"]}%</strong></font>', centered_style), driver['num_stdevs']])
	
	# create table
	std_table = Table(tbl_data, colWidths=[2*inch, 2*inch, 2*inch])
	
	# Style the Table
	std_table.setStyle(TableStyle([
		('BACKGROUND', (0, 0), (-1,0), settings.swto_blue),      # Header background
		('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke), # Header text color
		('ALIGN', (0, 0), (-1, -1), 'CENTER'),            # Center alignment
		('GRID', (0, 0), (-1, -1), 1, colors.black),      # Grid lines
		('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Header font
		('FONTSIZE', (0, 0), (-1, -1), 10),               # Font size
		('BOTTOMPADDING', (0, 0), (-1, 0), 12),           # Padding for header
		('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
	]))


	
	

	content.append(Paragraph(f'Overview of Average Analysis Of Speed Percentages', styles['Heading1']))
	
	content.append(Spacer(1,10))
	content.append(Paragraph(f'Current week average percent speeding: {avg}%'))
	content.append(Paragraph(f'Previous week average percent speeding: {prev_avg}%'))
	content.append(Paragraph(f'Absolute value change in average: <font color={abs_color}><strong>{aac_indicator}{abs_avg_change}{abs_arrow}</strong></font>'))
	content.append(Paragraph(f'Percent change in average: <font color={percent_change_color}><strong>{pac_indicator}{percent_avg_change}% {percent_arrow}</strong></font>'))
	content.append(Spacer(1,5))
	content.append(Paragraph(f'Standard deviation: <strong>{std}</strong>'))
	content.append(Paragraph(f'Number of drivers within 1 standard deviation of the mean: <font color={green}><strong>{len(std1)}</strong></font>'))
	content.append(Paragraph(f'Number of drivers within 2 standard deviations of the mean: <font color={green}><strong>{len(std2)}</strong></font>'))
	content.append(Paragraph(f'Number of drivers within 3 standard deviations of the mean: <font color={warning_orange}><strong>{len(std3)}</strong></font>'))
	content.append(Paragraph(f'Number of drivers 4 or more standard deviations from the mean: <font color={red}><strong>{len(std4plus)}</strong></font>'))
	content.append(Spacer(1,5))
	content.append(Paragraph(f'Drivers 4 or more standard deviations from the mean:', styles['Heading2']))
	
	content.append(Spacer(1,5))
	content.append(std_table)
	content.append(Spacer(1,5))
	
	icon_brake = insert_swto_icon(content, doc)
	
	for i in icon_brake:
		content.append(i)
	
	content.append(Paragraph(f'Overview of Average Analysis Of Speed Percentages', styles['Heading1']))
	
	content.append(Spacer(1,10))
	
	content.append(Paragraph(f'Line Graph of RTM and Company Average Percent Speeding Over Time', styles['Heading2']))
	content.append(HRFlowable(
		width='50%',
		thickness=3,
		color=settings.swto_blue,
		spaceBefore=1,
		spaceAfter=0
	))
	
	content.append(Spacer(1,50))
	
	line_img = Image(plt_paths['mean_lineChart'], width=4*inch, height=2.4*inch)
	
	content.append(line_img)
	content.append(Spacer(1,0.5*inch))
	
	return content









def create_median_frame(stats_package, scope, plt_paths, styles, doc):
	stats = stats_package['stats']
	driver_dicts = stats_package['driver_info']
	outlier_dicts = stats_package['outliers']
	#high_std_list = []
	centered_style = ParagraphStyle(name='CenteredText', parent=styles['BodyText'], alignment=1)
	content = []
	red = settings.red
	green = settings.green
	warning_orange = settings.warning_orange
	swto_blue = settings.swto_blue
	
	iqr = stats['iqr']
	high_range_iqr = stats['high_range_iqr']
	num_iqr_outliers = stats['num_iqr_outliers']
	
	median = round(stats['median'], 3)
	prev_median = round(stats['prev_median'])
	
	abs_median_change = stats['abs_median_change']
	abs_median_change = float(abs_median_change)
	abs_median_change = round(abs_median_change, 3)
	
	if abs_median_change > 0:
		amc_indicator = '+'
	elif abs_median_change == 0:
		amc_indicator = ''
	else:
		amc_indicator = '-'
	
	abs_color = green if abs_median_change <= 0 else red
	abs_arrow = "&#x2193;" if abs_median_change < 0 else "&#x2191;"  # Unicode arrows: ↑ (2191) and ↓ (2193)
	
	percent_median_change = float(stats['percent_median_change'])
	percent_median_change = round(percent_median_change, 3)
	
	if percent_median_change > 0:
		pmc_indicator = '+'
	elif percent_median_change == 0:
		pmc_indicator = ''
	else:
		pmc_indicator = '-'
	
	percent_change_color = green if percent_median_change <= 0 else red
	percent_arrow = "&#x2193;" if percent_median_change < 0 else "&#x2191;" # Unicode arrows: ↑ (2191) and ↓ (2193)
	
	# build std4 table
	tbl_data = [
		['Driver Name', 'Speeding Percentage']
	]
	
	# sort dictionarys in the list
	outlier_dicts.sort(key=lambda x: x['percent_speeding'])
	
	# populate table info
	for dict in outlier_dicts:
		row = [
			Paragraph(dict['driver_name']), Paragraph(f'<font color={red}><strong>{dict["percent_speeding"]}%</strong></font>', centered_style)
		]
		
		tbl_data.append(row)
	
	# create table
	outlier_table = Table(tbl_data, colWidths=[2*inch, 2*inch, 2*inch])
	
	# Style the Table
	outlier_table.setStyle(TableStyle([
		('BACKGROUND', (0, 0), (-1,0), settings.swto_blue),      # Header background
		('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke), # Header text color
		('ALIGN', (0, 0), (-1, -1), 'CENTER'),            # Center alignment
		('GRID', (0, 0), (-1, -1), 1, colors.black),      # Grid lines
		('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Header font
		('FONTSIZE', (0, 0), (-1, -1), 10),               # Font size
		('BOTTOMPADDING', (0, 0), (-1, 0), 12),           # Padding for header
		('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
	]))
	
	content.append(Paragraph(f'Overview of Median Analysis Of Speed Percentages', styles['Heading1']))
	content.append(Spacer(1,10))
	content.append(Paragraph(f'Current week median percent speeding: <strong>{median}</strong>'))
	content.append(Paragraph(f'Previous week median percent speeding: <strong>{prev_median}</strong>'))
	content.append(Paragraph(f'Absolute value change in median: <font color={abs_color}><strong>{amc_indicator}{abs_median_change}{abs_arrow}</strong></font>'))
	content.append(Paragraph(f'Percent change in median: <font color={percent_change_color}><strong>{pmc_indicator}{percent_median_change}% {percent_arrow}</strong></font>'))
	content.append(Spacer(1,5))
	content.append(Paragraph(f'InterQuartile Range: <strong>{iqr}</strong>'))
	content.append(Paragraph(f'High range IQR: <strong>{high_range_iqr}</strong>'))
	content.append(Paragraph(f'Number of ststistical median outliers: <font color=red><strong>{num_iqr_outliers}</strong></font>'))
	content.append(Spacer(1,5))
	content.append(Paragraph(f'Drivers Exceeding the Upper IQR Threshold for Percent Speeding', styles['Heading2']))
	content.append(Spacer(1,5))
	content.append(outlier_table)
	content.append(Spacer(1,15))
	
	line_img = Image(
		plt_paths['median_lineChart'],
		width = 4*inch,
		height = 2.4*inch
	)
	line_txt = 'Median percent_speeding over time'
	
	rtm_box_plt = Image(
		plt_paths['rtm_boxPlot'],
		width = 4 * inch,
		height = 2.4 * inch
	)
	rtm_box_text = f'Box plot showing the IQR for the RTM {str.capitalize(scope)}. This range of drivers has {stats["num_iqr_outliers"]} outliers. The drivers with outlying speeds are listed in the table above.'
	
	company_box_plt = Image(
		plt_paths['company_boxPlot'],
		width = 4 * inch,
		height = 2.4 * inch
	)
	company_box_text = f'Box plot showing the IQR for the company as a whole. This is just for an easy visual to comare with the RTM plot'
	
	tbl_data = [
		[
			Paragraph(line_txt),
			line_img
		],
		[
			Paragraph(rtm_box_text),
			rtm_box_plt
		],
		[
			Paragraph(company_box_text),
			company_box_plt
		]
	]
	
	img_table = Table(tbl_data, colWidths=[4*inch,4*inch])
	img_table.setStyle(TableStyle([
		('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
		('ALIGN', (0, 0), (0, -1), 'LEFT'),
		('ALIGN', (1, 0), (1, -1), 'CENTER')
		]))
	
	icon_brake = insert_swto_icon(
		content,
		doc
		)
	
	for i in icon_brake:
		content.append(i)
	
	content.append(Paragraph(f'Overview of Median Analysis Of Speed Percentages', styles['Heading1']))
	
	content.append(Spacer(1,10))
		
	content.append(img_table)
	
	
	
	return content
	
	







def create_report(stats_package, scope, plt_paths):
	'''
	scope will indicate if the file is 
	rtm or company
	'''
	
	output_path = build_output_path(stats_package, scope)
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
	
	
	
	content = []
	content.extend(create_overview_frame(stats_package, scope, plt_paths, styles, doc))
	content.append(PageBreak())	
	content.extend(create_avg_frame(stats_package, scope, plt_paths, styles, doc))
	
	content.append(PageBreak())
	content.extend(create_median_frame(stats_package, scope, plt_paths, styles, doc))

	

	doc.build(content)

