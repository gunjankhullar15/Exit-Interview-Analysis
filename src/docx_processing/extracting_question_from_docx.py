# from docx2python import docx2python
# import re


# def extracting_questions_and_adding_answer(df):

#     docs_path = r'G:\Netsmartz\Netsmartz\leaving office form\Exit-Interview-Analysis\src\docx_processing\Employee Exit Interview Feedback Form.docx'

#     # Load the .docx file
#     doc_data = docx2python(docs_path)
    
#     # Extract all text as plain text (keeps numbering & formatting)
#     text = doc_data.text
    
#     # Split on question numbers (1), 2), 3), 21), etc.)
#     parts = re.split(r"\n?\d+\)\s*", text)
    
#     # Remove empty items
#     questions = [q.strip() for q in parts if q.strip()]
    
#     all_questions = []
    
#     # making a list of all questions with numbering
#     for i, q in enumerate(questions):
#         all_questions.append(f"Question {i} -> {q}\n")
    
#     #removing the feedback question from the list
#     all_questions.pop(0)
    
#     #cleaning the last question removing the additional information from it.
#     end_marker = "Yes ☐ No ☐"
#     text1 = all_questions[24]
#     cleaned_text = ""
    
#     # Cut the text at the first occurrence of the marker
#     if end_marker in text1:
#         cleaned_text = text1.split(end_marker)[0] + end_marker
#     else:
#         cleaned_text = text1
    
#     all_questions[24] = cleaned_text
    
#     all_employee_data = []

#     for i in range(len(df)):
#         question_dict = {}

#         for i in range(25):
#             column_name = i+1           # Column names as string: '1', '2', etc.
#             answer_text = df.loc[0, column_name]   # 0-th row value
#             question_text = all_questions[i]       # Get question from list
#             question_dict[question_text] = answer_text  # Add to dictionary

#         all_employee_data.append(".....................................................................")
#         all_employee_data.append(question_dict)

#         df = df.iloc[1:].reset_index(drop=True)


#     return all_employee_data



from docx2python import docx2python
import re
import pandas as pd

def extracting_questions_and_adding_answer(df):
    # Path to your docx file
    docs_path = r'G:\Netsmartz\Netsmartz\leaving office form\Exit-Interview-Analysis\src\docx_processing\Employee Exit Interview Feedback Form.docx'

    # Load the .docx file
    doc_data = docx2python(docs_path)
    
    # Extract all text as plain text
    text = doc_data.text
    
    # Split on question numbers
    parts = re.split(r"\n?\d+\)\s*", text)
    
    # Remove empty items
    questions = [q.strip() for q in parts if q.strip()]
    
    all_questions = []
    
    # Making a list of all questions with numbering
    for i, q in enumerate(questions):
        all_questions.append(f"Question {i} -> {q}\n")
    
    # Removing the feedback question from the list (pop 0)
    all_questions.pop(0)
    
    # Cleaning the last question
    end_marker = "Yes ☐ No ☐"
    text1 = all_questions[24]
    cleaned_text = ""
    
    if end_marker in text1:
        cleaned_text = text1.split(end_marker)[0] + end_marker
    else:
        cleaned_text = text1
    
    all_questions[24] = cleaned_text
    
    # --- MODIFIED SECTION BELOW ---
    structured_data_list = []

    # Loop through the dataframe
    # We use a copy of range len because we are slicing df inside the loop
    total_rows = len(df)
    
    # Helper to safely clean extracted values (Handle NaN/Empty)
    def clean_val(val):
        if pd.isna(val) or str(val).lower() == 'nan':
            return None
        return str(val).strip()

    for _ in range(total_rows):
        # 1. Extract Answers
        question_dict = {}
        for i in range(25):
            column_name = i+1                       # Columns 1, 2, 3...
            answer_text = df.loc[0, column_name]    # Get answer from 0th row
            question_text = all_questions[i]        
            
            if pd.isna(answer_text):
                answer_text = "N/A"
            else:
                answer_text = str(answer_text)
                
            question_dict[question_text] = answer_text 

        # 2. Extract Metadata (Including Survey Initiated Date)
        metadata_dict = {
            "employee_code": clean_val(df.loc[0, "Employee Code"]),
            "name": clean_val(df.loc[0, "Employee Name"]),
            
            "l1_manager": clean_val(df.loc[0, "L1 Manager"]),
            "l1_manager_code": clean_val(df.loc[0, "L1 Managercode"]),
            
            "l2_manager": clean_val(df.loc[0, "L2 Manager"]),
            "l2_manager_code": clean_val(df.loc[0, "L2 Manager Code"]),
            
            "hrbp_name": clean_val(df.loc[0, "HR Manager"]), 
            "hrbp_code": clean_val(df.loc[0, "HR Manager Code"]),
            
            "location": clean_val(df.loc[0, "Location"]),
            
            "joining_date": clean_val(df.loc[0, "Joining Date"]),
            "exit_date": clean_val(df.loc[0, "Exit Date"]),
            "date_of_resignation": clean_val(df.loc[0, "Date of Resignation"]),

            "department": clean_val(df.loc[0, "Department"]),
            "designation": clean_val(df.loc[0, "Designation"]),
            
            # --- Handling the Empty "Survey Initiated Date" ---
            # If the column exists, it will extract; clean_val will turn NaN to None
            "survey_initiated_date": clean_val(df.loc[0, "Survey Initiated Date"]) if "Survey Initiated Date" in df.columns else None,
            
            "survey_submission_date": clean_val(df.loc[0, "Survey Submission Date"])
        }

        # Combine into one object
        structured_data_list.append({
            "metadata": metadata_dict,
            "answers": question_dict
        })

        # Remove the processed row from dataframe to prepare for next iteration
        df = df.iloc[1:].reset_index(drop=True)

    return structured_data_list