// Drag-and-drop (or click) upload for lecture material. Several files can be
// dropped at once; each uploads independently so one bad file can't block the rest.
import { useRef, useState } from "react";
import { api, type KukiDocument } from "../api";

const ACCEPT = ".pdf,.pptx,.docx,.txt,.md,.png,.jpg,.jpeg,.webp,.mp3,.m4a,.wav,.ogg,.webm,.mp4";

export function DropZone({ onUploaded }: { onUploaded: (doc: KukiDocument) => void }) {
  const input = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState<string[]>([]);
  const [errors, setErrors] = useState<string[]>([]);

  async function upload(files: FileList | File[]) {
    setErrors([]);
    await Promise.all(
      Array.from(files).map(async (file) => {
        setUploading((u) => [...u, file.name]);
        try {
          onUploaded(await api.documents.upload(file));
        } catch (e) {
          setErrors((errs) => [...errs, `${file.name}: ${e instanceof Error ? e.message : e}`]);
        } finally {
          setUploading((u) => u.filter((n) => n !== file.name));
        }
      }),
    );
  }

  return (
    <div>
      <div
        role="button"
        tabIndex={0}
        aria-label="Add lecture material"
        onClick={() => input.current?.click()}
        onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && input.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => { e.preventDefault(); setDragging(false); void upload(e.dataTransfer.files); }}
        className={`stitched relative flex cursor-pointer flex-col items-center gap-2 rounded-[2rem] px-6 py-10 text-center transition-colors sm:py-14 ${
          dragging ? "bg-whale-wash" : "bg-paper hover:bg-belly"
        }`}
      >
        {/* Kuki peeks over the edge, waiting for a lecture. */}
        <img
          src="/kuki.svg"
          alt=""
          className={`pointer-events-none absolute -top-14 right-6 h-24 w-24 transition-transform sm:right-12 sm:h-28 sm:w-28 ${dragging ? "-translate-y-2 rotate-6" : ""}`}
        />
        <p className="font-display text-2xl font-semibold">
          {uploading.length ? `Reading ${uploading.length === 1 ? uploading[0] : `${uploading.length} files`}…` : "Drop your lecture here"}
        </p>
        <p className="max-w-md text-ink-soft">
          Slides, PDFs, Word docs, photos of your notes or a recording. It stays on this computer.
        </p>
        <span className="mt-3 rounded-full bg-whale px-5 py-2 font-bold text-white dark:text-tide">Choose files</span>
      </div>
      <input
        ref={input}
        type="file"
        multiple
        accept={ACCEPT}
        className="hidden"
        onChange={(e) => { if (e.target.files) void upload(e.target.files); e.target.value = ""; }}
      />
      {errors.length > 0 && (
        <ul role="alert" className="mt-3 space-y-1 text-sm text-blush">
          {errors.map((err) => <li key={err}>{err}</li>)}
        </ul>
      )}
    </div>
  );
}
