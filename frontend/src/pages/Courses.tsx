// Open Course Library: free, openly licensed lectures from Harvard and Yale
// that a student can pull into Kuki with one click, credited to their authors.
import { useState } from "react";
import { Link } from "react-router-dom";
import { api, type Course } from "../api";
import { Button, ErrorNote } from "../components/ui";
import { useResource } from "../lib/useResource";

export default function Courses() {
  const courses = useResource(api.courses.list, []);
  if (courses.error) return <ErrorNote message={courses.error} onRetry={courses.reload} />;

  return (
    <div className="space-y-8">
      <div className="max-w-2xl">
        <h1 className="text-4xl font-bold">Open courses</h1>
        <p className="mt-2 text-lg text-ink-soft">
          Free lectures that universities share under Creative Commons. Import one to study it with Kuki; the
          original authors are credited on every page.
        </p>
      </div>
      {courses.data?.map((c) => <CourseBlock key={c.id} course={c} onImported={courses.reload} />)}
      <p className="text-sm text-ink-soft">
        Importing downloads the lecture page once from the university's site. Everything after that happens on your computer.
      </p>
    </div>
  );
}

function CourseBlock({ course, onImported }: { course: Course; onImported: () => void }) {
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const imported = course.lectures.filter((l) => l.document_id).length;

  async function importLecture(n: number) {
    setBusy(n);
    setError(null);
    try {
      await api.courses.importLecture(course.id, n);
      onImported();
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(null);
    }
  }

  return (
    <section className="rounded-3xl border border-line bg-paper">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
        className="flex w-full flex-wrap items-start gap-x-6 gap-y-2 px-6 py-5 text-left"
      >
        <div className="min-w-0 flex-1">
          <p className="text-sm font-bold text-ink-soft">{course.institution} · {course.subject}</p>
          <h2 className="mt-0.5 text-2xl font-semibold">{course.title}</h2>
          <p className="mt-1 text-ink-soft">{course.description}</p>
        </div>
        <span className="rounded-full bg-tide px-3 py-1 text-sm font-bold">
          {imported ? `${imported} of ${course.lectures.length} imported` : `${course.lectures.length} lectures`}
        </span>
      </button>

      {open && (
        <div className="border-t border-line px-6 py-4">
          <p className="mb-3 text-sm text-ink-soft">
            {course.instructor}.{" "}
            <a href={course.license_url} target="_blank" rel="noreferrer" className="underline">{course.license}</a>,{" "}
            <a href={course.homepage} target="_blank" rel="noreferrer" className="underline">course website</a>.
          </p>
          {error && <div className="mb-3"><ErrorNote message={error} /></div>}
          <ol className="divide-y divide-line">
            {course.lectures.map((l) => (
              <li key={l.number} className="flex items-center gap-3 py-2.5">
                <span className="w-8 shrink-0 text-right text-sm tabular-nums text-ink-soft">{l.number}</span>
                <span className="min-w-0 flex-1">{l.title}</span>
                {l.document_id ? (
                  <Link to={`/doc/${l.document_id}`} className="rounded-full bg-sea-wash px-4 py-1.5 text-sm font-bold text-sea">Open</Link>
                ) : (
                  <Button busy={busy === l.number} disabled={busy !== null} onClick={() => void importLecture(l.number)}>Import</Button>
                )}
              </li>
            ))}
          </ol>
        </div>
      )}
    </section>
  );
}
