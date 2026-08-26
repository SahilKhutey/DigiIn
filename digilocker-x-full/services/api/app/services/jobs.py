JOB_TYPES = ("MALWARE_SCAN","OCR","CLASSIFY","EXTRACT","DUPLICATE_CHECK","ISSUER_LOOKUP","VERIFICATION","PROOF_GENERATION")
JOB_STATES = ("QUEUED","RUNNING","SUCCEEDED","FAILED","RETRYING","CANCELLED")

def pipeline(document_id):
    return [{"document_id": document_id, "job_type": t, "status": "QUEUED", "attempts": 0} for t in JOB_TYPES[:-1]]
