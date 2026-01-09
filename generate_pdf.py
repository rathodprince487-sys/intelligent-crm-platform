#!/usr/bin/env python3
"""
Simple PDF generator for project documentation
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from pathlib import Path
import re

# Read markdown file
md_file = Path("PROJECT_DOCUMENTATION.md")
content = md_file.read_text()

# Create PDF
pdf_file = "PROJECT_DOCUMENTATION.pdf"
doc = SimpleDocTemplate(pdf_file, pagesize=A4,
                        rightMargin=72, leftMargin=72,
                        topMargin=72, bottomMargin=18)

# Container for the 'Flowable' objects
elements = []

# Define styles
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))

# Title style
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=24,
    textColor=colors.HexColor('#2563eb'),
    spaceAfter=30,
    alignment=TA_CENTER,
    fontName='Helvetica-Bold'
)

# Heading styles
h1_style = ParagraphStyle(
    'CustomH1',
    parent=styles['Heading1'],
    fontSize=18,
    textColor=colors.HexColor('#2563eb'),
    spaceAfter=12,
    spaceBefore=12,
    fontName='Helvetica-Bold'
)

h2_style = ParagraphStyle(
    'CustomH2',
    parent=styles['Heading2'],
    fontSize=14,
    textColor=colors.HexColor('#1e40af'),
    spaceAfter=10,
    spaceBefore=10,
    fontName='Helvetica-Bold'
)

h3_style = ParagraphStyle(
    'CustomH3',
    parent=styles['Heading3'],
    fontSize=12,
    textColor=colors.HexColor('#1e3a8a'),
    spaceAfter=8,
    spaceBefore=8,
    fontName='Helvetica-Bold'
)

body_style = ParagraphStyle(
    'CustomBody',
    parent=styles['BodyText'],
    fontSize=10,
    spaceAfter=6,
    alignment=TA_JUSTIFY
)

code_style = ParagraphStyle(
    'Code',
    parent=styles['Code'],
    fontSize=8,
    fontName='Courier',
    textColor=colors.HexColor('#dc2626'),
    backColor=colors.HexColor('#f1f5f9'),
    leftIndent=10,
    rightIndent=10
)

# Parse markdown and convert to PDF elements
lines = content.split('\n')
i = 0

print("Generating PDF from markdown...")

while i < len(lines):
    line = lines[i].strip()
    
    # Skip empty lines
    if not line:
        i += 1
        continue
    
    # Title (first H1)
    if line.startswith('# ') and i < 5:
        text = line[2:].strip()
        elements.append(Paragraph(text, title_style))
        elements.append(Spacer(1, 0.2*inch))
        i += 1
        continue
    
    # H1
    if line.startswith('# '):
        elements.append(PageBreak())
        text = line[2:].strip()
        elements.append(Paragraph(text, h1_style))
        elements.append(Spacer(1, 0.1*inch))
        i += 1
        continue
    
    # H2
    if line.startswith('## '):
        text = line[3:].strip()
        elements.append(Paragraph(text, h2_style))
        elements.append(Spacer(1, 0.08*inch))
        i += 1
        continue
    
    # H3
    if line.startswith('### '):
        text = line[4:].strip()
        elements.append(Paragraph(text, h3_style))
        elements.append(Spacer(1, 0.06*inch))
        i += 1
        continue
    
    # Horizontal rule
    if line.startswith('---'):
        elements.append(Spacer(1, 0.1*inch))
        i += 1
        continue
    
    # Code blocks
    if line.startswith('```'):
        code_lines = []
        i += 1
        while i < len(lines) and not lines[i].strip().startswith('```'):
            code_lines.append(lines[i])
            i += 1
        code_text = '<br/>'.join(code_lines[:20])  # Limit code block size
        if code_lines:
            elements.append(Paragraph(f'<font name="Courier" size="8">{code_text}</font>', code_style))
            elements.append(Spacer(1, 0.1*inch))
        i += 1
        continue
    
    # Bullet points
    if line.startswith('- ') or line.startswith('* '):
        text = '• ' + line[2:].strip()
        # Remove markdown formatting
        text = text.replace('**', '<b>').replace('**', '</b>')
        text = text.replace('`', '<font name="Courier">')
        text = text.replace('`', '</font>')
        elements.append(Paragraph(text, body_style))
        i += 1
        continue
    
    # Numbered lists
    if re.match(r'^\d+\.', line):
        text = line.strip()
        text = text.replace('**', '<b>').replace('**', '</b>')
        elements.append(Paragraph(text, body_style))
        i += 1
        continue
    
    # Regular paragraphs
    if line and not line.startswith('#'):
        text = line
        # Basic markdown to HTML conversion
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
        text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
        text = re.sub(r'`(.*?)`', r'<font name="Courier" color="#dc2626">\1</font>', text)
        
        # Remove markdown links but keep text
        text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
        
        elements.append(Paragraph(text, body_style))
        elements.append(Spacer(1, 0.05*inch))
    
    i += 1

# Build PDF
print("Building PDF document...")
doc.build(elements)
print(f"✅ PDF generated successfully: {pdf_file}")
print(f"📄 File size: {Path(pdf_file).stat().st_size / 1024:.1f} KB")
