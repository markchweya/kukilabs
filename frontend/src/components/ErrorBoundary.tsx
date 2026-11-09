// Catches render crashes so one broken panel can't blank the whole app.
import { Component, type ReactNode } from "react";

export class ErrorBoundary extends Component<{ children: ReactNode }, { error: Error | null }> {
  state = { error: null as Error | null };

  static getDerivedStateFromError(error: Error) {
    return { error };
  }

  render() {
    if (!this.state.error) return this.props.children;
    return (
      <div role="alert" className="mx-auto mt-16 max-w-md rounded-3xl bg-paper p-8 text-center">
        <img src="/kuki.svg" alt="" className="mx-auto mb-3 h-16 w-16" />
        <h1 className="text-2xl font-semibold">Something broke on this page</h1>
        <p className="mt-2 text-ink-soft">Your notes are safe. Reload to try again.</p>
        <p className="mt-3 font-mono text-xs text-ink-soft">{this.state.error.message}</p>
        <button type="button" onClick={() => location.reload()} className="mt-5 rounded-full bg-whale px-5 py-2 font-bold text-white">
          Reload
        </button>
      </div>
    );
  }
}
