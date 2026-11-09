// Simple line icons for each kind of study material (24px grid, 1.8 stroke).
import type { DocumentKind } from "../api";

const PATHS: Record<DocumentKind, string> = {
  slides: "M3 5h18v11H3zM12 16v4M8 20h8M7 9h6M7 12h4",
  pdf: "M6 3h8l4 4v14H6zM14 3v4h4M9 12h6M9 15h6M9 18h4",
  doc: "M6 3h12v18H6zM9 7h6M9 10h6M9 13h6M9 16h3",
  text: "M5 4h14M5 9h14M5 14h10M5 19h7",
  image: "M3 6h18v13H3zM8 11a1.5 1.5 0 1 0 0-.01M21 16l-5-5-8 8",
  audio: "M12 4v10M8 9v4a4 4 0 0 0 8 0V9M12 17v3M9 20h6",
  web: "M3 8l9-4 9 4-9 4zM7 10v5c3 2 7 2 10 0v-5M21 8v6",
};

export function KindIcon({ kind, className = "" }: { kind: DocumentKind; className?: string }) {
  return (
    <svg viewBox="0 0 24 24" aria-hidden className={className} fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d={PATHS[kind]} />
    </svg>
  );
}
