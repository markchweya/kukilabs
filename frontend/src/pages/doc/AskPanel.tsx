// Ask questions about this lecture. Answers come only from the student's
// material and cite where they came from; "not in your notes" is a valid answer.
import { useRef, useState } from "react";
import { api, type Answer, type KukiDocument } from "../../api";
import { Citations } from "../../components/sources";
import { Button, ErrorNote, Spinner } from "../../components/ui";

const STARTERS = ["What's the main idea of this lecture?", "What's likely to come up in an exam?", "Explain the hardest part simply."];

export function AskPanel({ doc }: { doc: KukiDocument }) {
  const [thread, setThread] = useState<Answer[]>([]);
  const [question, setQuestion] = useState("");
  const [pending, setPending] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  async function ask(q: string) {
    const text = q.trim();
    if (!text || pending) return;
    setPending(text);
    setQuestion("");
    setError(null);
    try {
      const answer = await api.ask(text, [doc.id]);
      setThread((t) => [...t, answer]);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setQuestion(text);
    } finally {
      setPending(null);
      inputRef.current?.focus();
    }
  }

  return (
    <div className="mx-auto max-w-3xl space-y-5">
      {thread.length === 0 && !pending && (
        <div className="flex flex-wrap gap-2">
          {STARTERS.map((s) => (
            <button key={s} type="button" onClick={() => void ask(s)} className="rounded-full border border-line bg-paper px-4 py-2 text-sm hover:border-whale">
              {s}
            </button>
          ))}
        </div>
      )}

      <ol className="space-y-5" aria-live="polite">
        {thread.map((a, i) => (
          <li key={i} className="space-y-2">
            <p className="ml-auto w-fit max-w-[85%] rounded-2xl rounded-br-md bg-whale px-4 py-2 text-white dark:text-tide">{a.question}</p>
            <div className={`max-w-[92%] rounded-2xl rounded-bl-md px-4 py-3 ${a.found ? "bg-paper" : "bg-sun-wash"}`}>
              <p className="whitespace-pre-line">{a.answer}</p>
              {a.citations.length > 0 && <div className="mt-2"><Citations items={a.citations} /></div>}
            </div>
          </li>
        ))}
        {pending && (
          <li className="space-y-2">
            <p className="ml-auto w-fit max-w-[85%] rounded-2xl rounded-br-md bg-whale px-4 py-2 text-white dark:text-tide">{pending}</p>
            <p className="flex items-center gap-2 text-ink-soft"><Spinner /> Looking through your notes…</p>
          </li>
        )}
      </ol>

      {error && <ErrorNote message={error} />}

      <form onSubmit={(e) => { e.preventDefault(); void ask(question); }} className="flex gap-2">
        <label htmlFor="ask" className="sr-only">Ask about this lecture</label>
        <input
          id="ask"
          ref={inputRef}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          maxLength={1000}
          placeholder="Ask about this lecture…"
          className="min-w-0 flex-1 rounded-full border border-line bg-paper px-5 py-2.5 outline-none focus:border-whale"
        />
        <Button type="submit" variant="primary" disabled={!question.trim() || !!pending}>Ask</Button>
      </form>
    </div>
  );
}
