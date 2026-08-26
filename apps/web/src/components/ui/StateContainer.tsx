import React from "react";

export type UIState =
  | "LOADING"
  | "EMPTY"
  | "SUCCESS"
  | "ERROR"
  | "PENDING"
  | "OFFLINE"
  | "UNAUTHORIZED"
  | "EXPIRED";

export interface StateContainerProps {
  state: UIState;
  children: React.ReactNode;
  loadingFallback?: React.ReactNode;
  emptyFallback?: React.ReactNode;
  errorFallback?: React.ReactNode;
  loadingMessage?: string;
  errorMessage?: string;
  emptyTitle?: string;
  emptyDescription?: string;
  emptyActionLabel?: string;
  onEmptyAction?: () => void;
  onRetry?: () => void;
}

export const StateContainer: React.FC<StateContainerProps> = ({
  state,
  children,
  loadingFallback,
  emptyFallback,
  errorFallback,
  loadingMessage,
  errorMessage,
  emptyTitle,
  emptyDescription,
  emptyActionLabel,
  onEmptyAction,
  onRetry,
}) => {
  if (state === "LOADING" || state === "PENDING") {
    if (loadingFallback) return <>{loadingFallback}</>;
    return (
      <div className="flex flex-col items-center justify-center p-8 text-center" aria-live="polite" aria-busy="true">
        <div className="h-8 w-8 animate-spin rounded-full border-3 border-[#0B5D9B] border-t-transparent" />
        <p className="mt-3 text-xs text-slate-600 font-medium">
          {loadingMessage || (state === "PENDING" ? "Processing verification query..." : "Loading content...")}
        </p>
      </div>
    );
  }

  if (state === "EMPTY") {
    if (emptyFallback) return <>{emptyFallback}</>;
    return (
      <div className="rounded-2xl border-2 border-dashed border-slate-200 p-8 text-center space-y-2">
        <div className="text-3xl mb-2">📁</div>
        <h3 className="text-sm font-bold text-slate-800 m-0">
          {emptyTitle || "No records found"}
        </h3>
        <p className="text-xs text-slate-500 max-w-sm mx-auto m-0">
          {emptyDescription || "There are no items matching this criteria."}
        </p>
        {emptyActionLabel && onEmptyAction && (
          <div className="pt-2">
            <button
              type="button"
              onClick={onEmptyAction}
              className="inline-flex items-center px-4 py-2 rounded-xl text-xs font-bold bg-[#0B5D9B] text-white hover:bg-[#074B7D] transition-colors cursor-pointer"
            >
              {emptyActionLabel}
            </button>
          </div>
        )}
      </div>
    );
  }

  if (state === "ERROR" || state === "OFFLINE" || state === "UNAUTHORIZED" || state === "EXPIRED") {
    if (errorFallback) return <>{errorFallback}</>;
    return (
      <div className="rounded-2xl border border-rose-200 bg-rose-50/80 p-6 text-center space-y-2" role="alert">
        <div className="text-2xl mb-1">
          {state === "OFFLINE" ? "📡" : state === "UNAUTHORIZED" ? "🔒" : state === "EXPIRED" ? "⏳" : "⚠️"}
        </div>
        <h3 className="text-sm font-bold text-rose-900 m-0">
          {state === "OFFLINE"
            ? "Network Offline"
            : state === "EXPIRED"
            ? "Session Expired"
            : state === "UNAUTHORIZED"
            ? "Access Unauthorized"
            : "Operation Failed"}
        </h3>
        <p className="text-xs text-rose-700 max-w-md mx-auto m-0">
          {errorMessage || "An unexpected condition occurred. Please verify your connection and try again."}
        </p>
        {onRetry && (
          <div className="pt-2">
            <button
              type="button"
              onClick={onRetry}
              className="inline-flex items-center justify-center rounded-xl bg-rose-700 px-4 py-2 text-xs font-bold text-white shadow-xs hover:bg-rose-800 cursor-pointer"
            >
              Try again
            </button>
          </div>
        )}
      </div>
    );
  }

  return <>{children}</>;
};
