from pathlib import Path
import hashlib, uuid
from fastapi import UploadFile, HTTPException
from app.core.config import settings
BASE=Path('./storage/documents'); BASE.mkdir(parents=True,exist_ok=True)
ALLOWED_TYPES={'application/pdf','image/jpeg','image/png','image/webp'}
MAX_BYTES=settings.max_upload_mb*1024*1024
async def save_upload(upload: UploadFile):
    if upload.content_type not in ALLOWED_TYPES: raise HTTPException(415,'Unsupported document type')
    data=await upload.read()
    if not data: raise HTTPException(400,'Empty file')
    if len(data)>MAX_BYTES: raise HTTPException(413,f'File exceeds {settings.max_upload_mb} MB limit')
    digest=hashlib.sha256(data).hexdigest(); key=f'{uuid.uuid4()}-{digest}'
    path=BASE/f'{key}{Path(upload.filename or "").suffix.lower()}'; path.write_bytes(data)
    return {'storage_key':str(path),'sha256':digest,'size':len(data),'content_type':upload.content_type,'filename':upload.filename or 'document'}
