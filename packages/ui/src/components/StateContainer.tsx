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
  errorMessage?: string;
  onRetry?: () => void;
}

export const StateContainer: React.FC<StateContainerProps> = ({
  state,
  children,
  loadingFallback,
  emptyFallback,
  errorFallback,
  errorMessage,
  onRetry,
}) => {
  if (state === "LOADING" || state === "PENDING") {
    if (loadingFallback) return <>{loadingFallback}</>;
    return (
      <div className="flex flex-col items-center justify-center p-8 text-center" aria-live="polite" aria-busy="true">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
        <p className="mt-3 text-sm text-slate-600 font-medium">
          {state === "PENDING" ? "Processing verification query..." : "Loading content..."}
        </p>
      </div>
    );
  }

  if (state === "EMPTY") {
    if (emptyFallback) return <>{emptyFallback}</>;
    return (
      <div className="rounded-lg border-2 border-dashed border-slate-200 p-8 text-center">
        <h3 className="text-sm font-semibold text-slate-900">No records found</h3>
        <p className="mt-1 text-sm text-slate-500">There are no items matching this criteria.</p>
      </div>
    );
  }

  if (state === "ERROR" || state === "OFFLINE" || state === "UNAUTHORIZED" || state === "EXPIRED") {
    if (errorFallback) return <>{errorFallback}</>;
    return (
      <div className="rounded-lg border border-rose-200 bg-rose-50 p-6 text-center" role="alert">
        <h3 className="text-base font-semibold text-rose-900">
          {state === "OFFLINE" ? "Network Offline" : state === "EXPIRED" ? "Session Expired" : "Operation Failed"}
        </h3>
        <p className="mt-2 text-sm text-rose-700">
          {errorMessage || "An unexpected system condition occurred. Please verify your connection and try again."}
        </p>
        {onRetry && (
          <button
            type="button"
            onClick={onRetry}
            className="mt-4 inline-flex items-center justify-center rounded-md bg-rose-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-rose-500 focus:outline-none focus:ring-2 focus:ring-rose-500 focus:ring-offset-2"
          >
            Retry Action
          </button>
        )}
      </div>
    );
  }

  return <>{children}</>;
};
