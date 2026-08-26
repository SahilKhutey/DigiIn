from fastapi import APIRouter,Depends,UploadFile,File,Form,HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.api.deps import current_user
from app.models.entities import Document,DocumentVersion,CorrectionCase
from app.core.storage import save_upload
from app.services.audit import audit
router=APIRouter(prefix='/documents',tags=['documents'])
@router.post('/upload')
async def upload_document(document_type:str=Form(...),title:str=Form(...),file:UploadFile=File(...),user=Depends(current_user),db:Session=Depends(get_db)):
    saved=await save_upload(file)
    doc=Document(user_id=user.id,document_type=document_type,source_type='SELF_UPLOAD',verification_status='PENDING_REVIEW',title=title)
    db.add(doc);db.flush();db.add(DocumentVersion(document_id=doc.id,version=1,storage_key=saved['storage_key'],sha256=saved['sha256']));db.commit();db.refresh(doc)
    audit(db,user.id,'DOCUMENT_UPLOADED','document',doc.id,{'sha256':saved['sha256'],'size':saved['size']})
    return {'id':doc.id,'status':doc.verification_status,'sha256':saved['sha256'],'filename':saved['filename']}
@router.get('')
def list_documents(user=Depends(current_user),db:Session=Depends(get_db)):
    return db.query(Document).filter(Document.user_id==user.id).order_by(Document.created_at.desc()).all()
@router.get('/{document_id}')
def get_document(document_id:str,user=Depends(current_user),db:Session=Depends(get_db)):
    doc=db.get(Document,document_id)
    if not doc or doc.user_id!=user.id: raise HTTPException(404,'Document not found')
    versions=db.query(DocumentVersion).filter(DocumentVersion.document_id==doc.id).all(); return {'document':doc,'versions':versions}
@router.post('/{document_id}/request-correction')
def request_correction(document_id:str,issue_type:str=Form(...),description:str=Form(...),user=Depends(current_user),db:Session=Depends(get_db)):
    doc=db.get(Document,document_id)
    if not doc or doc.user_id!=user.id: raise HTTPException(404,'Document not found')
    doc.verification_status='CORRECTION_REQUIRED';case=CorrectionCase(user_id=user.id,document_id=doc.id,issue_type=issue_type,description=description,status='OPEN');db.add(case);db.commit();db.refresh(case)
    audit(db,user.id,'DOCUMENT_CORRECTION_REQUESTED','correction_case',case.id);return {'id':case.id,'status':case.status}
