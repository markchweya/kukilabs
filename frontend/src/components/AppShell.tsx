// Layout: a navigation rail on wide screens, a bottom tab bar on phones.
import { NavLink, Outlet } from "react-router-dom";
import { StatusPill } from "./StatusPill";

const NAV = [
  { to: "/", label: "Library", end: true },
  { to: "/review", label: "Review" },
  { to: "/progress", label: "Weak spots" },
  { to: "/courses", label: "Open courses" },
];

export function AppShell() {
  return (
    <div className="min-h-dvh md:grid md:grid-cols-[15rem_1fr]">
      <a href="#main" className="sr-only focus:not-sr-only focus:absolute focus:left-3 focus:top-3 focus:z-50 focus:rounded-full focus:bg-paper focus:px-4 focus:py-2">
        Skip to content
      </a>

      <aside className="hidden border-r border-line bg-paper/60 md:flex md:flex-col md:gap-6 md:px-4 md:py-6">
        <Brand />
        <nav aria-label="Main" className="flex flex-col gap-1">
          {NAV.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `rounded-xl px-3 py-2 font-bold transition-colors ${isActive ? "bg-whale-wash text-whale-deep" : "text-ink-soft hover:text-ink"}`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="mt-auto">
          <StatusPill />
        </div>
      </aside>

      <header className="flex items-center justify-between gap-3 border-b border-line bg-paper/70 px-4 py-3 md:hidden">
        <Brand />
        <div className="w-36">
          <StatusPill />
        </div>
      </header>

      <main id="main" className="mx-auto w-full max-w-5xl px-4 pb-28 pt-6 sm:px-8 md:pb-12 md:pt-10">
        <Outlet />
      </main>

      <nav aria-label="Main" className="fixed inset-x-0 bottom-0 z-20 grid grid-cols-4 border-t border-line bg-paper md:hidden">
        {NAV.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            className={({ isActive }) => `px-1 py-3 text-center text-xs font-bold ${isActive ? "text-whale-deep" : "text-ink-soft"}`}
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </div>
  );
}

function Brand() {
  return (
    <NavLink to="/" className="flex items-center gap-2.5">
      <img src="/kuki.svg" alt="" className="h-10 w-10" />
      <span className="font-display text-2xl font-bold tracking-tight">Kuki</span>
    </NavLink>
  );
}
