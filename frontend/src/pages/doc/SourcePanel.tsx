import { api, type KukiDocument } from "../../api";
import { ErrorNote } from "../../components/ui";
import { useResource } from "../../lib/useResource";

/** The extracted text, exactly as Kuki sees it, so students can check the reading. */
export function SourcePanel({ doc }: { doc: KukiDocument }) {
  const segments = useResource(() => api.documents.segments(doc.id), [doc.id]);
  if (segments.error) return <ErrorNote message={segments.error} onRetry={segments.reload} />;
  return (
    <div className="space-y-3">
      <p className="text-ink-soft">This is the text Kuki read from your file. Study packs and quizzes only use what's here.</p>
      {segments.data?.map((s) => (
        <section key={s.id} className="rounded-2xl bg-paper px-5 py-4">
          <h3 className="mb-1 font-sans text-sm font-bold text-ink-soft">{s.locator}</h3>
          <p className="whitespace-pre-line">{s.text}</p>
        </section>
      ))}
    </div>
  );
}
