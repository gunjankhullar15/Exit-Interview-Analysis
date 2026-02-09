from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.database.database import get_db
from src.database.models import Employee, AnalysisReport
import csv
from io import StringIO
import json

router = APIRouter()


@router.get("/download-employee-details-csv/")
async def download_employee_details_csv(
    employee_codes: List[str] = Query(..., description="List of employee codes"),
    db: AsyncSession = Depends(get_db)
):
    """
    Async GET API: Fetch employees and their AnalysisReport, return as CSV
    with negative_sentiments, positive_sentiments, neutral_sentiments, overall_summary.
    """

    # Step 1: Fetch employees
    result = await db.execute(select(Employee).where(Employee.employee_code.in_(employee_codes)))
    employees = result.scalars().all()

    if not employees:
        raise HTTPException(status_code=404, detail="No employees found")

    # Step 2: Fetch AnalysisReport for those employee IDs
    employee_ids = [emp.id for emp in employees]
    result2 = await db.execute(select(AnalysisReport).where(AnalysisReport.employee_id.in_(employee_ids)))
    analysis_reports = result2.scalars().all()

    # Map employee_id -> AnalysisReport
    analysis_map = {ar.employee_id: ar for ar in analysis_reports}

    # Step 3: Create CSV in memory
    output = StringIO()
    writer = csv.writer(output)

    # CSV headers
    headers = [
        "Employee Code", "Name", "Department", "Designation",
        "L1 Manager", "L1 Manager Code", "L2 Manager", "L2 Manager Code",
        "HRBP Name", "HRBP Code", "Location", "Joining Date",
        "Exit Date", "Date of Resignation", "Survey Initiated",
        "Survey Submission", "Overall Sentiment",
        "Negative Sentiments", "Positive Sentiments", "Neutral Sentiments", "Overall Summary"
    ]
    writer.writerow(headers)

    # CSV rows
    for emp in employees:
        analysis_json_obj = analysis_map.get(emp.id)

        all_data = analysis_json_obj.full_analysis_json

        # default empty values
        negative = positive = neutral = summary = None

        negative = all_data["subjective_analysis"]["sentiment_definitions"]["negative_sentiments"]
        positive = all_data["subjective_analysis"]["sentiment_definitions"]["positive_sentiments"]
        neutral = all_data["subjective_analysis"]["sentiment_definitions"]["neutral_sentiments"]
        summary = all_data["subjective_analysis"]["overall_summary"]

        negative = str(negative)
        positive = str(positive)
        neutral = str(neutral)

        negative = negative[1:-1]
        positive = positive[1:-1]
        neutral = neutral[1:-1]

        writer.writerow([
            emp.employee_code,
            emp.name,
            emp.department,
            emp.designation,
            emp.l1_manager,
            emp.l1_manager_code,
            emp.l2_manager,
            emp.l2_manager_code,
            emp.hrbp_name,
            emp.hrbp_code,
            emp.location,
            emp.joining_date,
            emp.exit_date,
            emp.date_of_resignation,
            emp.survey_initiated_date,
            emp.survey_submission_date,
            emp.overall_sentiment,
            negative,
            positive,
            neutral,
            summary
        ])

    output.seek(0)

    # Return CSV as streaming response
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=employee_details.csv"}
    )

    # return "neivdujei"  