import {
  createContext,
  useCallback,
  useMemo,
  useRef,
  useState,
} from "react";
import { createPortal } from "react-dom";
import { X } from "lucide-react";

type ToastType = "error" | "warning" | "info" | "success";

interface Toast {
  id: number;
  message: string;
  type: ToastType;
  dismissing?: boolean;
}

export interface ToastContextValue {
  addToast: (message: string, type?: ToastType) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

const ALERT_CLASS: Record<ToastType, string> = {
  error: "alert-error",
  warning: "alert-warning",
  info: "alert-info",
  success: "alert-success",
};

let nextId = 0;

export function ToastProvider({ children }: Readonly<{ children: React.ReactNode }>) {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const timersRef = useRef<Map<number, ReturnType<typeof setTimeout>>>(new Map());

  const removeToast = useCallback((id: number) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const dismiss = useCallback((id: number) => {
    const timer = timersRef.current.get(id);
    if (timer) {
      clearTimeout(timer);
      timersRef.current.delete(id);
    }
    setToasts((prev) =>
      prev.map((t) => (t.id === id ? { ...t, dismissing: true } : t))
    );
    setTimeout(removeToast, 200, id);
  }, [removeToast]);

  const addToast = useCallback(
    (message: string, type: ToastType = "error") => {
      const id = ++nextId;
      setToasts((prev) => [...prev, { id, message, type }]);
      const timer = setTimeout(() => dismiss(id), 5000);
      timersRef.current.set(id, timer);
    },
    [dismiss]
  );

  return (
    <ToastContext.Provider value={useMemo(() => ({ addToast }), [addToast])}>
      {children}
      {createPortal(
        <div className="toast toast-top toast-end z-9999">
          {toasts.map((t) => (
            <div
              key={t.id}
              role="alert"
              className={`alert ${ALERT_CLASS[t.type]} flex items-start gap-3 shadow-lg`}
              style={{
                animation: t.dismissing
                  ? "toast-out 0.2s ease-in forwards"
                  : "toast-in 0.25s ease-out",
              }}
            >
              <span className="text-sm flex-1">{t.message}</span>
              <button
                type="button"
                aria-label="Dismiss"
                onClick={() => dismiss(t.id)}
              >
                <X size={14} />
              </button>
            </div>
          ))}
        </div>,
        document.body
      )}
    </ToastContext.Provider>
  );
}

export { ToastContext };
