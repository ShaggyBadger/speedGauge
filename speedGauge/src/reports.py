from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image, Spacer, PageBreak, Frame, PageTemplate
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
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
from src import db_utils

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

right_aligned_style = ParagraphStyle(
	name="RightAligned",
	alignment=TA_RIGHT
)

CenteredAligned = ParagraphStyle(
	name='CenteredAligned',
	alignment=TA_CENTER
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

def create_overview_frame(data_packet):
	stats = data_packet['stats']
	plt_paths = data_packet['plt_paths']
	styles = data_packet['styles']
	date = db_utils.get_max_date()
	doc = data_packet['doc']
	
	page_width = letter[0]

	rtm_stats = stats['rtm']
	cur_week_rtm = rtm_stats[-1]
	rtm = stats['rtm_name']
	company_stats = stats['company']
	cur_week_company = company_stats[-1]
	
	avg_plt_path = str(plt_paths['avg_plt_path'])
	
	content = []
	
	line_chart_img = Image(avg_plt_path)
	
	# scale the image
	img_w = line_chart_img.drawWidth
	img_h = line_chart_img.drawHeight
	ratio = img_w / img_h
	
	new_w = page_width * 0.8
	new_h = new_w / ratio
	
	line_chart_img.drawWidth = new_w
	line_chart_img.drawHeight = new_h
	
	content.append(Paragraph(f'Overview For {rtm.capitalize()} Market', title_style))
	content.append(Paragraph(f'Week begin date: {date}', title_style))
	content.append(Spacer(1, 20))
	
	line_graph_tbl_data = [
		[
			'',
			line_chart_img,
			''
			]
		]
	
	table = Table(
		line_graph_tbl_data,
		colWidths = [
			page_width * 0.1,
			page_width * 0.8,
			page_width * 0.1
			]
		)
	style = TableStyle([
		('VALIGN', (0,0), (-1,-1), 'MIDDLE')
		])
	table.setStyle(style)
	content.append(table)

	content.append(Spacer(1,0.5*inch))
	
	# build rtm subtable
	cur_wk_avg_rtm = bld_stat_color(cur_week_rtm['average'], threshold=0.4, arrow=False, percentage=True)
	
	cur_wk_avg_company = bld_stat_color(cur_week_company['average'], threshold=0.4, arrow=False, percentage=True)
	
	percent_change_avg_rtm = bld_stat_color(cur_week_rtm['avg_percent_change'], threshold=None, arrow=True, percentage=True)
	
	percent_change_avg_company = bld_stat_color(cur_week_company['avg_percent_change'], threshold=None, arrow=True, percentage=True)
	
	abs_change_rtm = bld_stat_color(cur_week_rtm['avg_abs_change'], threshold=None, arrow=True, percentage=False)
	
	abs_change_company = bld_stat_color(cur_week_company['avg_abs_change'], threshold=None, arrow=True, percentage=False)
	
	
	rtm_sub_tbl_data = [
		[
			'Average percent_speeding', 
			cur_wk_avg_rtm
		],
		[
			'Percent Change In Average',
			percent_change_avg_rtm
			],
		[
			'Absolute Change In Average',
			abs_change_rtm
		]
	]
	rtm_sub_tbl = Table(
		rtm_sub_tbl_data
		)
		
	# build company subtable
	company_sub_tbl_data = [
		[
			'Average percent_speeding',
			cur_week_company['average']
		],
		[
			'Percent Change in Average',
			cur_week_company['avg_percent_change']
		]
	]
	company_sub_tbl = Table(
		company_sub_tbl_data
		)
	
	# build analysis table
	rtm_header = Paragraph(f'<font color="white"><strong>RTM Market Stats</strong></font>', styles['centeredText'])
	
	company_header = Paragraph(f'<font color="white"><strong>Company Stats</strong></font>', styles['centeredText'])
	analysis_tbl_data = [
		[
			'',
			rtm_header,
			'',
			company_header,
			''
		],
		['',
		rtm_sub_tbl,
		'',
		company_sub_tbl,
		'']
		]
	analysis_tbl = Table(
		analysis_tbl_data,
		colWidths = [
			page_width * 0.1,
			page_width * 0.35,
			page_width * 0.05,
			page_width * 0.35,
			page_width * 0.1
			]
		)
	
	analysis_tbl.setStyle(
		[
			('ALIGN', (0,0), (-1,0), 'CENTER'),
			('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
			('BACKGROUND', (1,0), (1,0), settings.swto_blue),
			('BACKGROUND', (3,0), (3,0), settings.swto_blue)
		]
	)
	
	rtm_sub_tbl.setStyle([
		('ROWBACKGROUNDS', (0,0), (-1,-1), ['#ffffff', '#d3d3d3'])
	])
	
	content.append(analysis_tbl)
	
	return content



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
	


def create_report(stats, plt_paths):
	rtm_stats = stats['rtm']
	date = db_utils.get_max_date()
	output_path = build_output_path(date)
	
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
	

	doc.build(content, onLaterPages=add_logo)
	
if __name__ == '__main__':
	import json
	date_list = db_utils.get_all_dates()
	conn = settings.db_connection()
	c = conn.cursor()
	sql = f'SELECT start_date, rtm, stats, plt_paths FROM {settings.analysisStorage} WHERE start_date = ?'
	value = (date_list[-1],)
	c.execute(sql, value)
	result = c.fetchone()

	stats = json.loads(result[2])
	rtm_stats = stats['rtm']
	company_stats = stats['company']
	
	for i in rtm_stats[0]:
		print(i)
	
	plt_paths = json.loads(result[3])
	
	# temporary adjustment to fix my mistake from visualizatikns. mistake is saved in the db, so we fix it here
	#median_plt_path = plt_paths['median_plt_pth']
	#plt_paths['median_plt_path'] = median_plt_path
	conn.close()

	
	create_report(stats, plt_paths)
