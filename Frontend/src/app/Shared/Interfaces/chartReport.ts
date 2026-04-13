export interface ReportData {
  start_date: string;
  end_date: string;
  summary: {
    total_exits: number;
  };
  exits_by_department: { [dept: string]: number };
  reason_counts: { [reason: string]: number };
  overall_percentage: { [reason: string]: string };
  feedback_by_reason: { [reason: string]: string[] };
}

export interface BreakdownItem {
  label: string;
  count: number;
  percentage: number;
  color: string;
}