// Mirrors the backend's pydantic response models (backend/kuki/**).
// Keep field names identical so responses can be used without mapping.

export type DocumentStatus = "processing" | "ready" | "failed";
export type DocumentKind = "pdf" | "slides" | "doc" | "text" | "image" | "audio" | "web";

export interface KukiDocument {
  id: string;
  title: string;
  filename: string;
  kind: DocumentKind;
  status: DocumentStatus;
  error: string | null;
  source_url: string | null;
  license: string | null;
  attribution: string | null;
  audio_url: string | null;
  has_local_audio: boolean;
  created_at: string;
  segment_count: number;
}

export interface Segment {
  id: number;
  ordinal: number;
  locator: string;
  text: string;
}

export interface Citation {
  segment_id: number;
  document_id: string;
  document_title: string;
  locator: string;
  excerpt: string;
}

interface Cited {
  citations: Citation[];
  grounded: boolean;
}

export interface Concept extends Cited { term: string; explanation: string }
export interface KeyPoint extends Cited { point: string }
export interface Example extends Cited { title: string; explanation: string }
export interface Mistake extends Cited { mistake: string; correction: string }

export type Knowledge = "notes_only" | "fill_gaps";

export interface StudyPack {
  document_id: string;
  title: string;
  overview: string;
  mode: "ai" | "extractive";
  model: string | null;
  knowledge: Knowledge;
  concepts: Concept[];
  key_points: KeyPoint[];
  examples: Example[];
  common_mistakes: Mistake[];
  notice: string | null;
}

export interface Question {
  id: number;
  document_id: string;
  concept: string;
  prompt: string;
  citations: Citation[];
}

export type Verdict = "correct" | "partial" | "incorrect";
export type MisconceptionType =
  | "none" | "confused_concepts" | "factual_error" | "overgeneralization"
  | "missing_step" | "vague" | "off_topic";

export interface Grade {
  attempt_id: number;
  question_id: number;
  verdict: Verdict;
  score: number;
  got_right: string[];
  misconception: string;
  misconception_type: MisconceptionType;
  nudge: string;
  explanation: string;
  ideal_answer: string;
  key_ideas: string[];
  citations: Citation[];
  mode: "ai" | "keyword";
}

export interface Flashcard {
  id: number;
  document_id: string;
  front: string;
  back: string;
  citations: Citation[];
  due_at: string;
  ease: number;
  interval_days: number;
  repetitions: number;
  lapses: number;
}

export type ReviewButton = "again" | "hard" | "good" | "easy";

export interface DeckStats { total: number; due_now: number; learned: number }

export interface ConceptProgress {
  concept: string;
  document_id: string;
  document_title: string;
  attempts: number;
  latest_score: number;
  best_score: number;
  latest_misconception: string | null;
  status: "weak" | "improving" | "mastered";
}

export interface Insights {
  concepts: ConceptProgress[];
  mistake_patterns: Record<string, number>;
  total_attempts: number;
}

export interface Answer {
  question: string;
  answer: string;
  found: boolean;
  citations: Citation[];
  mode: "ai" | "search";
}

export interface Check { ok: boolean; label: string; detail: string; fix: string | null }

export interface Status {
  version: string;
  ai_ready: boolean;
  chat_model: string;
  embed_model: string;
  checks: Record<"ollama" | "chat_model" | "embed_model" | "ocr" | "whisper", Check>;
}

export interface Lecture { number: number; title: string; url: string; document_id: string | null }

export interface Course {
  id: string;
  title: string;
  institution: string;
  instructor: string;
  subject: string;
  description: string;
  license: string;
  license_url: string;
  homepage: string;
  lectures: Lecture[];
}

export interface SearchHit {
  segment_id: number;
  document_id: string;
  document_title: string;
  locator: string;
  text: string;
  method: string;
}
