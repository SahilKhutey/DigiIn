from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.api.deps import require_role
from app.models.entities import Document,DocumentVersion,User,Credential,CorrectionCase,Notification
from app.schemas.documents import ReviewDecision
from app.services.audit import audit
router=APIRouter(prefix='/review',tags=['review']); OFFICER=require_role('OFFICER','ADMIN')
@router.get('/documents')
def queue(user=Depends(OFFICER),db:Session=Depends(get_db)):
    return db.query(Document).filter(Document.verification_status.in_(['PENDING_REVIEW','CORRECTION_SUBMITTED'])).order_by(Document.created_at.asc()).all()
@router.get('/documents/{document_id}')
def detail(document_id:str,user=Depends(OFFICER),db:Session=Depends(get_db)):
    doc=db.get(Document,document_id)
    if not doc: raise HTTPException(404,'Document not found')
    owner=db.get(User,doc.user_id);versions=db.query(DocumentVersion).filter(DocumentVersion.document_id==doc.id).all()
    return {'document':doc,'owner':{'id':owner.id,'email':owner.email} if owner else None,'versions':versions}
@router.post('/documents/{document_id}/decision')
def decision(document_id:str,payload:ReviewDecision,user=Depends(OFFICER),db:Session=Depends(get_db)):
    doc=db.get(Document,document_id)
    if not doc: raise HTTPException(404,'Document not found')
    if payload.decision=='APPROVE':
        doc.verification_status='VERIFIED'
        if not db.query(Credential).filter(Credential.document_id==doc.id).first():
            db.add(Credential(user_id=doc.user_id,document_id=doc.id,credential_type=doc.document_type,issuer_id='GOV_REVIEW',holder_name='Verified citizen document',passing_year=0,status='VERIFIED',verification_level=3))
        db.add(Notification(user_id=doc.user_id,title='Document verified',body=f'{doc.title} has been verified by an authorized reviewer.'))
    elif payload.decision=='REJECT':
        doc.verification_status='REJECTED';db.add(Notification(user_id=doc.user_id,title='Document rejected',body=payload.reason or 'The document could not be verified.'))
    else:
        doc.verification_status='CORRECTION_REQUIRED';db.add(CorrectionCase(user_id=doc.user_id,document_id=doc.id,issue_type='REVIEW_CORRECTION',description=payload.reason or 'Reviewer requested correction.',status='OPEN'));db.add(Notification(user_id=doc.user_id,title='Correction required',body=payload.reason or 'Please correct the submitted document.'))
    db.commit();audit(db,user.id,f'DOCUMENT_{payload.decision}','document',doc.id,{'reason':payload.reason});return {'id':doc.id,'status':doc.verification_status}
