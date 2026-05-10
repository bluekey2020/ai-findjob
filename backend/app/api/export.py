from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.responses import Response
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix='/api/v1/export', tags=['export'])


@router.post('/resume/pdf')
async def export_resume(
  current_user: User = Depends(get_current_user),
):
  """Export the user's default resume as PDF."""
  from app.services.pdf_export import export_resume_pdf
  result = await export_resume_pdf(current_user.id)
  if 'error' in result:
    raise HTTPException(status_code=400, detail=result['error'])
  return Response(
    content=result['data'],
    media_type='application/pdf',
    headers={'Content-Disposition': f"attachment; filename={result['filename']}"},
  )


@router.post('/cover-letter/pdf')
async def export_cover_letter(
  job_id: str = Form(...),
  current_user: User = Depends(get_current_user),
):
  """Export a cover letter as PDF."""
  from app.services.pdf_export import export_cover_letter_pdf
  result = await export_cover_letter_pdf(current_user.id, job_id)
  if 'error' in result:
    raise HTTPException(status_code=400, detail=result['error'])
  return Response(
    content=result['data'],
    media_type='application/pdf',
    headers={'Content-Disposition': f"attachment; filename={result['filename']}"},
  )
