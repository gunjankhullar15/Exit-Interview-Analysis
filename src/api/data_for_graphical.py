# # from fastapi import APIRouter, Depends, HTTPException, Query
# # from sqlalchemy.ext.asyncio import AsyncSession
# # from sqlalchemy.future import select
# # from datetime import datetime
# # from collections import Counter
# # from src.database.database import get_db
# # from src.database.models import Employee, AnalysisReport

# # router = APIRouter()


# # @router.get("/graphical_report_data/")
# # async def get_graphical_report_data(
# #     start_date: str = Query(..., example="07 Sep 2015"),
# #     end_date: str = Query(..., example="26 Oct 2020"),
# #     db: AsyncSession = Depends(get_db),
# # ):
# #     """
# #     Returns employee details + ONLY leaving_reason from analysis_report
# #     """

# #     # -------------------------------
# #     # Step 1: Parse dates
# #     # -------------------------------
# #     try:
# #         start_dt = datetime.strptime(start_date, "%d %b %Y")
# #         end_dt = datetime.strptime(end_date, "%d %b %Y")
# #     except ValueError:
# #         raise HTTPException(
# #             status_code=400,
# #             detail="Invalid date format. Use DD Mon YYYY (e.g. 07 Sep 2015)"
# #         )

# #     # -------------------------------
# #     # Step 2: Fetch employees
# #     # -------------------------------
# #     result = await db.execute(select(Employee))
# #     employees = result.scalars().all()

# #     filtered_employees = []

# #     for emp in employees:
# #         if not emp.joining_date:
# #             continue

# #         try:
# #             # yha pai exit_date ki jhage data_of_resignation change hogi
# #             emp_resignation_dt = datetime.strptime(emp.exit_date, "%d %b %Y")
# #         except ValueError:
# #             continue

# #         if start_dt <= emp_resignation_dt <= end_dt:
# #             filtered_employees.append(emp)

# #     if not filtered_employees:
# #         return {
# #             "count": 0,
# #             "data": []
# #         }

# #     # -------------------------------
# #     # Step 3: Fetch Analysis Reports
# #     # -------------------------------
# #     employee_ids = [emp.id for emp in filtered_employees]

# #     result2 = await db.execute(
# #         select(AnalysisReport).where(
# #             AnalysisReport.employee_id.in_(employee_ids)
# #         )
# #     )
# #     analysis_reports = result2.scalars().all()

# #     analysis_map = {ar.employee_id: ar for ar in analysis_reports}

# #     # -------------------------------
# #     # Step 4: Build response
# #     # -------------------------------
# #     response_data = []

# #     for emp in filtered_employees:
# #         report = analysis_map.get(emp.id)

# #         all_data = report.full_analysis_json

# #         leaving_reason = None
        
# #         leaving_reason = all_data["subjective_analysis"]["leaving_reason"]

# #         response_data.append({
# #             "empid": emp.id,
# #             "empcode": emp.employee_code,
# #             "empname": emp.name,
# #             "joining_date": emp.joining_date,
# #             "l1_manager": emp.l1_manager,
# #             "l2_manager": emp.l2_manager,
# #             "hrbp_name": emp.hrbp_name,
# #             "resignation_date": emp.date_of_resignation,
# #             "overall_sentiment": emp.overall_sentiment,
# #             "department": emp.department,
# #             "designation": emp.designation,
# #             "leaving_reason": leaving_reason
# #         })

# #     person_wise_leaving_reasons = []

# #     person_counter = 1

# #     for item in response_data:
# #         reason_dict = item.get("leaving_reason", {})

# #         for reason, value in reason_dict.items():
# #             if value == 1:
# #                 person_wise_leaving_reasons.append({
# #                     f"person_{person_counter}": reason
# #                 })
# #                 person_counter += 1
# #                 break  # only one reason per person

# #     total_people = len(person_wise_leaving_reasons)

# #     # Extract only the reason values
# #     reasons = []
# #     for item in person_wise_leaving_reasons:
# #         reason = list(item.values())[0]  # get the reason string
# #         reasons.append(reason)

# #     # Count occurrences
# #     reason_counts = Counter(reasons)

# #     # Calculate percentages
# #     overall_percentage = {}

# #     for reason, count in reason_counts.items():
# #         percentage = round((count / total_people) * 100, 2)
# #         overall_percentage[reason] = f"{percentage}%"

# #     # Step 1: Master list of all possible leaving reasons
# #     ALL_REASONS = [
# #         "career change",
# #         "personal reasons",
# #         "better work-life balance",
# #         "role redundancy",
# #         "dissatisfaction with management",
# #         "seeking higher salary",
# #         "lack of growth opportunities",
# #         "toxic work environment"
# #     ]

# #     # Step 3: Initialize all reasons with 0%
# #     final_percentages = {
# #         reason: "0%"
# #         for reason in ALL_REASONS
# #     }

# #     # Step 4: Update with actual values
# #     final_percentages.update(overall_percentage)


# #     return {
# #         "start_date": start_date,
# #         "end_date": end_date,
# #         "overall_percentage": final_percentages,
# #         "leaving_reasons_list": person_wise_leaving_reasons,
# #         "count": len(response_data),
# #         "data": response_data
# #     }

# from fastapi import APIRouter, Depends, HTTPException, Query
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.future import select
# from datetime import datetime
# from collections import Counter
# from typing import Optional
# from src.database.database import get_db
# from src.database.models import Employee, AnalysisReport, SurveyResponse

# router = APIRouter()

# @router.get("/graphical_report_data/")
# async def get_graphical_report_data(
#     start_date: str = Query(..., example="07 Sep 2015"),
#     end_date: str = Query(..., example="26 Oct 2020"),
#     department: Optional[str] = Query(None, description="Filter by specific department"),
#     db: AsyncSession = Depends(get_db),
# ):
#     """
#     Returns employee details + ONLY leaving_reason from analysis_report
#     """

#     # -------------------------------
#     # Step 1: Parse dates
#     # -------------------------------
#     try:
#         start_dt = datetime.strptime(start_date, "%d %b %Y")
#         end_dt = datetime.strptime(end_date, "%d %b %Y")
#     except ValueError:
#         raise HTTPException(
#             status_code=400,
#             detail="Invalid date format. Use DD Mon YYYY (e.g. 07 Sep 2015)"
#         )

#     # -------------------------------
#     # Step 2: Fetch employees
#     # -------------------------------
#     result = await db.execute(select(Employee))
#     employees = result.scalars().all()

#     filtered_employees = []
    
#     # Track exits by department
#     department_counts_list = []

#     for emp in employees:
#         if not emp.joining_date:
#             continue

#         try:
#             # yha pai exit_date ki jhage data_of_resignation change hogi
#             emp_resignation_dt = datetime.strptime(emp.exit_date, "%d %b %Y")
#         except ValueError:
#             continue

#         if start_dt <= emp_resignation_dt <= end_dt:
#             # Apply Department Filter Logic
#             if department and department.lower() != "all":
#                 if not emp.department or emp.department.lower() != department.lower():
#                     continue
            
#             filtered_employees.append(emp)
#             if emp.department:
#                 department_counts_list.append(emp.department)

#     if not filtered_employees:
#         return {
#             "count": 0,
#             "data": []
#         }
        
#     # Calculate Exits by Department
#     exits_by_department = dict(Counter(department_counts_list))

#     # -------------------------------
#     # Step 3: Fetch Analysis & Survey Reports
#     # -------------------------------
#     employee_ids = [emp.id for emp in filtered_employees]

#     result2 = await db.execute(
#         select(AnalysisReport).where(
#             AnalysisReport.employee_id.in_(employee_ids)
#         )
#     )
#     analysis_reports = result2.scalars().all()
#     analysis_map = {ar.employee_id: ar for ar in analysis_reports}

#     # Fetch Survey Responses to safely extract Question 16
#     result3 = await db.execute(
#         select(SurveyResponse).where(
#             SurveyResponse.employee_id.in_(employee_ids)
#         )
#     )
#     survey_reports = result3.scalars().all()
#     survey_map = {sr.employee_id: sr for sr in survey_reports}

#     # Master list of all possible leaving reasons
#     ALL_REASONS = [
#         "career change",
#         "personal reasons",
#         "better work-life balance",
#         "role redundancy",
#         "dissatisfaction with management",
#         "seeking higher salary",
#         "lack of growth opportunities",
#         "toxic work environment"
#     ]
    
#     # Initialize Q16 feedback dictionary
#     q16_feedback_by_reason = {reason: [] for reason in ALL_REASONS}

#     # -------------------------------
#     # Step 4: Build response
#     # -------------------------------
#     response_data = []

#     for emp in filtered_employees:
#         report = analysis_map.get(emp.id)
#         if not report: 
#             continue

#         all_data = report.full_analysis_json
        
#         leaving_reason = None
#         if all_data and "subjective_analysis" in all_data:
#             leaving_reason = all_data["subjective_analysis"].get("leaving_reason", {})

#         response_data.append({
#             "empid": emp.id,
#             "empcode": emp.employee_code,
#             "empname": emp.name,
#             "joining_date": emp.joining_date,
#             "l1_manager": emp.l1_manager,
#             "l2_manager": emp.l2_manager,
#             "hrbp_name": emp.hrbp_name,
#             "resignation_date": emp.date_of_resignation,
#             "overall_sentiment": emp.overall_sentiment,
#             "department": emp.department,
#             "designation": emp.designation,
#             "leaving_reason": leaving_reason
#         })

#         # Extract Q16 and map it to this person's primary leaving reason
#         survey = survey_map.get(emp.id)
#         if leaving_reason and survey and survey.raw_answers:
#             primary_reason = None
#             for r_key, val in leaving_reason.items():
#                 if val == 1:
#                     primary_reason = r_key
#                     break
            
#             if primary_reason and primary_reason in q16_feedback_by_reason:
#                 for q_key, q_val in survey.raw_answers.items():
#                     if str(q_key).lower().startswith("question 16"):
#                         # Ensure we don't append empty/nan answers
#                         if q_val and str(q_val).lower() not in ["nan", "none", "n/a", "nothing"]:
#                             q16_feedback_by_reason[primary_reason].append(str(q_val).strip())
#                         break

#     person_wise_leaving_reasons = []
#     person_counter = 1

#     for item in response_data:
#         reason_dict = item.get("leaving_reason") or {}

#         for reason, value in reason_dict.items():
#             if value == 1:
#                 person_wise_leaving_reasons.append({
#                     f"person_{person_counter}": reason
#                 })
#                 person_counter += 1
#                 break  # only one reason per person

#     total_people = len(person_wise_leaving_reasons)

#     # Extract only the reason values
#     reasons = []
#     for item in person_wise_leaving_reasons:
#         reason = list(item.values())[0]  # get the reason string
#         reasons.append(reason)

#     # Count occurrences
#     reason_counts = Counter(reasons)

#     # Calculate percentages safely (Prevents ZeroDivisionError)
#     overall_percentage = {}
#     if total_people > 0:
#         for reason, count in reason_counts.items():
#             percentage = round((count / total_people) * 100, 2)
#             overall_percentage[reason] = f"{percentage}%"

#     # Initialize all reasons with 0%
#     final_percentages = {
#         reason: "0%"
#         for reason in ALL_REASONS
#     }

#     # Update with actual values
#     final_percentages.update(overall_percentage)

#     # Filter out Q16 feedback for categories that have 0%
#     filtered_q16_feedback = {
#         reason: feedback 
#         for reason, feedback in q16_feedback_by_reason.items() 
#         if reason_counts.get(reason, 0) > 0
#     }

#     return {
#         "start_date": start_date,
#         "end_date": end_date,
#         "summary": {
#             "total_exits": total_people
#         },
#         "exits_by_department": exits_by_department,
#         "reason_counts": dict(reason_counts),
#         "overall_percentage": final_percentages,
#         "q16_feedback_by_reason": filtered_q16_feedback,
#         "leaving_reasons_list": person_wise_leaving_reasons,
#         "count": len(response_data),
#         "data": response_data
#     }

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
from collections import Counter
from typing import Optional
from src.database.database import get_db
from src.database.models import Employee, AnalysisReport, SurveyResponse

router = APIRouter()

@router.get("/graphical_report_data/")
async def get_graphical_report_data(
    start_date: str = Query(..., example="07 Sep 2015"),
    end_date: str = Query(..., example="26 Oct 2020"),
    department: Optional[str] = Query(None, description="Filter by specific department"),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns aggregated dashboard data matching specific filters.
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
    # Step 2: Fetch and Filter Employees
    # -------------------------------
    result = await db.execute(select(Employee))
    employees = result.scalars().all()

    filtered_employees = []

    for emp in employees:
        if not emp.joining_date:
            continue

        try:
            emp_resignation_dt = datetime.strptime(emp.exit_date, "%d %b %Y")
        except ValueError:
            continue

        if start_dt <= emp_resignation_dt <= end_dt:
            if department and department.lower() != "all":
                if not emp.department or emp.department.lower() != department.lower():
                    continue
            
            filtered_employees.append(emp)

    # Define the core reasons list for UI mapping
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

    if not filtered_employees:
        return {
            "start_date": start_date,
            "end_date": end_date,
            "summary": {"total_exits": 0},
            "exits_by_department": {},
            "reason_counts": {},
            "overall_percentage": {},
            "feedback_by_reason": {}
        }
        
    # -------------------------------
    # Step 3: Fetch Analysis & Survey Reports
    # -------------------------------
    employee_ids = [emp.id for emp in filtered_employees]

    result2 = await db.execute(
        select(AnalysisReport).where(AnalysisReport.employee_id.in_(employee_ids))
    )
    analysis_map = {ar.employee_id: ar for ar in result2.scalars().all()}

    # result3 = await db.execute(
    #     select(SurveyResponse).where(SurveyResponse.employee_id.in_(employee_ids))
    # )
    # survey_map = {sr.employee_id: sr for sr in result3.scalars().all()}

    # -------------------------------
    # Step 4: Process Counts and Feedbacks
    # -------------------------------
    total_people = 0
    department_counts = Counter()
    reason_counts = Counter()
    
    # Pre-fill with empty arrays so the UI always has keys to map over
    feedback_by_reason = {reason: [] for reason in ALL_REASONS}

    # Blacklist of meaningless answers we want to drop
    junk_words = {
        "nan", "none", "nothing", "na", "n/a", "n.a.", "null", 
        "no", "nil", "-", ".", "not sure", "not applicable", 
        "n a", "no comment", "no comments"
    }

    for emp in filtered_employees:
        report = analysis_map.get(emp.id)
        if not report: 
            continue

        all_data = report.full_analysis_json
        
        leaving_reason = None
        if all_data and "subjective_analysis" in all_data:
            leaving_reason = all_data["subjective_analysis"].get("leaving_reason", {})

        primary_reason = None
        if leaving_reason:
            for r_key, val in leaving_reason.items():
                if val == 1:
                    primary_reason = r_key
                    break
        
        # Route hallucinations safely
        if primary_reason == "health reasons":
            primary_reason = "personal reasons"
            
        if primary_reason and primary_reason in ALL_REASONS:
            total_people += 1
            reason_counts[primary_reason] += 1
            
            if emp.department:
                department_counts[emp.department] += 1
            
            exit_analysis = all_data.get("subjective_analysis", {}).get("exit_analysis", {})
            golden_quote = exit_analysis.get("supporting_quote", "")
            
            # If the LLM successfully extracted a quote, apply the UI cleanliness filters
            if golden_quote:
                golden_quote = golden_quote.strip()
                
                # Check against junk words and ensure it's a real sentence (> 4 characters)
                if golden_quote.lower() not in junk_words and len(golden_quote) > 4:
                    
                    # Deduplicate: Only add if it's not already in the array
                    if golden_quote not in feedback_by_reason[primary_reason]:
                        feedback_by_reason[primary_reason].append(golden_quote)
 
     # -------------------------------
    # Step 5: Format Final Return Data
    # -------------------------------
    
    final_reason_counts = {}
    final_percentages = {}
    
    for reason in ALL_REASONS:
        count = reason_counts.get(reason, 0)
        # Only add to the dictionary if the count is greater than 0
        if count > 0:
            final_reason_counts[reason] = count
            
            # Calculate final percentages safely
            if total_people > 0:
                percentage = round((count / total_people) * 100, 2)
                final_percentages[reason] = f"{percentage}%"

    # Filter out empty arrays in feedback
    filtered_feedback_by_reason = {
        reason: feedback 
        for reason, feedback in feedback_by_reason.items() 
        if len(feedback) > 0
    }

    return {
        "start_date": start_date,
        "end_date": end_date,
        "summary": {
            "total_exits": total_people
        },
        "exits_by_department": dict(department_counts),
        "reason_counts": final_reason_counts,
        "overall_percentage": final_percentages,
        "feedback_by_reason": filtered_feedback_by_reason
    }