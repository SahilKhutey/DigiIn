import React, { useEffect } from "react";
import { IconButton } from "./IconButton";

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  description?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  maxWidth?: "sm" | "md" | "lg" | "xl";
}

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  description,
  children,
  footer,
  maxWidth = "md",
}) => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const maxWidthStyles = {
    sm: "max-w-sm",
    md: "max-w-md",
    lg: "max-w-lg",
    xl: "max-w-2xl",
  }[maxWidth];

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs"
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      aria-describedby={description ? "modal-desc" : undefined}
    >
      <div className={`w-full ${maxWidthStyles} bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden`}>
        <div className="flex items-start justify-between p-6 border-b border-slate-200">
          <div>
            <h3 id="modal-title" className="text-xl font-bold text-[#092F4F] m-0">
              {title}
            </h3>
            {description && (
              <p id="modal-desc" className="text-xs text-slate-500 mt-1 mb-0">
                {description}
              </p>
            )}
          </div>
          <IconButton
            icon="✕"
            label="Close dialog"
            size="sm"
            onClick={onClose}
          />
        </div>

        <div className="p-6 max-h-[70vh] overflow-y-auto">
          {children}
        </div>

        {footer && (
          <div className="flex items-center justify-end gap-3 p-4 bg-slate-50 border-t border-slate-200">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
};
