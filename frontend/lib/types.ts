export type PaperStatus = "uploaded" | "processing" | "ready" | "failed";

export interface Paper {
  paper_id: string;
  filename: string;
  title?: string | null;
  num_pages: number;
  num_chunks: number;
  status: PaperStatus;
  uploaded_at: string;
  error?: string | null;
}

export interface SourceChunk {
  paper_id: string;
  paper_title?: string | null;
  page_number: number;
  chunk_id: string;
  text: string;
  score: number;
}

export interface ChatResponse {
  answer: string;
  sources: SourceChunk[];
  conversation_id: string;
  used_papers: string[];
}

export interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: SourceChunk[];
}

export const SUMMARY_TYPES: { value: string; label: string }[] = [
  { value: "executive", label: "Executive Summary" },
  { value: "detailed", label: "Detailed Summary" },
  { value: "contributions", label: "Key Contributions" },
  { value: "methodology", label: "Methodology" },
  { value: "dataset", label: "Dataset Used" },
  { value: "results", label: "Results" },
  { value: "limitations", label: "Limitations" },
  { value: "future_work", label: "Future Work" },
  { value: "novelty", label: "Novelty" },
  { value: "practical_applications", label: "Practical Applications" },
  { value: "eli10", label: "Explain Like I'm 10" },
  { value: "viva", label: "Viva Prep Questions" },
  { value: "interview_questions", label: "Interview Questions" },
  { value: "quiz", label: "Quiz" },
];
