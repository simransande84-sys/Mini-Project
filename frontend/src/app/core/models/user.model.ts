export interface User {
  id: number;
  username: string;
  first_name: string;
  email: string;
  is_staff: boolean;
  roll_no: string | null;
  profile_complete: boolean;
}

export interface StudentProfile {
  roll_no: string;
  block: string;
  floor: string;
  room_no: string;
  phone: string;
  profile_complete: boolean;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}
