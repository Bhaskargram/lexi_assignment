from pydantic import BaseModel, Field
from typing import List

class State(BaseModel):
    id: str
    name: str

class StateListResponse(BaseModel):
    states: List[State]

class Commission(BaseModel):
    id: str
    name: str

class CommissionListResponse(BaseModel):
    commissions: List[Commission]

class CaseSearchRequest(BaseModel):
    state: str = Field(json_schema_extra={'example': 'KARNATAKA'})
    commission: str = Field(json_schema_extra={'example': 'Bangalore 1st & Rural Additional'})
    search_value: str = Field(json_schema_extra={'example': 'REDDY'})

class Case(BaseModel):
    case_number: str
    case_stage: str
    filing_date: str
    complainant: str
    respondent: str
    complainant_advocate: str | None = None
    respondent_advocate: str | None = None
    document_link: str | None = None

class CaseListResponse(BaseModel):
    cases: List[Case]