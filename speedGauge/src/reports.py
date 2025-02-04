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

def build_output_path(date):
	conn = settings.db_connection()
	c = conn.cursor()
	
	sql = f'SELECT formated_start_date FROM {settings.speedGaugeData} WHERE start_date = ?'
	value = (date,)
	c.execute(sql, value)
	result = c.fetchone()[0]

	conn.close()
	
	

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
	
	
	
	content = []
	content.extend(create_overview_frame(stats_package, scope, plt_paths, styles, doc))
	content.append(PageBreak())	
	content.extend(create_avg_frame(stats_package, scope, plt_paths, styles, doc))
	
	content.append(PageBreak())
	content.extend(create_median_frame(stats_package, scope, plt_paths, styles, doc))

	

	doc.build(content)
	
if __name__ == '__main__':
	import json
	with open('stats.json', 'r') as json_file:
		stats = json.load(json_file)
	
	plt_paths = {}
	
	create_report(stats, plt_paths)
