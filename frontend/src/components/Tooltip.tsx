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
 * A visually-hidden `<span>` makes the tooltip content available to screen
 * readers (DaisyUI's `data-tip` renders via CSS pseudo-elements which are not
 * exposed to assistive technology).
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
      <span className="sr-only">{content}</span>
    </div>
  );
}
