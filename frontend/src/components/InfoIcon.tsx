import { HelpCircle } from "lucide-react";
import { Tooltip } from "./Tooltip";

interface InfoIconProps {
  readonly label: string;
  readonly position?: "top" | "bottom" | "left" | "right";
  readonly className?: string;
}

/**
 * Info icon component that displays a help circle with tooltip.
 * Use this to provide context about fields, metrics, or concepts in the UI.
 *
 * @param label - The tooltip text to display
 * @param position - Where to position the tooltip (default: top)
 * @param className - Additional CSS classes (default includes sizing)
 */
export function InfoIcon({ label, position = "top", className = "" }: InfoIconProps) {
  return (
    <Tooltip content={label} position={position}>
      <HelpCircle
        className={`w-4 h-4 text-base-content/50 hover:text-base-content/70 cursor-help transition-colors ${className}`}
      />
    </Tooltip>
  );
}
