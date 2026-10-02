export type TranscriptFormat = "meet" | "zoom_vtt" | "teams" | "plain_text" | "generic";

export interface MeetingMetadata {
  title: string;
  detected_format: TranscriptFormat;
  total_words: number;
  total_turns: number;
  duration_seconds: number;
  participants: string[];
  speaker_turn_counts: Record<string, number>;
}

export interface ActionItem {
  task: string;
  assignee: string;
  deadline: string | null;
  priority: "alta" | "media" | "baja";
  context: string | null;
}

export interface KeyDecision {
  decision: string;
  rationale?: string | null;
  impact?: string | null;
}

export interface TopicDiscussion {
  topic: string;
  summary: string;
  participants_involved: string[];
}

export interface MeetingSummaryReport {
  meeting_id: string;
  title: string;
  executive_summary: string;
  topics: TopicDiscussion[];
  decisions: KeyDecision[];
  action_items: ActionItem[];
  open_questions: string[];
  email_followup: string;
  metadata: MeetingMetadata;
  model_used: string;
  mode: string;
  created_at: string;
}

export interface PipelineEvent {
  stage: string;
  progress: number;
  message: string;
  payload?: {
    meeting_id?: string;
    metadata?: MeetingMetadata;
    participants?: string[];
    total_chunks?: number;
    current_chunk?: number;
    report?: MeetingSummaryReport;
    [key: string]: any;
  } | null;
}

export interface MeetingListItem {
  meeting_id: string;
  title: string;
  format: string;
  total_words: number;
  duration_seconds: number;
  participants_count: number;
  created_at: string;
}

export interface FixtureSample {
  name: string;
  title: string;
  content: string;
}

export interface ChatMessage {
  id?: string;
  question: string;
  answer: string;
  created_at?: string;
}
