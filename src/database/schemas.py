from pydantic import BaseModel
from typing import Optional, Dict, Any


class ReportsInput(BaseModel):
    pass

class ReportsOutput(BaseModel):
    
    employee_code: str
    name: str
    l1_manager: Optional[str] = "N/A"
    l1_manager_code: Optional[str] = "N/A"
    l2_manager: Optional[str] = "N/A"
    l2_manager_code: Optional[str] = "N/A"
    hrbp_name: Optional[str] = "N/A"
    hrbp_code: Optional[str] = "N/A"
    location: Optional[str] = "N/A"
    joining_date: Optional[str] = "N/A"
    exit_date: Optional[str] = "N/A"
    survey_initiated_date: Optional[str] = "N/A"
    survey_submission_date: Optional[str] = "N/A"
    
    # This comes from the Employee table
    overall_sentiment: Optional[str] = "N/A"

    class Config:
        from_attributes = True


class GetReportInput(BaseModel):
    employee_code: str

class GetReportOutput(BaseModel):
    full_analysis_json: Dict[str, Any]

    class Config:
        from_attributes = True