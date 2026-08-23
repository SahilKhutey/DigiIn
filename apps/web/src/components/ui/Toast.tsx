import React, { createContext, useContext, useState, useCallback } from "react";

export type ToastType = "success" | "info" | "warning" | "error";

export interface ToastMessage {
  id: string;
  type: ToastType;
  title: string;
  message?: string;
  duration?: number;
}

interface ToastContextType {
  showToast: (type: ToastType, title: string, message?: string, duration?: number) => void;
  dismissToast: (id: string) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  const dismissToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const showToast = useCallback((type: ToastType, title: string, message?: string, duration = 4000) => {
    const id = `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const newToast: ToastMessage = { id, type, title, message, duration };

    setToasts((prev) => [...prev, newToast]);

    if (duration > 0) {
      setTimeout(() => {
        dismissToast(id);
      }, duration);
    }
  }, [dismissToast]);

  return (
    <ToastContext.Provider value={{ showToast, dismissToast }}>
      {children}
      {/* Toast Notification Container */}
      <div
        className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-sm w-full pointer-events-none"
        aria-live="polite"
      >
        {toasts.map((toast) => {
          const typeStyles = {
            success: "bg-[#DFF6E8] border-[#86EFAC] text-[#14743F]",
            info: "bg-[#E6F4F8] border-[#BAE6FD] text-[#0A6990]",
            warning: "bg-[#FFF0CC] border-[#FDE68A] text-[#744B00]",
            error: "bg-[#FEE2E2] border-[#FCA5A5] text-[#991B1B]",
          }[toast.type];

          const icon = {
            success: "✓",
            info: "ℹ",
            warning: "⚠",
            error: "✕",
          }[toast.type];

          return (
            <div
              key={toast.id}
              role="alert"
              className={`p-4 rounded-xl border shadow-lg pointer-events-auto flex items-start gap-3 transition-all animate-bounce-short ${typeStyles}`}
            >
              <span className="font-bold text-base shrink-0" aria-hidden="true">{icon}</span>
              <div className="flex-1">
                <strong className="text-sm font-bold block">{toast.title}</strong>
                {toast.message && <p className="text-xs text-slate-700 mt-0.5 mb-0">{toast.message}</p>}
              </div>
              <button
                type="button"
                onClick={() => dismissToast(toast.id)}
                className="text-slate-400 hover:text-slate-700 font-bold text-xs p-1"
                aria-label="Dismiss toast"
              >
                ✕
              </button>
            </div>
          );
        })}
      </div>
    </ToastContext.Provider>
  );
};

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error("useToast must be used within a ToastProvider");
  }
  return context;
}
