from langchain_groq import ChatGroq
import json
import os
from dotenv import load_dotenv

load_dotenv()

model = ChatGroq(
        # It is recommended to use environment variables for API keys
        api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama-3.3-70b-versatile",
        response_format={"type": "json_object"},
    )

def getting_analysis_from_llm(data):

    prompt = f"""
You are an expert HR analyst specializing in evaluating employee exit and feedback forms.

Your task is to analyze the employee’s written feedback, which contains two types of questions:
1. MCQ-type questions (Total: 17 questions)
2. Subjective-type questions (Total: 8 questions)

Question Types Details:
- Subjective questions are: 2, 12, 13, 14, 15, 16, 17, 18
- All other questions are MCQ-type.
- The complete set of questions along with the user’s answers is provided in:
{data}

---

MCQ Analysis Requirements:
Analyze all MCQ-type questions and generate the following fields:

- total_questions
- positive_count
- positive_percentage
- negative_count
- negative_percentage

(You must correctly calculate percentages based on the MCQ responses.)

---

Subjective Questions Analysis Requirements:
For each subjective question, provide the following details:

- question_number
- question_text
- user_answer
- sentiments (positive, neutral, negative)
- sentiment_score (0–1 score)

Additionally, provide:

- overall_sentiment (percentage of positive, neutral, negative answers)
- overall_summary (a detailed professional summary of all subjective responses)

---

Output Format (Strictly JSON Only):
The final output must strictly follow valid JSON format and should match the structure shown below:

{{
  "objective_analysis": {{
    "total_questions": 18,
    "positive_count": 12,
    "positive_percentage": 67,
    "negative_count": 6,
    "negative_percentage": 33
  }},

  "subjective_analysis": {{
    "question_wise_sentiment": [
      {{
        "question_number": 19,
        "question_text": "Describe your experience with the work environment.",
        "answer_text": "The work environment was supportive...",
        "sentiment": "positive",
        "sentiment_score": 0.84
      }},
      {{
        "question_number": 20,
        "question_text": "What challenges did you face?",
        "answer_text": "Sometimes communication was unclear...",
        "sentiment": "neutral",
        "sentiment_score": 0.55
      }}
    ],

    "overall_sentiment": {{
      "positive_percentage": 52,
      "neutral_percentage": 33,
      "negative_percentage": 15
    }},

    "overall_summary": "Most subjective responses indicate that the employee had a generally positive experience, particularly appreciating the support from team members. However, some recurring concerns include communication gaps and workload inconsistencies. The responses suggest that improving clarity in task delegation and ensuring better workload balance could enhance employee satisfaction."
  }}
}}

---

Important:
- The output must be valid JSON.
- Do not include explanations, markdown, or additional text outside JSON.
"""
    
    response = model.invoke(prompt)

    final_json_data = json.loads(response.content)

    return final_json_data