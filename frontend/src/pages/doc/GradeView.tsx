// Feedback on one answer. Leads with what the student got right, then names
// the exact snag, then asks a guiding question. The model answer stays hidden
// until asked for, so the student gets a real chance to fix it themselves.
import { useState } from "react";
import type { Grade } from "../../api";
import { Citations } from "../../components/sources";
import { MISCONCEPTION_LABEL, VERDICT_COPY } from "../../lib/misconceptions";

export function GradeView({ grade }: { grade: Grade }) {
  const [reveal, setReveal] = useState(false);
  const verdict = VERDICT_COPY[grade.verdict];

  return (
    <div className="space-y-4 rounded-3xl bg-paper p-5 sm:p-6" aria-live="polite">
      <div className="flex items-baseline justify-between gap-4">
        <h3 className={`text-2xl font-bold ${verdict.tone}`}>{verdict.title}</h3>
        <ScoreBar score={grade.score} />
      </div>

      {grade.got_right.length > 0 && (
        <div>
          <p className="font-bold text-sea">What you got right</p>
          <ul className="mt-1 list-disc space-y-0.5 pl-5">
            {grade.got_right.map((g) => <li key={g}>{g}</li>)}
          </ul>
        </div>
      )}

      {grade.misconception && (
        <div className="rounded-2xl bg-blush-wash px-4 py-3">
          <p className="font-bold text-blush">The snag: {MISCONCEPTION_LABEL[grade.misconception_type].toLowerCase()}</p>
          <p className="mt-1">{grade.misconception}</p>
        </div>
      )}

      {grade.verdict !== "correct" && grade.nudge && (
        <div className="rounded-2xl bg-whale-wash px-4 py-3">
          <p className="font-bold text-whale-deep">Think about this</p>
          <p className="mt-1 font-display text-lg">{grade.nudge}</p>
        </div>
      )}

      {reveal ? (
        <div className="stitched rounded-2xl bg-belly px-5 py-4">
          <p className="font-bold">A strong answer</p>
          <p className="mt-1">{grade.ideal_answer}</p>
          <div className="mt-2"><Citations items={grade.citations} /></div>
        </div>
      ) : (
        <button type="button" onClick={() => setReveal(true)} className="text-sm font-bold text-whale-deep underline">
          Show a strong answer
        </button>
      )}

      {grade.mode === "keyword" && (
        <p className="text-sm text-ink-soft">Kuki's AI was offline, so this was checked by matching key ideas. It can't spot subtle mistakes.</p>
      )}
    </div>
  );
}

function ScoreBar({ score }: { score: number }) {
  const tone = score >= 80 ? "bg-sea" : score >= 40 ? "bg-sun" : "bg-blush";
  return (
    <div className="flex items-center gap-2" aria-label={`Score ${score} out of 100`}>
      <div className="h-2 w-24 overflow-hidden rounded-full bg-tide">
        <div className={`h-full rounded-full ${tone}`} style={{ width: `${score}%` }} />
      </div>
      <span className="text-sm font-bold tabular-nums">{score}</span>
    </div>
  );
}
