import { useEffect } from "react";

/** Set the browser tab title, so screen readers and tab lists say where you are. */
export function usePageTitle(title: string | undefined) {
  useEffect(() => {
    document.title = title ? `${title} · Kuki` : "Kuki";
  }, [title]);
}
