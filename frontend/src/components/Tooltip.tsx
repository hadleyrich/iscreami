import type { ReactNode } from "react";

interface TooltipProps {
  readonly content: string;
  readonly children: ReactNode;
  readonly position?: "top" | "bottom" | "left" | "right";
}

/**
 * Tooltip component using DaisyUI's @tooltip directive.
 * Displays helpful information on hover/focus.
 *
 * @param content - The tooltip text to display
 * @param children - The element that triggers the tooltip
 * @param position - Where to position the tooltip (default: top)
 */
export function Tooltip({ content, children, position = "top" }: TooltipProps) {
  const positionClass = {
    top: "tooltip-top",
    bottom: "tooltip-bottom",
    left: "tooltip-left",
    right: "tooltip-right",
  }[position];

  return (
    <div className={`tooltip ${positionClass}`} data-tip={content}>
      {children}
    </div>
  );
}
