import React from "react";
import { StateContainer, UIState } from "./StateContainer";

export interface DataStateProps {
  loading?: boolean;
  error?: string | Error | null;
  empty?: boolean;
  offline?: boolean;
  unauthorized?: boolean;
  expired?: boolean;
  loadingMessage?: string;
  emptyTitle?: string;
  emptyDescription?: string;
  emptyActionLabel?: string;
  onEmptyAction?: () => void;
  onRetry?: () => void;
  children: React.ReactNode;
}

export const DataState: React.FC<DataStateProps> = ({
  loading = false,
  error = null,
  empty = false,
  offline = false,
  unauthorized = false,
  expired = false,
  loadingMessage,
  emptyTitle,
  emptyDescription,
  emptyActionLabel,
  onEmptyAction,
  onRetry,
  children,
}) => {
  let state: UIState = "SUCCESS";

  if (offline) {
    state = "OFFLINE";
  } else if (unauthorized) {
    state = "UNAUTHORIZED";
  } else if (expired) {
    state = "EXPIRED";
  } else if (error) {
    state = "ERROR";
  } else if (loading) {
    state = "LOADING";
  } else if (empty) {
    state = "EMPTY";
  }

  const errorMessage = error instanceof Error ? error.message : typeof error === "string" ? error : undefined;

  return (
    <StateContainer
      state={state}
      loadingMessage={loadingMessage}
      errorMessage={errorMessage}
      emptyTitle={emptyTitle}
      emptyDescription={emptyDescription}
      emptyActionLabel={emptyActionLabel}
      onEmptyAction={onEmptyAction}
      onRetry={onRetry}
    >
      {children}
    </StateContainer>
  );
};
