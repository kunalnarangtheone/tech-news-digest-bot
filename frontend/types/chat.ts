export interface Message {
  role: "user" | "assistant";
  content: string;
}

export interface ChatRequest {
  message: string;
  session_id?: string;
}

export interface ChatResponse {
  message: string;
  session_id: string;
  message_count: number;
}

export interface SessionResponse {
  session_id: string;
  created_at: string;
  message_count: number;
  last_activity: string;
}

export interface SSEEvent {
  type: "session" | "status" | "token" | "done" | "error" | "metadata";
  content: string | {
    citations?: string[];
    confidence?: number;
    debate_flag?: boolean;
    followups?: string[];
  };
}
