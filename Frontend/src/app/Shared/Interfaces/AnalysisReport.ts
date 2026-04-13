export interface AnalysisReport {
  full_analysis_json: {
    employee_code: string;
    name: string;
    l1_manager: string;
    l2_manager: string;
    hrbp_name: string;
    location: string;
    joining_date: string;
    exit_date: string;
    resignation_date: string;
    department: string;
    designation: string;
    objective_analysis: {
      total_questions: number;
      positive_count: number;
      positive_percentage: number;
      negative_count: number;
      negative_percentage: number;
    };
    subjective_analysis: {
      question_wise_sentiment: Array<{
        question_number: number;
        question_text: string;
        user_answer: string;
        sentiments: string;
        sentiment_score: number;
      }>;
      overall_sentiment: {
        positive_percentage: number;
        neutral_percentage: number;
        negative_percentage: number;
      };
      overall_summary: string;
      Sentiment_Definitions?: {
        positive_sentiments: string[];
        neutral_sentiments: string[];
        negative_sentiments: string[];
      };
    };
  };
}