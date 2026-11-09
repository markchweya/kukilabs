// Shows whether the local AI is available, and opens a setup checklist
// with copyable fix-it commands when something is missing.
import { useState } from "react";
import { api, type Status } from "../api";
import { useResource } from "../lib/useResource";

export function StatusPill() {
  const status = useResource(api.status, [], 30_000);
  const [open, setOpen] = useState(false);
  const s = status.data;
  const tone = !s ? "bg-line" : s.ai_ready ? "bg-sea" : "bg-sun";
  const label = !s ? (status.error ? "Server offline" : "Checking…") : s.ai_ready ? "AI ready" : "AI offline";

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
        className="flex w-full items-center gap-2 rounded-full border border-line bg-paper px-3 py-1.5 text-sm hover:border-whale"
      >
        <span aria-hidden className={`h-2.5 w-2.5 shrink-0 rounded-full ${tone}`} />
        <span className="truncate">{label}</span>
      </button>
      {open && (
        <div className="absolute bottom-full left-0 z-30 mb-2 w-80 max-w-[calc(100vw-2rem)] rounded-2xl border border-line bg-paper p-4 shadow-xl">
          {status.error && <p className="text-sm">{status.error}</p>}
          {s && <Checklist status={s} />}
        </div>
      )}
    </div>
  );
}

function Checklist({ status }: { status: Status }) {
  return (
    <div>
      <p className="mb-3 text-sm text-ink-soft">
        {status.ai_ready
          ? `Everything runs on this computer with ${status.chat_model}.`
          : "Kuki still works without AI: packs are copied from your notes and quizzes use recall. Fix the steps below for full features."}
      </p>
      <ul className="space-y-2.5">
        {Object.entries(status.checks).map(([key, c]) => (
          <li key={key} className="text-sm">
            <div className="flex items-center gap-2">
              <span aria-hidden className={c.ok ? "text-sea" : "text-sun"}>{c.ok ? "●" : "○"}</span>
              <span className="font-bold">{c.label}</span>
            </div>
            <p className="ml-5 text-ink-soft">{c.detail}</p>
            {c.fix && <CopyCommand command={c.fix} />}
          </li>
        ))}
      </ul>
    </div>
  );
}

function CopyCommand({ command }: { command: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <button
      type="button"
      onClick={() => navigator.clipboard?.writeText(command).then(() => setCopied(true))}
      className="ml-5 mt-1 block rounded-lg bg-tide px-2 py-1 text-left font-mono text-xs hover:bg-whale-wash"
      title="Copy command"
    >
      {command} <span className="text-ink-soft">{copied ? "copied" : "copy"}</span>
    </button>
  );
}
