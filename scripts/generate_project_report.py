"""
Generate a PDF from DETAILED_CODE_REPORT.md using ReportLab.
Produces: project report.pdf in the repository root
Formatting: A4, 1 inch margins, Times (Times-Roman), 12pt body
Note: this script implements a simple markdown->flowable converter for headers and paragraphs.
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
import textwrap
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MD_FILE = ROOT / 'DETAILED_CODE_REPORT.md'
OUT_PDF = ROOT / 'project report.pdf'

PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = inch  # 1 inch margins
CONTENT_WIDTH = PAGE_WIDTH - 2 * MARGIN

# Styles
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='Body', parent=styles['Normal'], fontName='Times-Roman', fontSize=12, leading=16, alignment=TA_JUSTIFY))
styles.add(ParagraphStyle(name='H1', parent=styles['Heading1'], fontName='Times-Roman', fontSize=18, leading=22, spaceAfter=12, alignment=TA_CENTER))
styles.add(ParagraphStyle(name='H2', parent=styles['Heading2'], fontName='Times-Roman', fontSize=14, leading=18, spaceAfter=8))
styles.add(ParagraphStyle(name='Pre', parent=styles['Code'], fontName='Courier', fontSize=9, leading=12))

# Basic markdown to flowables conversion
header1 = re.compile(r'^# (.+)')
header2 = re.compile(r'^##+\s*(.+)')
list_item = re.compile(r'^[-\*]\s+(.+)')


def md_to_flowables(md_text):
    flowables = []
    lines = md_text.splitlines()
    buffer = []

    def flush_buffer():
        nonlocal buffer
        if not buffer:
            return
        text = '\n'.join(buffer).strip()
        if text:
            # Wrap long lines for Paragraph
            flowables.append(Paragraph(text.replace('\n', '<br />'), styles['Body']))
            flowables.append(Spacer(1, 6))
        buffer = []

    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if not line:
            flush_buffer()
            i += 1
            continue
        m1 = header1.match(line)
        m2 = header2.match(line)
        mlist = list_item.match(line)
        if m1:
            flush_buffer()
            flowables.append(Paragraph(m1.group(1), styles['H1']))
            flowables.append(Spacer(1, 6))
        elif m2:
            flush_buffer()
            flowables.append(Paragraph(m2.group(1), styles['H2']))
            flowables.append(Spacer(1, 4))
        elif mlist:
            # simple list handling: collect consecutive list items
            flush_buffer()
            items = []
            while i < len(lines) and list_item.match(lines[i].rstrip()):
                items.append(list_item.match(lines[i].rstrip()).group(1))
                i += 1
            # convert to a paragraph with bullet-like markers
            for it in items:
                flowables.append(Paragraph('• ' + it, styles['Body']))
            flowables.append(Spacer(1, 6))
            continue
        else:
            # Accumulate into buffer until blank line or header
            buffer.append(line)
        i += 1
    flush_buffer()
    return flowables


def main():
    if not MD_FILE.exists():
        print(f"Markdown file not found: {MD_FILE}")
        return
    md_text = MD_FILE.read_text(encoding='utf-8')
    flowables = md_to_flowables(md_text)

    doc = SimpleDocTemplate(str(OUT_PDF), pagesize=A4,
                            leftMargin=MARGIN, rightMargin=MARGIN,
                            topMargin=MARGIN, bottomMargin=MARGIN)
    doc.build(flowables)
    print(f"Wrote PDF: {OUT_PDF} (A4, 1in margins, Times-Roman, 12pt body)")


if __name__ == '__main__':
    main()
