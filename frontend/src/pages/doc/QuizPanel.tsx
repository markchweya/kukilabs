// "Quiz me": one question at a time. The student explains in their own words,
// gets diagnosed feedback, and can try again before moving on. Retrying is the
// point: fixing your own misconception is what makes it stick.
import { useState } from "react";
import { Link } from "react-router-dom";
import { api, type Grade, type KukiDocument, type Question } from "../../api";
import { Citations } from "../../components/sources";
import { Button, Empty, ErrorNote, Working } from "../../components/ui";
import { GradeView } from "./GradeView";

export function QuizPanel({ doc }: { doc: KukiDocument }) {
  const [questions, setQuestions] = useState<Question[] | null>(null);
  const [index, setIndex] = useState(0);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function start() {
    setBusy(true);
    setError(null);
    try {
      const qs = await api.quiz.generate(doc.id, 5);
      if (qs.length === 0) throw new Error("Kuki couldn't write questions it could tie to your notes. Try again.");
      setQuestions(qs);
      setIndex(0);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  if (busy) return <Working label="Writing questions about your lecture…" />;

  if (!questions) {
    return (
      <div className="space-y-4">
        {error && <ErrorNote message={error} onRetry={start} />}
        <Empty title="Explain it back to Kuki" action={<Button variant="primary" onClick={start}>Start a 5-question quiz</Button>}>
          No multiple choice. You answer in your own words, and Kuki tells you exactly which idea you're missing or mixing up.
        </Empty>
      </div>
    );
  }

  if (index >= questions.length) {
    return (
      <Empty title="Quiz done" action={<div className="flex gap-2"><Button variant="primary" onClick={start}>New questions</Button><Link to="/progress" className="rounded-full border border-line bg-paper px-4 py-2 font-bold">See weak spots</Link></div>}>
        Kuki saved what you found hard. Your weak spots page shows which ideas to revise next.
      </Empty>
    );
  }

  return (
    <QuestionCard
      key={questions[index].id}
      question={questions[index]}
      position={index + 1}
      total={questions.length}
      onNext={() => setIndex((i) => i + 1)}
    />
  );
}

function QuestionCard({ question, position, total, onNext }: { question: Question; position: number; total: number; onNext: () => void }) {
  const [answer, setAnswer] = useState("");
  const [grade, setGrade] = useState<Grade | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit() {
    setBusy(true);
    setError(null);
    try {
      setGrade(await api.quiz.answer(question.id, answer));
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-5">
      <div>
        <p className="text-sm font-bold text-ink-soft">Question {position} of {total} · {question.concept}</p>
        <h2 className="mt-1 max-w-3xl text-2xl font-semibold sm:text-3xl">{question.prompt}</h2>
        <div className="mt-2"><Citations items={question.citations} /></div>
      </div>

      <form
        onSubmit={(e) => { e.preventDefault(); if (answer.trim()) void submit(); }}
        className="space-y-3"
      >
        <label htmlFor={`answer-${question.id}`} className="sr-only">Your answer</label>
        <textarea
          id={`answer-${question.id}`}
          value={answer}
          onChange={(e) => setAnswer(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter" && (e.metaKey || e.ctrlKey) && answer.trim()) void submit(); }}
          rows={5}
          maxLength={4000}
          placeholder="Explain it as if to a friend who missed the lecture…"
          className="w-full rounded-2xl border border-line bg-paper px-4 py-3 text-[1.05rem] outline-none focus:border-whale"
        />
        <div className="flex flex-wrap items-center gap-2">
          <Button type="submit" variant="primary" busy={busy} disabled={!answer.trim()}>
            {grade ? "Check again" : "Check my answer"}
          </Button>
          <Button onClick={onNext}>{grade ? (position === total ? "Finish" : "Next question") : "Skip"}</Button>
          <span className="hidden text-sm text-ink-soft sm:inline">Ctrl + Enter to check</span>
        </div>
      </form>

      {error && <ErrorNote message={error} />}
      {grade && <GradeView key={grade.attempt_id} grade={grade} />}
    </div>
  );
}
