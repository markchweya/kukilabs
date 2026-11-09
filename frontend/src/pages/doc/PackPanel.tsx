import { useState } from "react";
import { api, ApiError, type Knowledge, type KukiDocument, type StudyPack } from "../../api";
import { Citations } from "../../components/sources";
import { Button, Empty, ErrorNote, Working } from "../../components/ui";
import { useResource } from "../../lib/useResource";

/** Loads the saved pack; "not generated yet" is a normal state, not an error. */
function loadPack(docId: string): Promise<StudyPack | null> {
  return api.pack.get(docId).catch((e) => {
    if (e instanceof ApiError && e.status === 404) return null;
    throw e;
  });
}

export function PackPanel({ doc }: { doc: KukiDocument }) {
  const pack = useResource(() => loadPack(doc.id), [doc.id]);
  const [knowledge, setKnowledge] = useState<Knowledge>("notes_only");
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function generate() {
    setGenerating(true);
    setError(null);
    try {
      pack.setData(await api.pack.generate(doc.id, knowledge));
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setGenerating(false);
    }
  }

  if (generating) return <Working label="Writing your study pack…" />;
  if (pack.error) return <ErrorNote message={pack.error} onRetry={pack.reload} />;
  if (pack.data === undefined) return null;

  const controls = (
    <div className="flex flex-wrap items-center gap-3">
      <KnowledgeToggle value={knowledge} onChange={setKnowledge} />
      <Button variant="primary" onClick={generate}>{pack.data ? "Rewrite pack" : "Make study pack"}</Button>
    </div>
  );

  if (pack.data === null) {
    return (
      <div className="space-y-4">
        {error && <ErrorNote message={error} />}
        <Empty title="Turn this into a study pack" action={controls}>
          Key concepts, main points, examples and common mistakes, each linked to the slide or page it came from.
        </Empty>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {error && <ErrorNote message={error} />}
      <PackView pack={pack.data} />
      <footer className="flex flex-wrap items-center justify-between gap-3 border-t border-line pt-5">
        {controls}
        <div className="flex gap-4">
          <button type="button" onClick={() => window.print()} className="font-bold text-whale-deep underline">Print</button>
          <a href={api.pack.markdownUrl(doc.id)} className="font-bold text-whale-deep underline">Download as Markdown</a>
        </div>
      </footer>
    </div>
  );
}

function KnowledgeToggle({ value, onChange }: { value: Knowledge; onChange: (k: Knowledge) => void }) {
  const options: { id: Knowledge; label: string; hint: string }[] = [
    { id: "notes_only", label: "Only my notes", hint: "Nothing that isn't in your material" },
    { id: "fill_gaps", label: "Fill gaps", hint: "Kuki may add missing steps, clearly marked" },
  ];
  return (
    <div role="radiogroup" aria-label="What Kuki may use" className="inline-flex rounded-full border border-line bg-paper p-1">
      {options.map((o) => (
        <button
          key={o.id}
          type="button"
          role="radio"
          aria-checked={value === o.id}
          title={o.hint}
          onClick={() => onChange(o.id)}
          className={`rounded-full px-3 py-1 text-sm font-bold ${value === o.id ? "bg-whale-wash text-whale-deep" : "text-ink-soft"}`}
        >
          {o.label}
        </button>
      ))}
    </div>
  );
}

function PackView({ pack }: { pack: StudyPack }) {
  return (
    <article className="space-y-8">
      {pack.notice && <p className="rounded-2xl bg-sun-wash px-4 py-3 text-sm">{pack.notice}</p>}
      <div className="max-w-3xl">
        <h2 className="text-3xl font-bold">{pack.title}</h2>
        {pack.overview && <p className="mt-2 text-lg text-ink-soft">{pack.overview}</p>}
      </div>

      {pack.concepts.length > 0 && (
        <Section title="Key concepts">
          <dl className="grid gap-x-8 gap-y-5 sm:grid-cols-2">
            {pack.concepts.map((c) => (
              <div key={c.term}>
                <dt className="font-display text-lg font-semibold">{c.term}</dt>
                <dd className="mt-0.5">{c.explanation}</dd>
                <dd className="mt-1.5"><Citations items={c.citations} /></dd>
              </div>
            ))}
          </dl>
        </Section>
      )}

      {pack.key_points.length > 0 && (
        <Section title="Main points">
          <ul className="space-y-3">
            {pack.key_points.map((p) => (
              <li key={p.point} className="flex gap-3">
                <span aria-hidden className="mt-2.5 h-2 w-2 shrink-0 rounded-full bg-whale" />
                <div>
                  <p>{p.point}</p>
                  <div className="mt-1"><Citations items={p.citations} /></div>
                </div>
              </li>
            ))}
          </ul>
        </Section>
      )}

      {pack.examples.length > 0 && (
        <Section title="Examples">
          <div className="space-y-4">
            {pack.examples.map((e) => (
              <div key={e.title} className="rounded-2xl bg-paper px-5 py-4">
                <h4 className="font-bold">{e.title}</h4>
                <p className="mt-1">{e.explanation}</p>
                <div className="mt-2"><Citations items={e.citations} /></div>
              </div>
            ))}
          </div>
        </Section>
      )}

      {pack.common_mistakes.length > 0 && (
        <Section title="Common mistakes">
          <ul className="space-y-4">
            {pack.common_mistakes.map((m) => (
              <li key={m.mistake} className="rounded-2xl bg-paper px-5 py-4">
                <p className="text-blush"><span className="font-bold">Mistake: </span>{m.mistake}</p>
                <p className="mt-1"><span className="font-bold text-sea">Actually: </span>{m.correction}</p>
                <div className="mt-2"><Citations items={m.citations} /></div>
              </li>
            ))}
          </ul>
        </Section>
      )}

      <p className="text-sm text-ink-soft">
        {pack.mode === "ai" ? `Written by ${pack.model} on this computer.` : "Copied from your notes without AI."}{" "}
        {pack.knowledge === "fill_gaps" && "Items marked “Not from your notes” were added by Kuki; check them."}
      </p>
    </article>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section>
      <h3 className="mb-4 text-2xl font-semibold">{title}</h3>
      {children}
    </section>
  );
}
