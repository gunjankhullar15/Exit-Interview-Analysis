from langchain_groq import ChatGroq
import json
from src.config.pydantic_config import settings

model = ChatGroq(
        
        api_key=settings.GROQ_API_KEY,
        model_name="llama-3.3-70b-versatile" ,
        response_format={"type": "json_object"},
    )

def getting_analysis_from_llm(data):

    prompt = f"""
You are an expert HR analyst specializing in evaluating employee exit and feedback forms.

Your task is to analyze an employee’s written feedback containing two types of questions:
1. MCQ-type questions (Total: 17 questions)
2. Subjective-type questions (Total: 8 questions)

Question Type Details:
- Subjective question numbers: 2, 12, 13, 14, 15, 16, 17, 18
- All remaining questions are MCQ-type
- The complete set of questions and user answers is provided below:
{data}

---

MCQ Analysis Requirements:
Analyze only MCQ-type questions and generate the following fields:
- total_questions
- positive_count
- positive_percentage
- negative_count
- negative_percentage

Percentages must be accurately calculated based on MCQ responses.

---

Subjective Analysis Requirements:
For each subjective question, provide:
- question_number
- question_text
- answer_text
- sentiment (positive, neutral, or negative)
- sentiment_score (float between 0 and 1)

Additionally, compute:
- overall_sentiment (percentage distribution of positive, neutral, and negative answers)
- overall_summary (a professional summary strictly between 100 and 200 words from the subjective questions answers)

---

Sentiment Definitions (Subjective Only):
Extract sentiment points strictly from the provided data and return them in bullet-point format:
- Positive Sentiments
- Neutral Sentiments
- Negative Sentiments

---

Company Feedback:
Summarize the negative feedback provided by the employee.
This should clearly describe areas where the company needs improvement.
Use concise bullet points.

---

Leaving Reason Classification & Analytics:
Identify the primary reason for leaving from the list below. 
1. In the "leaving_reason" object, assign value 1 to the most relevant reason and 0 to all others.
2. In the "exit_analysis" object, provide the string name of the category and its controllability.

REQUIRED REASONS:
- career change (Controllable: false)
- personal reasons (Controllable: false)
- better work-life balance (Controllable: true)
- role redundancy (Controllable: true)
- dissatisfaction with management (Controllable: true)
- seeking higher salary (Controllable: true)
- lack of growth opportunities (Controllable: true)
- toxic work environment (Controllable: true)

---

STRICT OUTPUT FORMAT (VALID JSON ONLY):
Do not include explanations, markdown, comments, or additional text.
Return only valid JSON exactly in the structure below.

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
        "question_number": 2,
        "question_text": "Question text here",
        "answer_text": "User answer here",
        "sentiment": "positive",
        "sentiment_score": 0.84
      }}
    ],
    "overall_sentiment": {{
      "positive_percentage": 52,
      "neutral_percentage": 33,
      "negative_percentage": 15
    }},
    "overall_summary": "300–400 word professional summary here.",
    "sentiment_definitions": {{
      "positive_sentiments": [
        "- supportive teammates",
        "- learning opportunities"
      ],
      "neutral_sentiments": [
        "- average workload",
        "- standard communication"
      ],
      "negative_sentiments": [
        "- unfair treatment",
        "- micromanagement",
        "- lack of appreciation",
        "- poor management",
        "- favoritism",
        "- biased decisions"
      ]
    }},
    "company_feedback": [
      "Address unfair treatment by ensuring transparency and fairness in workplace practices.",
      "Reduce micromanagement by promoting trust and autonomy.",
      "Improve employee recognition and appreciation.",
      "Strengthen management practices through leadership training.",
      "Eliminate favoritism using objective evaluation criteria.",
      "Ensure unbiased and well-documented decision-making."
    ],
    "leaving_reason": {{
      "career change": 0,
      "personal reasons": 0,
      "better work-life balance": 0,
      "health reasons": 0,
      "dissatisfaction with management": 1,
      "seeking higher salary": 0,
      "lack of growth opportunities": 0,
      "toxic work environment": 0
    }},
    "exit_analysis": {{
        "primary_reason_category": "Management & Leadership",
        "is_controllable": true
    }}
  }}
}}
"""
    
    response = model.invoke(prompt)

    final_json_data = json.loads(response.content)

    return final_json_data