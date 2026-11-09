// One document's workspace: study pack, quiz, flashcards, ask, and the
// original text, as tabs that live in the URL (/doc/:id/:tab).
import { useState } from "react";
import { NavLink, useNavigate, useParams } from "react-router-dom";
import { api, type KukiDocument } from "../api";
import { KindIcon } from "../components/KindIcon";
import { LectureAudio } from "../components/LectureAudio";
import { Button, ErrorNote, Working } from "../components/ui";
import { KIND_LABEL, partsLabel } from "../lib/format";
import { usePageTitle } from "../lib/usePageTitle";
import { useResource } from "../lib/useResource";

const TABS = [
  { id: "pack", label: "Study pack" },
  { id: "quiz", label: "Quiz me" },
  { id: "cards", label: "Flashcards" },
  { id: "ask", label: "Ask" },
  { id: "source", label: "Original" },
] as const;

export type TabId = (typeof TABS)[number]["id"];

const poll = (doc?: KukiDocument) => (doc?.status === "processing" ? 1500 : null);

export default function DocumentPage({ panels }: { panels: Record<TabId, (doc: KukiDocument) => React.ReactNode> }) {
  const { id = "", tab = "pack" } = useParams();
  const doc = useResource(() => api.documents.get(id), [id], poll);
  const active = (TABS.some((t) => t.id === tab) ? tab : "pack") as TabId;
  usePageTitle(doc.data?.title);

  if (doc.error) return <ErrorNote message={doc.error} onRetry={doc.reload} />;
  if (!doc.data) return null;
  const d = doc.data;

  return (
    <div className="space-y-6">
      <DocumentHeader doc={d} onChange={doc.setData} />
      {d.status === "processing" && <Working label="Reading your document…" />}
      {d.status === "failed" && <ErrorNote message={d.error ?? "This file couldn't be read."} />}
      {d.status === "ready" && (
        <>
          <nav aria-label="Study modes" className="-mx-1 flex gap-1 overflow-x-auto px-1">
            {TABS.map((t) => (
              <NavLink
                key={t.id}
                to={`/doc/${d.id}/${t.id}`}
                className={() =>
                  `shrink-0 rounded-full px-4 py-2 font-bold transition-colors ${
                    active === t.id ? "bg-ink text-paper" : "text-ink-soft hover:bg-paper hover:text-ink"
                  }`
                }
              >
                {t.label}
              </NavLink>
            ))}
          </nav>
          <div key={active}>{panels[active](d)}</div>
        </>
      )}
    </div>
  );
}

function DocumentHeader({ doc, onChange }: { doc: KukiDocument; onChange: (d: KukiDocument) => void }) {
  const navigate = useNavigate();
  const [confirming, setConfirming] = useState(false);
  const [busy, setBusy] = useState(false);

  async function remove() {
    setBusy(true);
    await api.documents.remove(doc.id).catch(() => setBusy(false));
    navigate("/");
  }

  return (
    <header className="flex flex-wrap items-start gap-4">
      <span aria-hidden className="grid h-14 w-14 shrink-0 place-items-center rounded-2xl bg-whale-wash text-whale-deep">
        <KindIcon kind={doc.kind} className="h-7 w-7" />
      </span>
      <div className="min-w-0 flex-1">
        <EditableTitle doc={doc} onChange={onChange} />
        <p className="mt-1 text-ink-soft">
          {KIND_LABEL[doc.kind]}
          {doc.status === "ready" && `, ${partsLabel(doc.kind, doc.segment_count)}`}
        </p>
        {doc.attribution && (
          <p className="mt-2 max-w-2xl text-sm text-ink-soft">
            {doc.attribution}{" "}
            {doc.source_url && <a href={doc.source_url} target="_blank" rel="noreferrer" className="underline">Original</a>}
          </p>
        )}
        <LectureAudio doc={doc} onChange={onChange} />
      </div>
      <div className="flex gap-2">
        {confirming ? (
          <>
            <Button variant="danger" busy={busy} onClick={remove}>Delete for good</Button>
            <Button onClick={() => setConfirming(false)}>Keep it</Button>
          </>
        ) : (
          <Button variant="danger" onClick={() => setConfirming(true)}>Delete</Button>
        )}
      </div>
    </header>
  );
}

/** Click the title to rename; Enter saves, Escape cancels. */
function EditableTitle({ doc, onChange }: { doc: KukiDocument; onChange: (d: KukiDocument) => void }) {
  const [editing, setEditing] = useState(false);
  const [value, setValue] = useState(doc.title);

  async function save() {
    setEditing(false);
    if (value.trim() && value.trim() !== doc.title) {
      onChange(await api.documents.rename(doc.id, value).catch(() => doc));
    } else {
      setValue(doc.title);
    }
  }

  if (editing) {
    return (
      <input
        autoFocus
        aria-label="Document title"
        value={value}
        maxLength={200}
        onChange={(e) => setValue(e.target.value)}
        onBlur={() => void save()}
        onKeyDown={(e) => {
          if (e.key === "Enter") void save();
          if (e.key === "Escape") { setValue(doc.title); setEditing(false); }
        }}
        className="w-full rounded-xl border border-whale bg-paper px-2 font-display text-3xl font-bold outline-none sm:text-4xl"
      />
    );
  }
  return (
    <h1 className="text-3xl font-bold sm:text-4xl">
      <button type="button" onClick={() => setEditing(true)} title="Rename" className="text-left hover:underline hover:decoration-stitch hover:decoration-dashed">
        {doc.title}
      </button>
    </h1>
  );
}
