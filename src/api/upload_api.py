from fastapi import APIRouter, UploadFile, File
import pandas as pd
from src.excel_processing.extract_data import making_dataframe_in_correct_format
from src.docx_processing.extracting_question_from_docx import extracting_questions_and_adding_answer

router = APIRouter()

@router.post("/upload-excel/")
async def upload_excel(file: UploadFile = File(...)):
    # Read the uploaded Excel file
    df = pd.read_excel(file.file)

    df = making_dataframe_in_correct_format(df)

    final_dict = extracting_questions_and_adding_answer(df)
    
    final_data = str(final_dict)

    return final_data