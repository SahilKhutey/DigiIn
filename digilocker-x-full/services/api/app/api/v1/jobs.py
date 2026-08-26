from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import require_role
from app.services.jobs import pipeline

router=APIRouter(prefix="/jobs",tags=["jobs"])
OPS=require_role("OFFICER","ADMIN")
QUEUE=[]

@router.get("")
def list_jobs(user=Depends(OPS)): return QUEUE

@router.post("/documents/{document_id}/enqueue")
def enqueue(document_id:str,user=Depends(OPS)):
    jobs=[]
    for j in pipeline(document_id):
        j["id"]=f"dev-{document_id}-{j['job_type']}"
        QUEUE.append(j); jobs.append(j)
    return {"document_id":document_id,"jobs":jobs}

@router.post("/{job_id}/retry")
def retry(job_id:str,user=Depends(OPS)):
    for j in QUEUE:
        if j["id"]==job_id:
            if j["status"] not in {"FAILED","RETRYING"}: raise HTTPException(409,"Job is not retryable")
            j["status"]="QUEUED"; j["attempts"]+=1
            return j
    raise HTTPException(404,"Job not found")
