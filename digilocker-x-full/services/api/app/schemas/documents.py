from pydantic import BaseModel, Field
class ReviewDecision(BaseModel):
    decision:str=Field(pattern='^(APPROVE|REJECT|REQUEST_CORRECTION)$')
    reason:str|None=None
