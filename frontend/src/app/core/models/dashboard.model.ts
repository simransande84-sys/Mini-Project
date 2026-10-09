export interface DashboardStats {
  total_complaints: number;
  by_priority: Record<string, number>;
  by_category: Record<string, number>;
  by_block: Record<string, number>;
  by_complaint_type: Record<string, number>;
  monthly_trend: { month: string; count: number }[];
  model_info: { loaded: boolean; classes?: string[]; model?: string };
}
