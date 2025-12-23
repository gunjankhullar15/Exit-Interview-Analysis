from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
from collections import Counter
from src.database.database import get_db
from src.database.models import Employee, AnalysisReport

router = APIRouter()


@router.get("/graphical_report_data/")
async def get_graphical_report_data(
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
            emp_resignation_dt = datetime.strptime(emp.date_of_resignation, "%d %b %Y")
        except ValueError:
            continue

        if start_dt <= emp_resignation_dt <= end_dt:
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

    person_wise_leaving_reasons = []

    person_counter = 1

    for item in response_data:
        reason_dict = item.get("leaving_reason", {})

        for reason, value in reason_dict.items():
            if value == 1:
                person_wise_leaving_reasons.append({
                    f"person_{person_counter}": reason
                })
                person_counter += 1
                break  # only one reason per person

    total_people = len(person_wise_leaving_reasons)

    # Extract only the reason values
    reasons = []
    for item in person_wise_leaving_reasons:
        reason = list(item.values())[0]  # get the reason string
        reasons.append(reason)

    # Count occurrences
    reason_counts = Counter(reasons)

    # Calculate percentages
    overall_percentage = {}

    for reason, count in reason_counts.items():
        percentage = round((count / total_people) * 100, 2)
        overall_percentage[reason] = f"{percentage}%"

    # Step 1: Master list of all possible leaving reasons
    ALL_REASONS = [
        "career change",
        "personal reasons",
        "better work-life balance",
        "role redundancy",
        "dissatisfaction with management",
        "seeking higher salary",
        "lack of growth opportunities",
        "toxic work environment"
    ]

    # Step 3: Initialize all reasons with 0%
    final_percentages = {
        reason: "0%"
        for reason in ALL_REASONS
    }

    # Step 4: Update with actual values
    final_percentages.update(overall_percentage)


    return {
        "start_date": start_date,
        "end_date": end_date,
        "overall_percentage": final_percentages,
        "leaving_reasons_list": person_wise_leaving_reasons,
        "count": len(response_data),
        "data": response_data
    }
