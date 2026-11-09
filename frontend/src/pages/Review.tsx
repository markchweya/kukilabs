// Daily review: every due flashcard across the whole library in one session.
import { useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import { ReviewSession } from "../components/ReviewSession";
import { Button, Empty, ErrorNote } from "../components/ui";
import { useResource } from "../lib/useResource";

export default function Review() {
  const due = useResource(() => api.cards.due(), []);
  const stats = useResource(() => api.cards.stats(), []);
  const [session, setSession] = useState(false);
  const [finished, setFinished] = useState<number | null>(null);

  if (due.error) return <ErrorNote message={due.error} onRetry={due.reload} />;
  if (!due.data || !stats.data) return null;

  if (session && due.data.length > 0) {
    return (
      <ReviewSession
        cards={due.data}
        onFinished={(n) => {
          setSession(false);
          setFinished(n);
          void due.reload();
          void stats.reload();
        }}
      />
    );
  }

  const s = stats.data;
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-4xl font-bold">Review</h1>
        <p className="mt-2 text-lg text-ink-soft">
          {s.total === 0
            ? "Flashcards you make from any lecture show up here when they're due."
            : `${s.learned} of ${s.total} cards learned across your library.`}
        </p>
      </div>

      {finished !== null && (
        <p className="rounded-2xl bg-sea-wash px-4 py-3">Nice work: {finished} review{finished === 1 ? "" : "s"} done. Kuki will bring each card back just before you'd forget it.</p>
      )}

      {s.total === 0 ? (
        <Empty title="No flashcards yet" action={<Link to="/" className="font-bold text-whale-deep underline">Open a lecture to make some</Link>} />
      ) : due.data.length === 0 ? (
        <Empty title="All caught up">Nothing is due right now. Come back tomorrow.</Empty>
      ) : (
        <div className="flex flex-col items-start gap-3 rounded-3xl bg-paper p-6">
          <p className="font-display text-3xl font-semibold">{due.data.length} card{due.data.length === 1 ? "" : "s"} due</p>
          <p className="text-ink-soft">A few minutes now saves hours of re-reading later.</p>
          <Button variant="primary" onClick={() => setSession(true)}>Start review</Button>
        </div>
      )}
    </div>
  );
}
