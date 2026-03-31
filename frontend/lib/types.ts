export type MovementType = "income" | "expense" | "transfer";
export type MovementStatus = "pending" | "confirmed" | "discarded";

export interface Category {
  id: string;
  name: string;
  icon: string | null;
  color: string | null;
  parent_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface Tag {
  id: string;
  name: string;
  color: string | null;
  created_at: string;
  updated_at: string;
}

export interface Movement {
  id: string;
  type: MovementType;
  amount: string;
  currency: string;
  account: string | null;
  movement_date: string;
  concept: string | null;
  merchant: string | null;
  status: MovementStatus;
  notes: string | null;
  source_email_id: string | null;
  source_email_sender: string | null;
  source_email_subject: string | null;
  duplicate_group_id: string | null;
  is_duplicate: boolean;
  superseded_by_id: string | null;
  category: Category | null;
  tags: Tag[];
  created_at: string;
  updated_at: string;
}

export interface Sender {
  id: string;
  email_pattern: string;
  name: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ProcessResult {
  status: string;
  emails_fetched: number;
  movements_detected: number;
  movements_stored: number;
  duplicates_found: number;
  details: {
    email_id: string;
    subject: string;
    has_movement: boolean;
    movements_count: number;
  }[];
}
