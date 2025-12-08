from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List

from src.database.database import get_db
from src.database.models import Employee
from src.database.schemas import ReportsOutput, GetReportOutput

router = APIRouter()

@router.get("/reports", response_model=List[ReportsOutput])
async def get_all_reports(db: AsyncSession = Depends(get_db)):
    
    stmt = select(Employee)
    result = await db.execute(stmt)
    employees = result.scalars().all()
    
    # Pydantic (from_attributes=True) will handle the mapping automatically
    return employees

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

    return GetReportOutput(
        full_analysis_json=emp.analysis_report.full_analysis_json
    )