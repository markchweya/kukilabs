import { Link } from "react-router-dom";
import { api, type KukiDocument } from "../api";
import { DocumentList } from "../components/DocumentList";
import { DropZone } from "../components/DropZone";
import { LibrarySearch } from "../components/LibrarySearch";
import { Empty, ErrorNote } from "../components/ui";
import { usePageTitle } from "../lib/usePageTitle";
import { useResource } from "../lib/useResource";

// Poll every 1.5 s only while something is still being read.
const pollWhileProcessing = (docs?: KukiDocument[]) =>
  docs?.some((d) => d.status === "processing") ? 1500 : null;

export default function Library() {
  usePageTitle("Library");
  const docs = useResource(api.documents.list, [], pollWhileProcessing);

  return (
    <div className="space-y-10">
      <section className="space-y-6">
        <div className="max-w-2xl">
          <h1 className="text-4xl font-bold sm:text-5xl">Your private AI study buddy.</h1>
          <p className="mt-3 text-lg text-ink-soft">
            Kuki turns lecture slides, notes and recordings into study packs, flashcards and quizzes that find your exact
            misunderstanding. Everything runs on your own computer.
          </p>
        </div>
        <DropZone onUploaded={(doc) => docs.setData([doc, ...(docs.data ?? [])])} />
      </section>

      <section className="space-y-3">
        <h2 className="text-2xl font-semibold">Your library</h2>
        {docs.data && docs.data.some((d) => d.status === "ready") && <LibrarySearch />}
        {docs.error && <ErrorNote message={docs.error} onRetry={docs.reload} />}
        {docs.data && docs.data.length === 0 && (
          <Empty title="Nothing here yet" action={<Link to="/courses" className="font-bold text-whale-deep underline">Browse open courses</Link>}>
            Add your own lecture above, or import a free lecture from Harvard or Yale to try Kuki.
          </Empty>
        )}
        {docs.data && docs.data.length > 0 && <DocumentList docs={docs.data} />}
      </section>
    </div>
  );
}
