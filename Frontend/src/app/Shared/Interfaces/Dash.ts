export interface Dash {
  [x: string]: any;
  Emp_Code: any;
  SNo?: number; // Optional, for UI numbering
  employee_code: string;
  name: string;
  l1_manager: string;
  l1_manager_code: string;
  l2_manager: string;
  l2_manager_code: string;
  hrbp_name: string;
  hrbp_code: string;
  location: string;
  joining_date: string;
  exit_date: string;
  survey_initiated_date: string | null;
  survey_submission_date: string;
  date_of_resignation: string;
  department: string;
  designation: string;
  overall_sentiment: string | null;
}