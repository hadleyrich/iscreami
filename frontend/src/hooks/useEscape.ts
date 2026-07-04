import { useEffect } from "react";

/**
 * Calls `onEscape` when the Escape key is pressed.
 * Only active when `active` is true (default: true).
 *
 * Eliminates the duplicated `useEffect` + keydown listener pattern
 * that previously appeared 9 times across the codebase.
 */
export function useEscape(onEscape: () => void, active = true): void {
  useEffect(() => {
    if (!active) return;
    function onKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") onEscape();
    }
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [onEscape, active]);
}
