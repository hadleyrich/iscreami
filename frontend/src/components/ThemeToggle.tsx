import { Monitor, Moon, Sun } from "lucide-react";
import type { Theme } from "../hooks/useTheme";

interface Props {
  readonly theme: Theme;
  readonly setTheme: (t: Theme) => void;
}

const options: { value: Theme; Icon: React.ComponentType<{ size?: number }>; label: string }[] = [
  { value: "light", Icon: Sun, label: "Light" },
  { value: "system", Icon: Monitor, label: "System" },
  { value: "dark", Icon: Moon, label: "Dark" },
];

export function ThemeToggle({ theme, setTheme }: Props) {
  return (
    <div className="join">
      {options.map(({ value, Icon, label }) => (
        <button
          key={value}
          type="button"
          onClick={() => setTheme(value)}
          title={label}
          aria-label={label}
          aria-pressed={theme === value}
          className={`join-item btn btn-sm ${
            theme === value ? "btn-primary" : "btn-ghost"
          }`}
        >
          <Icon size={14} />
        </button>
      ))}
    </div>
  );
}
