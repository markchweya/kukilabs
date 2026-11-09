// Citations and the source drawer.
//
// Every claim Kuki makes about a student's material carries stitched chips
// pointing at the exact slide, page or timestamp. Tapping one opens the
// drawer with the full original passage, so the student can check Kuki
// instead of having to trust it.
import { createContext, useContext, useEffect, useRef, useState, type ReactNode } from "react";
import { api, type Citation, type Segment } from "../api";
import { Spinner } from "./ui";

const SourceContext = createContext<(c: Citation) => void>(() => {});

export function useOpenSource() {
  return useContext(SourceContext);
}

export function SourceProvider({ children }: { children: ReactNode }) {
  const [open, setOpen] = useState<Citation | null>(null);
  return (
    <SourceContext.Provider value={setOpen}>
      {children}
      {open && <SourceDrawer citation={open} onClose={() => setOpen(null)} />}
    </SourceContext.Provider>
  );
}

export function Citations({ items, ungroundedLabel = "Not from your notes" }: { items: Citation[]; ungroundedLabel?: string }) {
  const openSource = useOpenSource();
  if (items.length === 0) {
    // Deliberately un-stitched: nothing ties this to the student's material.
    return <span className="text-xs text-sun">{ungroundedLabel}</span>;
  }
  return (
    <span className="inline-flex flex-wrap gap-1.5">
      {items.map((c) => (
        <button
          key={c.segment_id}
          type="button"
          onClick={() => openSource(c)}
          title={c.excerpt}
          className="stitched rounded-full bg-belly px-2.5 py-0.5 text-xs text-ink-soft transition-colors hover:border-whale hover:text-ink"
        >
          {c.locator}
        </button>
      ))}
    </span>
  );
}

function SourceDrawer({ citation, onClose }: { citation: Citation; onClose: () => void }) {
  const [segments, setSegments] = useState<Segment[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const activeRef = useRef<HTMLElement>(null);
  const closeRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    setSegments(null);
    api.documents.segments(citation.document_id).then(setSegments, (e) => setError(e.message));
  }, [citation.document_id]);

  useEffect(() => {
    closeRef.current?.focus();
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  useEffect(() => {
    activeRef.current?.scrollIntoView({ block: "center" });
  }, [segments, citation.segment_id]);

  return (
    <div className="fixed inset-0 z-40 flex justify-end" role="dialog" aria-modal="true" aria-label={`Source: ${citation.locator}`}>
      <button type="button" aria-label="Close source" className="absolute inset-0 bg-ink/25" onClick={onClose} />
      <aside className="relative flex h-full w-full max-w-xl flex-col bg-paper shadow-2xl motion-safe:animate-[slide-in_.18s_ease-out]">
        <header className="flex items-start gap-3 border-b border-line px-5 py-4">
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm text-ink-soft">{citation.document_title}</p>
            <h2 className="text-xl font-semibold">{citation.locator}</h2>
          </div>
          <button ref={closeRef} type="button" onClick={onClose} className="rounded-full border border-line px-3 py-1 text-sm hover:border-whale">
            Close
          </button>
        </header>
        <div className="flex-1 overflow-y-auto px-5 py-4">
          {error && <p className="text-blush">{error}</p>}
          {!segments && !error && <p className="flex items-center gap-2 text-ink-soft"><Spinner /> Opening your notes…</p>}
          {segments?.map((s) => {
            const active = s.id === citation.segment_id;
            return (
              <section
                key={s.id}
                ref={active ? activeRef : undefined}
                className={`mb-3 rounded-2xl px-4 py-3 ${active ? "stitched bg-belly" : "opacity-60"}`}
              >
                <p className="mb-1 text-xs text-ink-soft">{s.locator}</p>
                <p className="whitespace-pre-line">{s.text}</p>
              </section>
            );
          })}
        </div>
      </aside>
    </div>
  );
}
