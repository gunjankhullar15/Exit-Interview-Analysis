#from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
import json
from src.config.pydantic_config import settings

model = ChatOpenAI(
    api_key=settings.OPENAI_API_KEY,
    model="gpt-4o-mini",
    temperature=0,
    model_kwargs={"response_format": {"type": "json_object"}},
    max_retries=3 
)

async def getting_analysis_from_llm(data):

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

# >>> ADDED / UPDATED: CONCEPTUAL CATEGORY DEFINITIONS <<<
CATEGORY DEFINITIONS & CONCEPTUAL BOUNDARIES:
You must strictly evaluate the core intent of the employee's feedback using these boundaries:

- career change: The employee is leaving the current industry/profession entirely or returning to full-time education. 
- personal reasons: The driver for leaving originates COMPLETELY OUTSIDE the workplace (e.g., family circumstances, personal health, relocation). If the feedback mentions ANY individual, behavior, or policy inside the company, it CANNOT be a personal reason.
- better work-life balance: The employee's primary focus is on their schedule, time, or location (e.g., seeking remote work, escaping shift timings, reducing commute, or recovering from burnout).
- role redundancy: The company explicitly eliminated the position or laid off the employee.
- dissatisfaction with management: The employee is unhappy with operational or structural leadership. This includes being assigned out-of-scope work, lack of role clarity, poor company policies, or micromanagement. 
- seeking higher salary: The employee's primary focus is base compensation, pay, or financial benefits.
- lack of growth opportunities: The employee is seeking career advancement or skill development that the company cannot provide (e.g., seeking upward mobility, promotions, or better technical projects).
- toxic work environment: The employee is experiencing negative interpersonal dynamics. This includes unfair favoritism, discrimination, hostility, harassment, or unprofessional peer/leadership behavior.
# >>> END ADDED INSTRUCTIONS <<<

---

Leaving Reason Classification & Analytics:
Identify the primary reason for leaving from the list below based strictly on the definitions above. 
1. In the "leaving_reason" object, assign value 1 to the most relevant reason and 0 to all others.
2. In the "exit_analysis" object, provide the string name of the category, its controllability, and a "supporting_quote".

3. The "supporting_quote" MUST be a pure COPY-PASTE extraction from the provided `{data}`. 
   - RULE 1: Find the exact text the employee wrote that justifies your category and extract the COMPLETE SENTENCE containing that thought.
   - RULE 2: DO NOT extract mid-sentence fragments. The quote must start with a capital letter and end with a period or proper punctuation.
   - RULE 3: DO NOT rephrase, paraphrase, or fix the employee's grammar. If the employee wrote a grammatically incorrect full sentence, copy it exactly.
   - RULE 4: If no specific text justifies the reason, return an empty string "".

CRITICAL INSTRUCTION: You MUST ONLY use one of the exact reasons from the list below. Do not invent new categories. 

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
      "role redundancy": 0,
      "dissatisfaction with management": 0,
      "seeking higher salary": 0,
      "lack of growth opportunities": 0,
      "toxic work environment": 0
    }},
    "exit_analysis": {{
        "primary_reason_category": "[INSERT SELECTED CATEGORY HERE]",
        "is_controllable": true,
        "supporting_quote": "[COPY EXACT TEXT FROM DATA OR LEAVE BLANK]"
    }}
  }}
}}
"""
    
    response = await model.ainvoke(prompt)

    final_json_data = json.loads(response.content)

    return final_json_data