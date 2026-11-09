// Small shared building blocks. Variants are explicit props, not ad-hoc
// classNames, so every button in the app looks like it belongs.
import type { ButtonHTMLAttributes, ReactNode } from "react";

type Variant = "primary" | "quiet" | "danger";

const VARIANTS: Record<Variant, string> = {
  primary: "bg-whale text-white hover:bg-whale-deep dark:text-tide",
  quiet: "bg-paper text-ink border border-line hover:border-whale",
  danger: "bg-paper text-blush border border-line hover:border-blush",
};

export function Button({
  variant = "quiet",
  busy = false,
  className = "",
  children,
  ...rest
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant; busy?: boolean }) {
  return (
    <button
      type="button"
      {...rest}
      disabled={rest.disabled || busy}
      aria-busy={busy || undefined}
      className={`inline-flex items-center justify-center gap-2 rounded-full px-4 py-2 text-[0.94rem] font-bold transition-colors disabled:cursor-not-allowed disabled:opacity-55 ${VARIANTS[variant]} ${className}`}
    >
      {busy && <Spinner />}
      {children}
    </button>
  );
}

export function Spinner() {
  return (
    <span
      aria-hidden
      className="inline-block h-3.5 w-3.5 animate-spin rounded-full border-2 border-current border-r-transparent"
    />
  );
}

/** The whale bobs while the local model works: Kuki's one ambient animation. */
export function Working({ label }: { label: string }) {
  return (
    <div role="status" className="flex flex-col items-center gap-3 py-14 text-center">
      <img src="/kuki.svg" alt="" className="h-20 w-20 motion-safe:animate-[bob_2.4s_ease-in-out_infinite]" />
      <p className="font-display text-lg">{label}</p>
      <p className="max-w-sm text-sm text-ink-soft">This runs on your own computer, so it can take a minute on a laptop.</p>
    </div>
  );
}

export function ErrorNote({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div role="alert" className="flex flex-wrap items-center gap-3 rounded-2xl bg-blush-wash px-4 py-3 text-sm">
      <span className="flex-1">{message}</span>
      {onRetry && <Button onClick={onRetry}>Try again</Button>}
    </div>
  );
}

export function Empty({ title, children, action }: { title: string; children?: ReactNode; action?: ReactNode }) {
  return (
    <div className="flex flex-col items-center gap-2 rounded-3xl border border-line bg-paper px-6 py-12 text-center">
      <img src="/kuki.svg" alt="" className="mb-1 h-14 w-14 opacity-90" />
      <h2 className="text-xl font-semibold">{title}</h2>
      {children && <div className="max-w-md text-ink-soft">{children}</div>}
      {action && <div className="mt-3">{action}</div>}
    </div>
  );
}
