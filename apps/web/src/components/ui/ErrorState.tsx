import React from "react";
import { Button } from "./Button";

export interface ErrorStateProps {
  title?: string;
  message: string;
  errorCode?: string;
  onRetry?: () => void;
  className?: string;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = "Something went wrong",
  message,
  errorCode,
  onRetry,
  className = "",
}) => {
  return (
    <div
      role="alert"
      className={`p-6 md:p-8 bg-[#FEE2E2]/40 border border-[#FCA5A5] rounded-2xl text-center space-y-4 ${className}`}
    >
      <div className="w-12 h-12 rounded-full bg-[#FEE2E2] text-[#991B1B] text-xl font-bold flex items-center justify-center mx-auto" aria-hidden="true">
        ✕
      </div>
      <div className="space-y-1">
        <h3 className="text-lg font-bold text-[#991B1B] m-0">{title}</h3>
        <p className="text-xs text-slate-700 max-w-md mx-auto m-0 leading-relaxed">
          {message}
        </p>
        {errorCode && (
          <code className="text-[11px] font-mono text-slate-500 block mt-1">
            Reference Code: {errorCode}
          </code>
        )}
      </div>
      {onRetry && (
        <div className="pt-2">
          <Button variant="danger" size="sm" onClick={onRetry}>
            Try Again
          </Button>
        </div>
      )}
    </div>
  );
};
