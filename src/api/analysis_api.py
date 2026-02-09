# from fastapi import APIRouter
# from src.llm.llm_services import getting_analysis_from_llm

# router = APIRouter()

# @router.post("/Generate_llm_response/")
# async def Generate_llm_response():

#     data = """
# {'Question 1 -> How was your overall experience working with Netsmartz Group?\\nSelect one: 1 ☐ 2 ☐ 3 ☐ 4 ☐ 5 ☐\\n': np.float64(4.0), 'Question 2 -> What are the major reasons for your resignation?\\n(Provide details here)\\n': 'Role redundancy. Project no longer aligned for team', 'Question 3 -> Do you feel there is joy in working with Netsmartz Group?\\nYes ☐ No ☐\\n': 'Yes', 'Question 4 -> In your opinion, were you provided the essential tools and resources required to excel in your position?\\nYes ☐ No ☐\\n': 'Yes', 'Question 5 -> Do you feel there is any form of politics, backbiting, or power struggle in the organization?\\nYes ☐ No ☐\\n': 'No', 'Question 6 -> Did you get along well with your team members?\\nYes ☐ No ☐\\n': 'Yes', 'Question 7 -> Did you get along well with your reporting manager?\\nYes ☐ No ☐\\n': 'Yes', 'Question 8 -> Were you satisfied with your benefits, perks, and other incentives?\\nYes ☐ No ☐\\n': 'Yes', 'Question 9 -> Do you believe your work was adequately recognized and appreciated?\\nYes ☐ No ☐\\n': 'Yes', 'Question 10 -> Is there a culture of teamwork and cooperation within the organization?\\nYes ☐ No ☐\\n': 'Yes', 'Question 11 -> Have you ever experienced any discrimination or harassment while working in this organization?\\nYes ☐ No ☐\\n': 'No', 'Question 12 -> Do you think the company policies were adequate? If not, do you want to suggest changes to the company policy?\\n(Provide suggestions if any)\\n': 'All okay', 'Question 13 -> Any suggestions for improvements in your team or department?\\n(Provide suggestions here)\\n': nan, 'Question 14 -> Do you feel you were given sufficient training to perform well in your role? If not, how could it have been better?\\nYes ☐ No ☐\\n(Suggestions)\\n': 'Yes', 'Question 15 -> What did you enjoy the most about your job?\\n(Provide details here)\\n': 'The team camaraderie', 'Question 16 -> What did you dislike the most about your job?\\n(Provide details here)\\n': 'Nothing', 'Question 17 -> Do you have any concerns about the organization at large that you would like to share?\\n(Provide details here)\\n': 'no', 'Question 18 -> Is there any problem issue, in particular, you would like to mention?\\n(Provide details here)\\n': 'no', 'Question 19 -> Will you recommend Netsmartz to your friends and family for potential employment opportunities?\\nYes ☐ No ☐\\n': 'Yes', 'Question 20 -> Would you like to work with Netsmartz in the future?\\nYes ☐ No ☐\\n\\n\\n\\nFinancial Clearance:\\n': 'Yes', 'Question 21 -> Whether you have any pending loan amount to be paid. If yes, mention the amount:\\nYes ☐ No ☐ (Amount)\\n': nan, 'Question 22 -> Whether you have a pending Imprest account to be paid. If yes, mention the amount:\\nYes ☐ No ☐ (Amount)\\n': 'No', \"Question 23 -> Whether you have downloaded your past years' Form 16:\\nYes ☐ No ☐\\n\": 'Yes', 'Question 24 -> If applicable, whether you have submitted your Tax Saving proofs, if applicable in Peoplestrong.\\nYes ☐ No ☐\\n': 'No', 'Question 25 -> If applicable, whether you have submitted your Tax-Free Reimbursement components proofs as hard copies.\\nYes ☐ No ☐': 'No'}

# """
#     json_response = getting_analysis_from_llm(data)

#     return json_response


# from fastapi import APIRouter, Depends
# from fastapi.concurrency import run_in_threadpool
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.future import select
# from sqlalchemy.orm import selectinload
# import asyncio
# import json
# from src.database.database import get_db
# from src.database.models import AnalysisReport, SurveyResponse, Employee
# from src.llm.llm_services import getting_analysis_from_llm

# router = APIRouter()


# MAX_CONCURRENT_LLM_CALLS = 3
# llm_semaphore = asyncio.Semaphore(MAX_CONCURRENT_LLM_CALLS)

# @router.post("/Generate_llm_response/")
# async def Generate_llm_response(db: AsyncSession = Depends(get_db)):
     
#     stmt = select(SurveyResponse).options(
#         selectinload(SurveyResponse.employee)
#     ).filter(SurveyResponse.status == "PENDING")
    
#     result = await db.execute(stmt)
#     pending_surveys = result.scalars().all()
    
#     if not pending_surveys:
#         return {"status": "success", "message": "No pending reports to process."}

#     async def process_single_llm_call(survey_obj):
#         async with llm_semaphore:
#             if not survey_obj.raw_answers:
#                 return survey_obj, None
            
#             # Convert raw dict to string for LLM
#             data_str = json.dumps(survey_obj.raw_answers, indent=2)
            
            
#             try:
#                 llm_result = await run_in_threadpool(getting_analysis_from_llm, data_str)
#                 return survey_obj, llm_result
#             except Exception as e:
#                 print(f"LLM Error for Emp ID {survey_obj.employee_id}: {e}")
#                 return survey_obj, None

    
#     tasks = [process_single_llm_call(survey) for survey in pending_surveys]
    
#     processed_count = 0
#     failed_count = 0

    
#     for completed_task in asyncio.as_completed(tasks):
#         survey, analysis_json = await completed_task
        
#         if analysis_json:
#             try:
                
#                 emp = survey.employee

#                 sentiment_val = "N/A"
#                 try:
                    
#                     obj_data = analysis_json.get("objective_analysis", {})
#                     obj_pos = float(obj_data.get("positive_percentage", 0))
#                     obj_neg = float(obj_data.get("negative_percentage", 0))
                    
#                     obj_neu = max(0, 100 - (obj_pos + obj_neg))

                   
#                     subj_data = analysis_json.get("subjective_analysis", {})
#                     subj_overall = subj_data.get("overall_sentiment", {})
                    
#                     subj_pos = 0.0
#                     subj_neg = 0.0
#                     subj_neu = 0.0
                    
#                     if isinstance(subj_overall, dict):
#                         subj_pos = float(subj_overall.get("positive_percentage", 0))
#                         subj_neg = float(subj_overall.get("negative_percentage", 0))
#                         subj_neu = float(subj_overall.get("neutral_percentage", 0))

                    
#                     final_pos = (obj_pos + subj_pos) / 2
#                     final_neg = (obj_neg + subj_neg) / 2
#                     final_neu = (obj_neu + subj_neu) / 2
                    
                    
#                     if final_pos >= final_neg and final_pos >= final_neu:
#                         sentiment_val = "Positive"
#                     elif final_neg >= final_pos and final_neg >= final_neu:
#                         sentiment_val = "Negative"
#                     else:
#                         sentiment_val = "Neutral"

#                 except Exception as calc_err:
#                     print(f"Sentiment Calc Error: {calc_err}")
#                     sentiment_val = "Analyzed" 
                
#                 emp.overall_sentiment = sentiment_val
                
#                 metadata_json = {
#                     "employee_code": emp.employee_code,
#                     "name": emp.name,
#                     "l1_manager": emp.l1_manager or "N/A",
#                     "l2_manager": emp.l2_manager or "N/A",
#                     "hrbp_name": emp.hrbp_name or "N/A",
#                     "location": emp.location or "N/A",
#                     "joining_date": emp.joining_date or "N/A",
#                     "exit_date": emp.exit_date or "N/A"
#                 }

                
#                 full_combined_json = {**metadata_json, **analysis_json}

                
#                 new_report = AnalysisReport(
#                     employee_id=survey.employee_id,
#                     full_analysis_json=full_combined_json
                    
#                 )
#                 db.add(new_report)

                
#                 survey.status = "COMPLETED"
                
                
#                 await db.commit()
#                 processed_count += 1
                
#             except Exception as db_err:
#                 print(f"Database Save Error for Emp ID {survey.employee_id}: {db_err}")
#                 await db.rollback()
#                 failed_count += 1
#         else:
#             # Handle LLM Failure
#             survey.status = "FAILED"
#             await db.commit()
#             failed_count += 1

#     return {
#         "status": "success", 
#         "message": f"Report generated successfully for {processed_count} rows.",
#         "failed": failed_count
#     }


from fastapi import APIRouter, Depends
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import or_, extract, delete, cast, Date
import asyncio
import json
from src.database.database import get_db
from src.database.models import AnalysisReport, SurveyResponse, Employee, MonthlyReasonStats
from src.llm.llm_services import getting_analysis_from_llm
from datetime import datetime

router = APIRouter()

MAX_CONCURRENT_LLM_CALLS = 3
llm_semaphore = asyncio.Semaphore(MAX_CONCURRENT_LLM_CALLS)

def parse_date_robustly(date_val):
    """Helper to handle various date formats like '11 Jul 2025' or '2025-07-11'"""
    if not date_val:
        return None
    if not isinstance(date_val, str):
        return date_val # Already a date object
    
    # Try different formats commonly found in Excel and Postgres
    for fmt in ("%d %b %Y", "%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(date_val, fmt).date()
        except ValueError:
            continue
    return None

async def update_monthly_stats_table(db: AsyncSession, month: int, year: int):
    """Recalculates the aggregated stats for the specific month/year."""
    stmt = select(AnalysisReport).join(Employee).filter(
        extract('month', cast(Employee.exit_date, Date)) == month,
        extract('year', cast(Employee.exit_date, Date)) == year
    )
    result = await db.execute(stmt)
    reports = result.scalars().all()
    
    total = len(reports)
    if total == 0: return

    reason_counts = {}
    for r in reports:
        cat = r.exit_category or "Other"
        reason_counts[cat] = reason_counts.get(cat, 0) + 1

    # Clear old data and insert fresh calculations
    await db.execute(delete(MonthlyReasonStats).where(
        MonthlyReasonStats.month == month, 
        MonthlyReasonStats.year == year
    ))

    for reason, count in reason_counts.items():
        db.add(MonthlyReasonStats(
            month=month, year=year, reason_name=reason,
            percentage=round((count / total) * 100, 2),
            total_count=count, total_month_exits=total
        ))
    await db.commit()

@router.post("/Generate_llm_response/")
async def Generate_llm_response(db: AsyncSession = Depends(get_db)):
    
    # 1. Fetch all pending surveys and their employees upfront
    # selectinload prevents "MissingGreenlet" errors by fetching related data immediately
    stmt = select(SurveyResponse).options(
        selectinload(SurveyResponse.employee)
    ).filter(or_(SurveyResponse.status == "PENDING", SurveyResponse.status == "FAILED"))
    
    result = await db.execute(stmt)
    pending_surveys = result.scalars().unique().all()
    
    if not pending_surveys:
        return {"status": "success", "message": "No pending reports to process."}

    # 2. Extract Data to local variables to disconnect from DB session during LLM processing
    # This is the best defense against Greenlet/Concurrency errors
    processing_batch = []
    for s in pending_surveys:
        processing_batch.append({
            "survey_id": s.id,
            "raw_answers": s.raw_answers,
            "employee_id": s.employee_id,
            "exit_date": s.employee.exit_date
        })

    affected_periods = set()
    processed_count = 0
    failed_count = 0

    async def llm_task(item):
        async with llm_semaphore:
            if not item["raw_answers"]:
                return item["survey_id"], None
            
            data_str = json.dumps(item["raw_answers"], indent=2)
            try:
                # Spacing out requests slightly to avoid TPM Rate Limits
                await asyncio.sleep(1.5) 
                llm_result = await run_in_threadpool(getting_analysis_from_llm, data_str)
                return item["survey_id"], llm_result
            except Exception as e:
                print(f"LLM Processing Error for Survey {item['survey_id']}: {e}")
                return item["survey_id"], None

    # 3. Execute LLM calls concurrently
    results = await asyncio.gather(*(llm_task(item) for item in processing_batch))
    
    # 4. Save results in a single transaction loop
    survey_lookup = {s.id: s for s in pending_surveys}

    for s_id, analysis_json in results:
        survey = survey_lookup.get(s_id)
        if not survey: continue

        if analysis_json:
            try:
                emp = survey.employee
                exit_dt = parse_date_robustly(emp.exit_date)

                # Extraction logic for Analytics
                subj_data = analysis_json.get("subjective_analysis", {})
                exit_info = subj_data.get("exit_analysis", {})
                category_name = exit_info.get("primary_reason_category", "Other")
                is_controllable = exit_info.get("is_controllable", True)

                if exit_dt:
                    affected_periods.add((exit_dt.month, exit_dt.year))

                # Sentiment Calculation (Your Logic)
                sentiment_val = "N/A"
                obj_data = analysis_json.get("objective_analysis", {})
                obj_pos = float(obj_data.get("positive_percentage", 0))
                obj_neg = float(obj_data.get("negative_percentage", 0))
                
                subj_overall = subj_data.get("overall_sentiment", {})
                subj_pos = float(subj_overall.get("positive_percentage", 0)) if isinstance(subj_overall, dict) else 0.0
                subj_neg = float(subj_overall.get("negative_percentage", 0)) if isinstance(subj_overall, dict) else 0.0

                final_pos = (obj_pos + subj_pos) / 2
                final_neg = (obj_neg + subj_neg) / 2
                
                if final_pos > final_neg: sentiment_val = "Positive"
                elif final_neg > final_pos: sentiment_val = "Negative"
                else: sentiment_val = "Neutral"

                emp.overall_sentiment = sentiment_val
                
                # Combine metadata for the full report
                full_combined_json = {
                    "employee_code": emp.employee_code,
                    "name": emp.name,
                    "exit_date": str(exit_dt) if exit_dt else "N/A",
                    **analysis_json
                }

                new_report = AnalysisReport(
                    employee_id=survey.employee_id,
                    full_analysis_json=full_combined_json,
                    exit_category=category_name,
                    is_controllable=is_controllable
                )
                db.add(new_report)
                survey.status = "COMPLETED"
                processed_count += 1
                
            except Exception as e:
                print(f"Data save error: {e}")
                survey.status = "FAILED"
                failed_count += 1
        else:
            survey.status = "FAILED"
            failed_count += 1

    # 5. Commit all changes at once
    await db.commit()

    # 6. Update Stats Table for the affected months
    for m, y in affected_periods:
        await update_monthly_stats_table(db, m, y)

    return {
        "status": "success", 
        "message": f"Analysis complete. {processed_count} processed, {failed_count} failed."
    }