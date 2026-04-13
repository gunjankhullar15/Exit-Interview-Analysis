from pydantic import BaseModel
from typing import Optional, Dict, Any, List, Union
from datetime import datetime

class ReportsInput(BaseModel):
    pass

class ReportsOutput(BaseModel):
    # --- ORDERED EXACTLY AS PER FIGMA UI TABLE ---
    employee_code: str
    name: str
    department: Optional[str] = "N/A"
    designation: Optional[str] = "N/A"
    date_of_resignation: Optional[str] = "N/A"
    exit_date: Optional[str] = "N/A"
    l1_manager: Optional[str] = "N/A"
    l2_manager: Optional[str] = "N/A"          # Replaces the duplicate "L1 Manager" in UI
    hrbp_name: Optional[str] = "N/A"           # Mapped to "HRBP" in UI
    overall_sentiment: Optional[str] = "N/A"   # The 1st "Overall Sentiments" in UI
    exit_reason: Optional[str] = "N/A"         # Replaces the 2nd "Overall Sentiments" in UI

    class Config:
        from_attributes = True


class GetReportInput(BaseModel):
    employee_code: str

class GetReportOutput(BaseModel):
    full_analysis_json: Dict[str, Any]

    class Config:
        from_attributes = True

class Parameters(BaseModel):
    month: Union[str, int]  
    department: str         
    year: int

class ReasonAnalysisItem(BaseModel):
    category_name: str
    count: int
    percentage: float
    detailed_reasons: List[str]  

class DepartmentAnalysisItem(BaseModel):
    department: str
    exit_count: int

class AnalysisResponse(BaseModel):
    parameters: Parameters
    reason_analysis: List[ReasonAnalysisItem]
    department_analysis: List[DepartmentAnalysisItem]