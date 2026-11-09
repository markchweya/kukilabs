// A flashcard review session: think, flip, then rate how well you remembered.
// Keyboard: Space flips, 1-4 rate (Again, Hard, Good, Easy).
import { useCallback, useEffect, useState } from "react";
import { api, type Flashcard, type ReviewButton } from "../api";
import { intervalLabel, previewInterval } from "../lib/srs";
import { Citations } from "./sources";
import { ErrorNote } from "./ui";

const BUTTONS: { id: ReviewButton; label: string; key: string; tone: string }[] = [
  { id: "again", label: "Again", key: "1", tone: "text-blush" },
  { id: "hard", label: "Hard", key: "2", tone: "text-sun" },
  { id: "good", label: "Good", key: "3", tone: "text-whale-deep" },
  { id: "easy", label: "Easy", key: "4", tone: "text-sea" },
];

export function ReviewSession({ cards, onFinished }: { cards: Flashcard[]; onFinished: (reviewed: number) => void }) {
  const [queue, setQueue] = useState(cards);
  const [flipped, setFlipped] = useState(false);
  const [reviewed, setReviewed] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const card = queue[0];

  const rate = useCallback(
    async (button: ReviewButton) => {
      if (!card || !flipped) return;
      try {
        await api.cards.review(card.id, button);
        // "Again" puts the card back at the end of this session so it's seen once more today.
        setQueue((q) => (button === "again" ? [...q.slice(1), q[0]] : q.slice(1)));
        setReviewed((n) => n + 1);
        setFlipped(false);
      } catch (e) {
        setError(e instanceof Error ? e.message : String(e));
      }
    },
    [card, flipped],
  );

  useEffect(() => {
    if (!card) onFinished(reviewed);
  }, [card, onFinished, reviewed]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLTextAreaElement || e.target instanceof HTMLInputElement) return;
      if (e.key === " ") { e.preventDefault(); setFlipped((f) => !f); }
      const b = BUTTONS.find((x) => x.key === e.key);
      if (b) void rate(b.id);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [rate]);

  if (!card) return null;

  return (
    <div className="mx-auto max-w-2xl space-y-5">
      <p className="text-center text-sm text-ink-soft">{queue.length} left in this session</p>
      <button
        type="button"
        onClick={() => setFlipped((f) => !f)}
        aria-label={flipped ? "Show question" : "Show answer"}
        className={`flex min-h-64 w-full flex-col items-center justify-center gap-4 rounded-[2rem] px-8 py-10 text-center transition-colors ${flipped ? "stitched bg-belly" : "bg-paper"}`}
      >
        <p className="font-display text-2xl font-semibold sm:text-3xl">{card.front}</p>
        {flipped ? (
          <p className="max-w-lg text-lg">{card.back}</p>
        ) : (
          <p className="text-sm text-ink-soft">Think of the answer, then tap to check</p>
        )}
      </button>
      {flipped && <div className="text-center"><Citations items={card.citations} /></div>}

      <div className="grid grid-cols-4 gap-2" aria-label="How well did you remember?">
        {BUTTONS.map((b) => (
          <button
            key={b.id}
            type="button"
            disabled={!flipped}
            onClick={() => void rate(b.id)}
            className="rounded-2xl border border-line bg-paper px-2 py-3 transition-colors hover:border-whale disabled:opacity-40"
          >
            <span className={`block font-bold ${b.tone}`}>{b.label}</span>
            <span className="block text-xs text-ink-soft">
              {/* "Again" re-queues the card in this session before it is rescheduled. */}
              {b.id === "again" ? "this session" : intervalLabel(previewInterval(card, card.ease, b.id))}
            </span>
          </button>
        ))}
      </div>
      <p className="hidden text-center text-xs text-ink-soft sm:block">Space to flip · 1–4 to rate</p>
      {error && <ErrorNote message={error} />}
    </div>
  );
}
