// Search every document at once. Results open the exact passage in the
// source drawer, using the same citation flow as the rest of the app.
import { useEffect, useState } from "react";
import { api, type SearchHit } from "../api";
import { useOpenSource } from "../lib/sourceContext";

export function LibrarySearch() {
  const [query, setQuery] = useState("");
  const [hits, setHits] = useState<SearchHit[] | null>(null);
  const openSource = useOpenSource();

  useEffect(() => {
    const q = query.trim();
    if (q.length < 2) { setHits(null); return; }
    // Debounce so typing doesn't fire a search per keystroke.
    const timer = window.setTimeout(() => { api.search(q).then(setHits, () => setHits([])); }, 250);
    return () => window.clearTimeout(timer);
  }, [query]);

  return (
    <div className="relative">
      <label htmlFor="library-search" className="sr-only">Search your notes</label>
      <input
        id="library-search"
        type="search"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search all your notes…"
        className="w-full rounded-full border border-line bg-paper px-5 py-2.5 outline-none focus:border-whale"
      />
      {hits && (
        <ul className="mt-2 divide-y divide-line overflow-hidden rounded-3xl border border-line bg-paper">
          {hits.length === 0 && <li className="px-5 py-4 text-ink-soft">Nothing in your notes matches “{query.trim()}”.</li>}
          {hits.map((h) => (
            <li key={h.segment_id}>
              <button
                type="button"
                onClick={() => openSource({ ...h, excerpt: h.text })}
                className="block w-full px-5 py-3 text-left hover:bg-tide/60"
              >
                <p className="text-sm text-ink-soft">{h.document_title} · {h.locator}</p>
                <p className="line-clamp-2">{h.text}</p>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
