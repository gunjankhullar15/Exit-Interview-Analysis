from docx2python import docx2python
import re


def extracting_questions_and_adding_answer(df):

    docs_path = r'G:\Netsmartz\Netsmartz\leaving office form\Exit-Interview-Analysis\src\docx_processing\Employee Exit Interview Feedback Form.docx'

    # Load the .docx file
    doc_data = docx2python(docs_path)
    
    # Extract all text as plain text (keeps numbering & formatting)
    text = doc_data.text
    
    # Split on question numbers (1), 2), 3), 21), etc.)
    parts = re.split(r"\n?\d+\)\s*", text)
    
    # Remove empty items
    questions = [q.strip() for q in parts if q.strip()]
    
    all_questions = []
    
    # making a list of all questions with numbering
    for i, q in enumerate(questions):
        all_questions.append(f"Question {i} -> {q}\n")
    
    #removing the feedback question from the list
    all_questions.pop(0)
    
    #cleaning the last question removing the additional information from it.
    end_marker = "Yes ☐ No ☐"
    text1 = all_questions[24]
    cleaned_text = ""
    
    # Cut the text at the first occurrence of the marker
    if end_marker in text1:
        cleaned_text = text1.split(end_marker)[0] + end_marker
    else:
        cleaned_text = text1
    
    all_questions[24] = cleaned_text
    
    all_employee_data = []

    for i in range(len(df)):
        question_dict = {}

        for i in range(25):
            column_name = i+1           # Column names as string: '1', '2', etc.
            answer_text = df.loc[0, column_name]   # 0-th row value
            question_text = all_questions[i]       # Get question from list
            question_dict[question_text] = answer_text  # Add to dictionary

        all_employee_data.append(".....................................................................")
        all_employee_data.append(question_dict)

        df = df.iloc[1:].reset_index(drop=True)


    return all_employee_data