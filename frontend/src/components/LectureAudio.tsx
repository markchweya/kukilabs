// Plays an imported lecture's recording: from this computer once saved,
// otherwise streamed from the university with an option to save it.
import { useState } from "react";
import { api, type KukiDocument } from "../api";
import { Button } from "./ui";

export function LectureAudio({ doc, onChange }: { doc: KukiDocument; onChange: (d: KukiDocument) => void }) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  if (!doc.audio_url) return null;

  async function save() {
    setBusy(true);
    setError(null);
    try {
      onChange(await api.documents.saveAudio(doc.id));
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  const src = doc.has_local_audio ? api.documents.localAudioUrl(doc.id) : doc.audio_url;
  return (
    <div className="mt-3 flex flex-wrap items-center gap-3">
      <audio key={src} controls preload="none" src={src} className="w-full max-w-md">
        <a href={src}>Lecture recording</a>
      </audio>
      {doc.has_local_audio ? (
        <span className="text-sm text-sea">Saved on this computer</span>
      ) : (
        <Button busy={busy} onClick={save}>Save for offline</Button>
      )}
      {error && <p className="w-full text-sm text-blush">{error}</p>}
    </div>
  );
}
