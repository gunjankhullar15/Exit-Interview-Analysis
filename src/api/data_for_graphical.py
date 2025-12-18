from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime

from src.database.database import get_db
from src.database.models import Employee, AnalysisReport

router = APIRouter()


@router.get("/analysis-reports-by-joining-date/")
async def get_analysis_reports_by_joining_date(
    start_date: str = Query(..., example="07 Sep 2015"),
    end_date: str = Query(..., example="26 Oct 2020"),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns employee details + ONLY leaving_reason from analysis_report
    """

    # -------------------------------
    # Step 1: Parse dates
    # -------------------------------
    try:
        start_dt = datetime.strptime(start_date, "%d %b %Y")
        end_dt = datetime.strptime(end_date, "%d %b %Y")
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Use DD Mon YYYY (e.g. 07 Sep 2015)"
        )

    # -------------------------------
    # Step 2: Fetch employees
    # -------------------------------
    result = await db.execute(select(Employee))
    employees = result.scalars().all()

    filtered_employees = []

    for emp in employees:
        if not emp.joining_date:
            continue

        try:
            emp_joining_dt = datetime.strptime(emp.joining_date, "%d %b %Y")
        except ValueError:
            continue

        if start_dt <= emp_joining_dt <= end_dt:
            filtered_employees.append(emp)

    if not filtered_employees:
        return {
            "count": 0,
            "data": []
        }

    # -------------------------------
    # Step 3: Fetch Analysis Reports
    # -------------------------------
    employee_ids = [emp.id for emp in filtered_employees]

    result2 = await db.execute(
        select(AnalysisReport).where(
            AnalysisReport.employee_id.in_(employee_ids)
        )
    )
    analysis_reports = result2.scalars().all()

    analysis_map = {ar.employee_id: ar for ar in analysis_reports}

    # -------------------------------
    # Step 4: Build response
    # -------------------------------
    response_data = []

    for emp in filtered_employees:
        report = analysis_map.get(emp.id)

        all_data = report.full_analysis_json

        leaving_reason = None
        
        leaving_reason = all_data["subjective_analysis"]["leaving_reason"]

        response_data.append({
            "empid": emp.id,
            "empcode": emp.employee_code,
            "empname": emp.name,
            "joining_date": emp.joining_date,
            "l1_manager": emp.l1_manager,
            "l2_manager": emp.l2_manager,
            "hrbp_name": emp.hrbp_name,
            "resignation_date": emp.date_of_resignation,
            "overall_sentiment": emp.overall_sentiment,
            "department": emp.department,
            "designation": emp.designation,
            "leaving_reason": leaving_reason
        })

    return {
        "start_date": start_date,
        "end_date": end_date,
        "count": len(response_data),
        "data": response_data
    }
