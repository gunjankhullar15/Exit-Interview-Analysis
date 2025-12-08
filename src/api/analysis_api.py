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


from fastapi import APIRouter, Depends
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
import asyncio
import json
from src.database.database import get_db
from src.database.models import AnalysisReport, SurveyResponse, Employee
from src.llm.llm_services import getting_analysis_from_llm

router = APIRouter()


MAX_CONCURRENT_LLM_CALLS = 5
llm_semaphore = asyncio.Semaphore(MAX_CONCURRENT_LLM_CALLS)

@router.post("/Generate_llm_response/")
async def Generate_llm_response(db: AsyncSession = Depends(get_db)):
     
    stmt = select(SurveyResponse).options(
        selectinload(SurveyResponse.employee)
    ).filter(SurveyResponse.status == "PENDING")
    
    result = await db.execute(stmt)
    pending_surveys = result.scalars().all()
    
    if not pending_surveys:
        return {"status": "success", "message": "No pending reports to process."}

    async def process_single_llm_call(survey_obj):
        async with llm_semaphore:
            if not survey_obj.raw_answers:
                return survey_obj, None
            
            # Convert raw dict to string for LLM
            data_str = json.dumps(survey_obj.raw_answers, indent=2)
            
            
            try:
                llm_result = await run_in_threadpool(getting_analysis_from_llm, data_str)
                return survey_obj, llm_result
            except Exception as e:
                print(f"LLM Error for Emp ID {survey_obj.employee_id}: {e}")
                return survey_obj, None

    
    tasks = [process_single_llm_call(survey) for survey in pending_surveys]
    
    processed_count = 0
    failed_count = 0

    
    for completed_task in asyncio.as_completed(tasks):
        survey, analysis_json = await completed_task
        
        if analysis_json:
            try:
                
                emp = survey.employee

                sentiment_val = "N/A"
                try:
                    
                    obj_data = analysis_json.get("objective_analysis", {})
                    obj_pos = float(obj_data.get("positive_percentage", 0))
                    obj_neg = float(obj_data.get("negative_percentage", 0))
                    
                    obj_neu = max(0, 100 - (obj_pos + obj_neg))

                   
                    subj_data = analysis_json.get("subjective_analysis", {})
                    subj_overall = subj_data.get("overall_sentiment", {})
                    
                    subj_pos = 0.0
                    subj_neg = 0.0
                    subj_neu = 0.0
                    
                    if isinstance(subj_overall, dict):
                        subj_pos = float(subj_overall.get("positive_percentage", 0))
                        subj_neg = float(subj_overall.get("negative_percentage", 0))
                        subj_neu = float(subj_overall.get("neutral_percentage", 0))

                    
                    final_pos = (obj_pos + subj_pos) / 2
                    final_neg = (obj_neg + subj_neg) / 2
                    final_neu = (obj_neu + subj_neu) / 2
                    
                    
                    if final_pos >= final_neg and final_pos >= final_neu:
                        sentiment_val = "Positive"
                    elif final_neg >= final_pos and final_neg >= final_neu:
                        sentiment_val = "Negative"
                    else:
                        sentiment_val = "Neutral"

                except Exception as calc_err:
                    print(f"Sentiment Calc Error: {calc_err}")
                    sentiment_val = "Analyzed" 
                
                emp.overall_sentiment = sentiment_val
                
                metadata_json = {
                    "employee_code": emp.employee_code,
                    "name": emp.name,
                    "l1_manager": emp.l1_manager or "N/A",
                    "l2_manager": emp.l2_manager or "N/A",
                    "hrbp_name": emp.hrbp_name or "N/A",
                    "location": emp.location or "N/A",
                    "joining_date": emp.joining_date or "N/A",
                    "exit_date": emp.exit_date or "N/A"
                }

                
                full_combined_json = {**metadata_json, **analysis_json}

                
                new_report = AnalysisReport(
                    employee_id=survey.employee_id,
                    full_analysis_json=full_combined_json
                )
                db.add(new_report)

                
                survey.status = "COMPLETED"
                
                
                await db.commit()
                processed_count += 1
                
            except Exception as db_err:
                print(f"Database Save Error for Emp ID {survey.employee_id}: {db_err}")
                await db.rollback()
                failed_count += 1
        else:
            # Handle LLM Failure
            survey.status = "FAILED"
            await db.commit()
            failed_count += 1

    return {
        "status": "success", 
        "message": f"Report generated successfully for {processed_count} rows.",
        "failed": failed_count
    }