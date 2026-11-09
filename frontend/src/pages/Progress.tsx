// Weak spots: the concepts a student keeps missing, weakest first, plus the
// kinds of mistakes they tend to make. Built from every quiz attempt.
import { Link } from "react-router-dom";
import { api, type ConceptProgress, type MisconceptionType } from "../api";
import { Empty, ErrorNote } from "../components/ui";
import { MISCONCEPTION_LABEL } from "../lib/misconceptions";
import { useResource } from "../lib/useResource";

const STATUS = {
  weak: { label: "Needs work", tone: "bg-blush-wash text-blush" },
  improving: { label: "Improving", tone: "bg-sun-wash text-sun" },
  mastered: { label: "Got it", tone: "bg-sea-wash text-sea" },
} as const;

const PATTERN_TIPS: Partial<Record<MisconceptionType, string>> = {
  confused_concepts: "Try writing two similar ideas side by side and listing one difference.",
  missing_step: "When you explain, say each step out loud, even the obvious ones.",
  overgeneralization: "Ask yourself: is this always true, or only in the case from the lecture?",
  vague: "Use one concrete example in every answer.",
  factual_error: "Check the cited slide before your next quiz.",
};

export default function Progress() {
  const insights = useResource(() => api.insights(), []);
  if (insights.error) return <ErrorNote message={insights.error} onRetry={insights.reload} />;
  if (!insights.data) return null;
  const { concepts, mistake_patterns, total_attempts } = insights.data;
  const topPattern = Object.keys(mistake_patterns)[0] as MisconceptionType | undefined;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-4xl font-bold">Weak spots</h1>
        <p className="mt-2 text-lg text-ink-soft">What to revise next, from {total_attempts} quiz answer{total_attempts === 1 ? "" : "s"}.</p>
      </div>

      {concepts.length === 0 ? (
        <Empty title="Take a quiz to find your weak spots" action={<Link to="/" className="font-bold text-whale-deep underline">Choose a lecture</Link>}>
          Every answer you give in "Quiz me" teaches Kuki which ideas you've got and which keep tripping you up.
        </Empty>
      ) : (
        <>
          {topPattern && (
            <section className="rounded-3xl bg-whale-wash p-6">
              <h2 className="text-2xl font-semibold">Your most common snag: {MISCONCEPTION_LABEL[topPattern].toLowerCase()}</h2>
              <p className="mt-2">{PATTERN_TIPS[topPattern] ?? "Look back at the cited slides for the concepts below."}</p>
              <p className="mt-3 text-sm text-ink-soft">
                {Object.entries(mistake_patterns)
                  .map(([k, n]) => `${MISCONCEPTION_LABEL[k as MisconceptionType]}: ${n}`)
                  .join(", ")}
              </p>
            </section>
          )}
          <ul className="divide-y divide-line overflow-hidden rounded-3xl border border-line bg-paper">
            {concepts.map((c) => <ConceptRow key={`${c.document_id}:${c.concept}`} c={c} />)}
          </ul>
        </>
      )}
    </div>
  );
}

function ConceptRow({ c }: { c: ConceptProgress }) {
  const status = STATUS[c.status];
  return (
    <li className="grid gap-2 px-5 py-4 sm:grid-cols-[1fr_auto] sm:items-center">
      <div className="min-w-0">
        <div className="flex flex-wrap items-center gap-2">
          <p className="font-display text-lg font-semibold">{c.concept}</p>
          <span className={`rounded-full px-2.5 py-0.5 text-xs font-bold ${status.tone}`}>{status.label}</span>
        </div>
        {c.latest_misconception && c.status !== "mastered" && <p className="mt-1 text-ink-soft">{c.latest_misconception}</p>}
        <p className="mt-1 text-sm text-ink-soft">
          {c.document_title} · latest {c.latest_score}, best {c.best_score}, {c.attempts} attempt{c.attempts === 1 ? "" : "s"}
        </p>
      </div>
      <Link to={`/doc/${c.document_id}/quiz`} className="justify-self-start rounded-full border border-line px-4 py-2 text-sm font-bold hover:border-whale sm:justify-self-end">
        Practise
      </Link>
    </li>
  );
}
