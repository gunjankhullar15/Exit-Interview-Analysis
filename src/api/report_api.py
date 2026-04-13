import copy
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List

from src.database.database import get_db
from src.database.models import Employee, AnalysisReport
from src.database.schemas import ReportsOutput, GetReportOutput

router = APIRouter()

@router.get("/reports", response_model=List[ReportsOutput])
async def get_all_reports(db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Employee, AnalysisReport.exit_category)
        .outerjoin(AnalysisReport, Employee.id == AnalysisReport.employee_id)
    )
    
    result = await db.execute(stmt)
    rows = result.all()
    
    response_data = []
    for emp, exit_category in rows:
        response_data.append({
            "employee_code": emp.employee_code,
            "name": emp.name,
            "department": emp.department if emp.department else "N/A",
            "designation": emp.designation if emp.designation else "N/A",
            "date_of_resignation": emp.date_of_resignation if emp.date_of_resignation else "N/A",
            "exit_date": emp.exit_date if emp.exit_date else "N/A",
            "l1_manager": emp.l1_manager if emp.l1_manager else "N/A",
            #"l2_manager": emp.l2_manager if emp.l2_manager else "N/A",
            "hrbp_name": emp.hrbp_name if emp.hrbp_name else "N/A",
            "overall_sentiment": emp.overall_sentiment if emp.overall_sentiment else "N/A",
            "exit_reason": exit_category if exit_category else "N/A"
        })
        
    return response_data

@router.get("/report/{employee_code}", response_model=GetReportOutput)
async def get_report_by_employee_code(employee_code: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Employee).options(
        selectinload(Employee.analysis_report)
    ).filter(Employee.employee_code == employee_code)
    
    result = await db.execute(stmt)
    emp = result.scalar_one_or_none()
    
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    if not emp.analysis_report or not emp.analysis_report.full_analysis_json:
        raise HTTPException(status_code=404, detail="Analysis report not found")

    # Deep copy to ensure we don't mutate the SQLAlchemy object state
    report_data = copy.deepcopy(emp.analysis_report.full_analysis_json)
    
    # Handle both nested and un-nested JSON structures dynamically
    data_to_clean = report_data.get("full_analysis_json", report_data)
    
    # Clean subjective_analysis
    if "subjective_analysis" in data_to_clean:
        subj = data_to_clean["subjective_analysis"]
        keys_to_remove = [
            "question_wise_sentiment",
            "overall_sentiment",
            "company_feedback",
            "leaving_reason",
            "exit_analysis"
        ]
        for key in keys_to_remove:
            subj.pop(key, None)

    # >>> ADDED: Clean objective_analysis <<<
    if "objective_analysis" in data_to_clean:
        obj = data_to_clean["objective_analysis"]
        obj.pop("positive_count", None)
        obj.pop("negative_count", None)

    return GetReportOutput(
        full_analysis_json=report_data
    )