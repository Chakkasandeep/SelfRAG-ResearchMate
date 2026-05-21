from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
import tempfile
import re

def generate_pdf(review: str, citations: list[dict]) -> str:
    """
    Generates a beautifully structured academic PDF report using ReportLab.
    ReportLab is selected for its high compatibility on Windows machines
    and dependency-free setup.
    """
    # Create temp file destination
    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    tmp_path = tmp.name
    tmp.close()
    
    doc = SimpleDocTemplate(
        tmp_path,
        pagesize=letter,
        leftMargin=54,  # 0.75 in
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Custom academic theme styles (slate and emerald tones)
    primary_color = colors.HexColor("#0F172A")  # Slate-900
    accent_color = colors.HexColor("#059669")   # Emerald-600
    text_color = colors.HexColor("#1E293B")     # Slate-800
    muted_color = colors.HexColor("#64748B")    # Slate-500
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=primary_color,
        spaceAfter=15,
        alignment=TA_LEFT
    )
    
    h1_style = ParagraphStyle(
        'DocH1',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=accent_color,
        spaceBefore=15,
        spaceAfter=8,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'DocH2',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=primary_color,
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=10,
        leading=14.5,
        textColor=text_color,
        spaceAfter=10,
        alignment=TA_JUSTIFY
    )
    
    footer_style = ParagraphStyle(
        'DocFooter',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=10,
        textColor=muted_color,
        alignment=TA_CENTER
    )
    
    story = []
    
    # Document main title (resolve Markdown header tags first if any)
    review_lines = review.split("\n")
    title_text = "Literature Review Report"
    content_lines = []
    
    for line in review_lines:
        striped = line.strip()
        if striped.startswith("# "):
            title_text = striped.replace("# ", "")
        else:
            content_lines.append(line)
            
    # Add title paragraph
    story.append(Paragraph(title_text, title_style))
    story.append(Paragraph("Synthesized autonomously with ResearchMate Self-RAG Engine", ParagraphStyle('Sub', parent=body_style, fontSize=9, textColor=muted_color, fontName='Helvetica-Bold')))
    story.append(Spacer(1, 15))
    
    # Process review body text
    body_markdown = "\n".join(content_lines)
    paragraphs = body_markdown.split("\n\n")
    
    for p_text in paragraphs:
        p_text = p_text.strip()
        if not p_text:
            continue
            
        # Clean inline citation formatting for print: resolve [cite:id] to inline superscripts or numbered braces
        # We replace '[cite:ss-123]' with a formatted bracket e.g. '[ss-123]' or numbers
        p_text = re.sub(r'\[cite:([^\]]+)\]', r'[\1]', p_text)
        
        if p_text.startswith("## "):
            story.append(Paragraph(p_text.replace("## ", ""), h1_style))
        elif p_text.startswith("### "):
            story.append(Paragraph(p_text.replace("### ", ""), h2_style))
        else:
            # Escape HTML characters that could break ReportLab parser
            safe_text = p_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(safe_text, body_style))
            
    # ── REFERENCES SECTION ───────────────────────────────────
    if citations:
        story.append(Spacer(1, 15))
        story.append(Paragraph("References", h1_style))
        
        ref_table_data = []
        for idx, c in enumerate(citations):
            ref_id = Paragraph(f"<b>[{c['id']}]</b>", ParagraphStyle('RefId', parent=body_style, fontSize=9, textColor=accent_color))
            ref_body = Paragraph(
                f"{c['authors']} ({c['year'] or 'n.d.'}). <i>{c['title']}</i>. {c['source']}. Available at: {c['url']}",
                ParagraphStyle('RefBody', parent=body_style, fontSize=8.5, leading=12)
            )
            ref_table_data.append([ref_id, ref_body])
            
        ref_table = Table(ref_table_data, colWidths=[55, 449])
        ref_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(ref_table)
        
    # Footer metadata callback
    def add_page_decorations(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(primary_color)
        canvas.setLineWidth(0.5)
        # Top rule header
        canvas.line(54, 738, 558, 738)
        # Bottom rule footer
        canvas.line(54, 54, 558, 54)
        
        # Header string
        canvas.setFont('Helvetica-Bold', 7)
        canvas.setFillColor(muted_color)
        canvas.drawString(54, 744, "RESEARCHMATE AUTOMATED REVIEW SYSTEM")
        
        # Footer string
        canvas.setFont('Helvetica-Bold', 7)
        canvas.drawCentredString(doc.pagesize[0]/2.0, 42, f"Page {doc.page}")
        canvas.restoreState()

    # Build the document
    doc.build(story, onFirstPage=add_page_decorations, onLaterPages=add_page_decorations)
    return tmp_path
