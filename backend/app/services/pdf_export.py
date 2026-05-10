"""PDF export service — resumes and cover letters to PDF."""
import io
from html import escape


def _markdown_to_html(md: str) -> str:
  """Minimal markdown → HTML converter for resume/cover letter output."""
  lines = md.split('\n')
  html = []
  in_list = False

  for line in lines:
    stripped = line.strip()
    if not stripped:
      if in_list:
        html.append('</ul>')
        in_list = False
      html.append('<br>')
      continue

    if stripped.startswith('# '):
      if in_list:
        html.append('</ul>')
        in_list = False
      html.append(f'<h1>{escape(stripped[2:])}</h1>')
    elif stripped.startswith('## '):
      if in_list:
        html.append('</ul>')
        in_list = False
      html.append(f'<h2>{escape(stripped[3:])}</h2>')
    elif stripped.startswith('### '):
      if in_list:
        html.append('</ul>')
        in_list = False
      html.append(f'<h3>{escape(stripped[4:])}</h3>')
    elif stripped.startswith('- ') or stripped.startswith('* '):
      if not in_list:
        html.append('<ul>')
        in_list = True
      html.append(f'<li>{escape(stripped[2:])}</li>')
    elif stripped.startswith('---'):
      if in_list:
        html.append('</ul>')
        in_list = False
      html.append('<hr>')
    else:
      if in_list:
        html.append('</ul>')
        in_list = False
      # Bold and italic
      import re
      text = escape(stripped)
      text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
      text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
      html.append(f'<p>{text}</p>')

  if in_list:
    html.append('</ul>')

  return '\n'.join(html)


def generate_pdf(content: str, title: str = 'Document', css: str | None = None) -> bytes:
  """Generate a PDF from markdown content using a built-in HTML→PDF approach.

  Uses reportlab for clean PDF generation without external dependencies.
  """
  try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
    from reportlab.lib.colors import HexColor

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
      buffer,
      pagesize=A4,
      rightMargin=20*mm,
      leftMargin=20*mm,
      topMargin=20*mm,
      bottomMargin=20*mm,
      title=title,
    )

    styles = getSampleStyleSheet()
    story = []

    for line in content.split('\n'):
      stripped = line.strip()
      if not stripped:
        story.append(Spacer(1, 6))
        continue

      if stripped.startswith('# '):
        story.append(Paragraph(escape(stripped[2:]), styles['Title']))
        story.append(Spacer(1, 4))
      elif stripped.startswith('## '):
        story.append(Paragraph(escape(stripped[3:]), styles['Heading1']))
        story.append(Spacer(1, 3))
      elif stripped.startswith('### '):
        story.append(Paragraph(escape(stripped[4:]), styles['Heading2']))
        story.append(Spacer(1, 2))
      elif stripped.startswith('---'):
        story.append(HRFlowable(width='100%', color=HexColor('#cccccc')))
        story.append(Spacer(1, 4))
      elif stripped.startswith('- ') or stripped.startswith('* '):
        story.append(Paragraph(f'&bull; {escape(stripped[2:])}', styles['Normal']))
      else:
        story.append(Paragraph(escape(stripped), styles['Normal']))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

  except ImportError:
    pass

  # Fallback: plain HTML wrapped in basic HTML doc
  html_body = _markdown_to_html(content)
  full_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{escape(title)}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 210mm; padding: 20mm; margin: 0; color: #1a1a1a; line-height: 1.6; }}
  h1 {{ font-size: 20pt; margin-bottom: 8pt; color: #1e40af; }}
  h2 {{ font-size: 14pt; margin-top: 16pt; margin-bottom: 6pt; color: #374151; }}
  h3 {{ font-size: 12pt; margin-top: 12pt; margin-bottom: 4pt; color: #4b5563; }}
  p {{ font-size: 10pt; margin: 4pt 0; }}
  li {{ font-size: 10pt; margin: 2pt 0; }}
  hr {{ border: none; border-top: 1px solid #e5e7eb; margin: 12pt 0; }}
  strong {{ color: #1f2937; }}
  ul {{ margin: 4pt 0; padding-left: 20pt; }}
</style>
</head>
<body>{html_body}</body>
</html>'''

  return full_html.encode('utf-8')


async def export_resume_pdf(user_id: str) -> dict:
  """Export user's default resume as PDF."""
  from app.services.resume_generation import generate_default_resume
  result = await generate_default_resume(user_id)
  if 'error' in result:
    return result

  resume_md = result.get('resume_markdown', '')
  if not resume_md:
    return {'error': 'No resume content to export'}

  pdf_bytes = generate_pdf(resume_md, 'Resume')
  return {
    'filename': 'resume.pdf',
    'content_type': 'application/pdf',
    'data': pdf_bytes,
    'size': len(pdf_bytes),
  }


async def export_cover_letter_pdf(user_id: str, job_id: str) -> dict:
  """Export a cover letter as PDF."""
  from app.services.cover_letter import generate_cover_letter
  result = await generate_cover_letter(user_id, job_id)
  if 'error' in result:
    return result

  letter_md = result.get('cover_letter', {}).get('cover_letter_markdown', '')
  if not letter_md:
    return {'error': 'No cover letter content to export'}

  pdf_bytes = generate_pdf(letter_md, f"Cover Letter - {result.get('company', 'Company')}")
  return {
    'filename': f'cover-letter-{job_id[:8]}.pdf',
    'content_type': 'application/pdf',
    'data': pdf_bytes,
    'size': len(pdf_bytes),
  }
