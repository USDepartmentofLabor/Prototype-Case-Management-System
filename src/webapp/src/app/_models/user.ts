import { Role } from "./role";

export interface User extends Avatar {
  id: number;
  email: string;
  username: string;
  role: Role;
  name: string;
  location: string;
  last_seen_at: string;
  is_active?: true;
  created_at: string;
  updated_at: string;
  confirmed: boolean;
  confirmed_at: string;
  first_initial?: string;
  color?: string;
}

export interface Avatar {
  firstInitial: string;
  avatarBgColor: string;
}
