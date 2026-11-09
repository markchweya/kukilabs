import { useState } from "react";
import { api, type KukiDocument } from "../../api";
import { ReviewSession } from "../../components/ReviewSession";
import { Citations } from "../../components/sources";
import { Button, Empty, ErrorNote, Working } from "../../components/ui";
import { relativeDays } from "../../lib/format";
import { useResource } from "../../lib/useResource";

export function CardsPanel({ doc }: { doc: KukiDocument }) {
  const cards = useResource(() => api.cards.list(doc.id), [doc.id]);
  const [generating, setGenerating] = useState(false);
  const [reviewing, setReviewing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function generate() {
    setGenerating(true);
    setError(null);
    try {
      const created = await api.cards.generate(doc.id, 12);
      if (created.length === 0) setError("No new cards: everything Kuki found is already in this deck.");
      await cards.reload();
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setGenerating(false);
    }
  }

  if (generating) return <Working label="Making flashcards…" />;
  if (cards.error) return <ErrorNote message={cards.error} onRetry={cards.reload} />;
  if (!cards.data) return null;

  const now = Date.now();
  const due = cards.data.filter((c) => new Date(`${c.due_at.replace(" ", "T")}Z`).getTime() <= now);

  if (reviewing) {
    return <ReviewSession cards={due} onFinished={() => { setReviewing(false); void cards.reload(); }} />;
  }

  if (cards.data.length === 0) {
    return (
      <div className="space-y-4">
        {error && <ErrorNote message={error} />}
        <Empty title="No flashcards yet" action={<Button variant="primary" onClick={generate}>Make flashcards</Button>}>
          Kuki writes cards from this lecture and schedules each one for just before you'd forget it.
        </Empty>
      </div>
    );
  }

  return (
    <div className="space-y-5">
      {error && <ErrorNote message={error} />}
      <div className="flex flex-wrap items-center gap-3">
        <Button variant="primary" disabled={due.length === 0} onClick={() => setReviewing(true)}>
          {due.length ? `Review ${due.length} due card${due.length === 1 ? "" : "s"}` : "Nothing due right now"}
        </Button>
        <Button onClick={generate}>Add more cards</Button>
      </div>
      <ul className="divide-y divide-line overflow-hidden rounded-3xl border border-line bg-paper">
        {cards.data.map((c) => (
          <li key={c.id} className="grid gap-1 px-5 py-4 sm:grid-cols-[1fr_1fr_auto] sm:gap-6">
            <p className="font-bold">{c.front}</p>
            <div>
              <p>{c.back}</p>
              <div className="mt-1"><Citations items={c.citations} /></div>
            </div>
            <p className="text-sm text-ink-soft sm:text-right">
              {c.repetitions === 0 ? "New" : `Next ${relativeDays(c.due_at)}`}
            </p>
          </li>
        ))}
      </ul>
    </div>
  );
}
