import type { DocumentKind } from "../api";

export const KIND_LABEL: Record<DocumentKind, string> = {
  pdf: "PDF",
  slides: "Slides",
  doc: "Word",
  text: "Notes",
  image: "Photo",
  audio: "Recording",
  web: "Open course",
};

/** How a document's parts are named, for "12 slides" / "30 chapters". */
export function partsLabel(kind: DocumentKind, count: number): string {
  const noun: Record<DocumentKind, string> = {
    pdf: "page", slides: "slide", doc: "section", text: "section",
    image: "photo", audio: "minute", web: "section",
  };
  const n = noun[kind];
  return `${count} ${n}${count === 1 ? "" : "s"}`;
}

/** SQLite timestamps are UTC without a zone marker. */
export function parseUtc(ts: string): Date {
  return new Date(ts.includes("T") ? ts : `${ts.replace(" ", "T")}Z`);
}

export function relativeDays(ts: string): string {
  const days = Math.round((parseUtc(ts).getTime() - Date.now()) / 86_400_000);
  if (days <= 0) return "today";
  if (days === 1) return "tomorrow";
  if (days < 30) return `in ${days} days`;
  return `in ${Math.round(days / 30)} months`;
}
