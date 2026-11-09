// Client-side preview of the backend's SM-2 schedule (backend/kuki/study/srs.py),
// used only to label review buttons with "in 6 days" etc. The server remains
// the source of truth for the actual schedule.
import type { Flashcard, ReviewButton } from "../api";

const GRADES: Record<ReviewButton, number> = { again: 1, hard: 3, good: 4, easy: 5 };
const EASY_FIRST_INTERVAL = 4; // days, matches EASY_FIRST_INTERVAL in srs.py

export function previewInterval(card: Pick<Flashcard, "interval_days" | "repetitions">, ease: number, button: ReviewButton): number {
  const grade = GRADES[button];
  if (grade < 3) return 1;
  if (card.repetitions === 0) return button === "easy" ? EASY_FIRST_INTERVAL : 1;
  if (card.repetitions === 1) return 6;
  return Math.max(1, Math.round(card.interval_days * ease));
}

export function intervalLabel(days: number): string {
  if (days <= 1) return "tomorrow";
  if (days < 30) return `${days} days`;
  const months = Math.round(days / 30);
  return months === 1 ? "1 month" : `${months} months`;
}
