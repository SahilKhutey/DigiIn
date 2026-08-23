import React, { useEffect } from "react";
import { IconButton } from "./IconButton";

export interface DrawerProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  position?: "left" | "right";
}

export const Drawer: React.FC<DrawerProps> = ({
  isOpen,
  onClose,
  title,
  children,
  position = "right",
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

  return (
    <div
      className="fixed inset-0 z-50 flex bg-slate-900/60 backdrop-blur-xs"
      role="dialog"
      aria-modal="true"
      aria-labelledby="drawer-title"
    >
      <div
        className={`fixed top-0 bottom-0 ${
          position === "right" ? "right-0" : "left-0"
        } w-full max-w-md bg-white shadow-2xl flex flex-col`}
      >
        <div className="flex items-center justify-between p-5 border-b border-slate-200">
          <h3 id="drawer-title" className="text-lg font-bold text-[#092F4F] m-0">
            {title}
          </h3>
          <IconButton icon="✕" label="Close drawer" size="sm" onClick={onClose} />
        </div>
        <div className="flex-1 p-6 overflow-y-auto">{children}</div>
      </div>
    </div>
  );
};
