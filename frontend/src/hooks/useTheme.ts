import { useEffect, useState } from "react";

export type Theme = "system" | "light" | "dark";

function resolveAndApply(theme: Theme) {
    const prefersDark = globalThis.matchMedia("(prefers-color-scheme: dark)").matches;
    const dark = theme === "dark" || (theme === "system" && prefersDark);
    document.documentElement.classList.toggle("dark", dark);
    document.documentElement.dataset.theme = dark ? "dark" : "light";
}

export function useTheme() {
    const [theme, setTheme] = useState<Theme>(() => {
        const stored = localStorage.getItem("theme");
        return (stored === "light" || stored === "dark" || stored === "system") ? stored : "system";
    });

    useEffect(() => {
        localStorage.setItem("theme", theme);
        resolveAndApply(theme);
    }, [theme]);

    // Track system preference changes while in system mode
    useEffect(() => {
        if (theme !== "system") return;
        const mq = globalThis.matchMedia("(prefers-color-scheme: dark)");
        const handler = () => resolveAndApply("system");
        mq.addEventListener("change", handler);
        return () => mq.removeEventListener("change", handler);
    }, [theme]);

    return { theme, setTheme };
}
