# from fastapi import APIRouter, UploadFile, File
# import pandas as pd
# from src.excel_processing.extract_data import making_dataframe_in_correct_format
# from src.docx_processing.extracting_question_from_docx import extracting_questions_and_adding_answer

# router = APIRouter()

# @router.post("/upload-excel/")
# async def upload_excel(file: UploadFile = File(...)):
#     # Read the uploaded Excel file
#     df = pd.read_excel(file.file)

#     df = making_dataframe_in_correct_format(df)

#     final_dict = extracting_questions_and_adding_answer(df)
    
#     final_data = str(final_dict)

#     return final_data

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi.concurrency import run_in_threadpool
import pandas as pd
import io

# Import DB and Models
from src.database.database import get_db
from src.database.models import Employee, SurveyResponse

# Import Processing Modules
from src.excel_processing.extract_data import making_dataframe_in_correct_format
from src.docx_processing.extracting_question_from_docx import extracting_questions_and_adding_answer

router = APIRouter()

@router.post("/upload-excel/")
async def upload_excel(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    try:
        # 1. Read the uploaded Excel file (Async wrapper for heavy IO)
        contents = await file.read()
        
        # Helper to read excel in threadpool to avoid blocking async loop
        def read_excel_sync(content):
            return pd.read_excel(io.BytesIO(content))
        
        df = await run_in_threadpool(read_excel_sync, contents)

        # 2. Format Dataframe (Existing logic)
        df = making_dataframe_in_correct_format(df)

        # 3. Extract Metadata & Questions (Existing logic with additions)
        # Run in threadpool as docx processing is CPU bound
        processed_data = await run_in_threadpool(extracting_questions_and_adding_answer, df)
        
        count = 0
        
        # 4. Save to Database
        for entry in processed_data:
            meta = entry['metadata']
            answers = entry['answers']
            
            # Check if Employee already exists (by Employee Code)
            stmt = select(Employee).filter(Employee.employee_code == meta['employee_code'])
            result = await db.execute(stmt)
            if result.scalar_one_or_none():
                # Skip duplicate employees
                continue

            # Create Employee Record with ALL metadata fields
            # Note: Ensure your src/database/models.py Employee table has these columns.
            new_emp = Employee(
                employee_code=meta['employee_code'],
                name=meta['name'],
                
                # Manager Hierarchy
                l1_manager=meta['l1_manager'],
                l1_manager_code=meta['l1_manager_code'],
                l2_manager=meta['l2_manager'],         
                l2_manager_code=meta['l2_manager_code'], 
                
                # HR Details
                hrbp_name=meta['hrbp_name'],
                hrbp_code=meta['hrbp_code'],          
                
                # Location & Dates
                location=meta['location'],
                joining_date=meta['joining_date'],
                exit_date=meta['exit_date'],
                date_of_resignation=meta['exit_date'], # Using Exit Date as fallback for resignation date
                survey_initiated_date=meta['survey_initiated_date'], 
                survey_submission_date=meta['survey_submission_date'], 
                
                # Defaults
                department="BYT", 
                designation="AIML Engineer"
            )
            db.add(new_emp)
            await db.flush() 

            # Create Survey Response with mapped answers
            new_resp = SurveyResponse(
                employee_id=new_emp.id,
                raw_answers=answers,
                status="PENDING" # Set status to PENDING for LLM analysis
            )
            db.add(new_resp)
            
            count += 1

        
        await db.commit()

        return {
            "status": "success", 
            "message": f"Successfully uploaded and processed {count} employee records."
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")