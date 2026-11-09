import { createContext, useContext } from "react";
import type { Citation } from "../api";

/** Opens the source drawer for a citation. Provided by <SourceProvider>. */
export const SourceContext = createContext<(c: Citation) => void>(() => {});

export function useOpenSource() {
  return useContext(SourceContext);
}
