export type Priority = 'Critical' | 'High' | 'Medium' | 'Low';
export type ComplaintStatus = 'Pending' | 'In Progress' | 'Resolved' | 'Rejected';
export type ComplaintType = 'Public' | 'Private';

export interface Complaint {
  id: number;
  complaint_text: string;
  complaint_type: ComplaintType;
  category: string;
  block: string;
  floor: string;
  room_no: string;
  students_affected: number;
  duration: string | null;
  support_count: number;
  predicted_priority: Priority;
  status: ComplaintStatus;
  submitted_by_username: string;
  user_has_voted: boolean;
  created_at: string;
}

export interface ComplaintCreatePayload {
  complaint_text: string;
  complaint_type: ComplaintType;
  category: string;
  block?: string;
  floor?: string;
  room_no?: string;
  students_affected: number;
  duration: string;
}

export interface PredictPayload {
  complaint_text: string;
  complaint_type: string;
  category: string;
  block?: string;
  floor?: string;
  students_affected: number;
  support_count: number;
}

export interface PredictResponse {
  predicted_priority: Priority;
  model_loaded: boolean;
}

export interface VoteResponse {
  message: string;
  support_count: number;
  predicted_priority: Priority;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
