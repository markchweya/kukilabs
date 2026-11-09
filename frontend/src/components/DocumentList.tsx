import { Link } from "react-router-dom";
import type { KukiDocument } from "../api";
import { KIND_LABEL, partsLabel } from "../lib/format";
import { Spinner } from "./ui";

export function DocumentList({ docs }: { docs: KukiDocument[] }) {
  return (
    <ul className="divide-y divide-line overflow-hidden rounded-3xl border border-line bg-paper">
      {docs.map((doc) => (
        <li key={doc.id}>
          <Link to={`/doc/${doc.id}`} className="flex items-center gap-4 px-5 py-4 transition-colors hover:bg-tide/60">
            <KindBadge doc={doc} />
            <div className="min-w-0 flex-1">
              <p className="truncate font-bold">{doc.title}</p>
              <p className="truncate text-sm text-ink-soft">
                {doc.status === "processing" && <span className="inline-flex items-center gap-1.5"><Spinner /> Reading…</span>}
                {doc.status === "failed" && <span className="text-blush">{doc.error}</span>}
                {doc.status === "ready" && (
                  <>
                    {KIND_LABEL[doc.kind]}, {partsLabel(doc.kind, doc.segment_count)}
                    {doc.license && <> · {doc.license}</>}
                  </>
                )}
              </p>
            </div>
          </Link>
        </li>
      ))}
    </ul>
  );
}

function KindBadge({ doc }: { doc: KukiDocument }) {
  const tone = doc.status === "failed" ? "bg-blush-wash text-blush" : doc.kind === "web" ? "bg-sea-wash text-sea" : "bg-whale-wash text-whale-deep";
  return (
    <span aria-hidden className={`grid h-11 w-11 shrink-0 place-items-center rounded-2xl font-display text-sm font-bold ${tone}`}>
      {KIND_LABEL[doc.kind].slice(0, 2)}
    </span>
  );
}
