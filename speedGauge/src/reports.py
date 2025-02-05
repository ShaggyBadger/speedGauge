from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image, Spacer, PageBreak, Frame, PageTemplate
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
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
	stats = data_packet['stats']
	for i in data_packet:
		print(i)
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
	
	content.append(Paragraph(f'Overview for {rtm}', styles['Heading1']))
	content.append(Paragraph(f'Week begin date: {start_date}', styles['Heading2']))
	content.append(Spacer(1, 20))
	
	content.append(Paragraph(f'Number of drivers in this analysis: {rtm_stats["sample_size"]}\n', styles['BodyText']))
	
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

def create_avg_frame(data_packet):
	context = []
	
	return context
	
def create_median_frame(data_packet):
	context = []
	
	return context

def create_report(stats, plt_paths):
	for i in stats:
		print(i)
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

	doc.build(content)
	
if __name__ == '__main__':
	import json
	conn = settings.db_connection()
	c = conn.cursor()
	sql = f'SELECT start_date, rtm, stats, plt_paths FROM {settings.analysisStorage} ORDER BY start_date'
	c.execute(sql)
	result = c.fetchone()
	stats = json.loads(result[2])
	plt_paths = json.loads(result[3])
	conn.close()

	
	create_report(stats, plt_paths)
