import React from "react";

export type StepStatus = "completed" | "in_progress" | "pending" | "failed";

export interface ProgressStep {
  id: string;
  title: string;
  description?: string;
  status: StepStatus;
}

export interface ProgressIndicatorProps {
  steps: ProgressStep[];
  currentStepIndex?: number;
  className?: string;
}

export const ProgressIndicator: React.FC<ProgressIndicatorProps> = ({
  steps,
  currentStepIndex = 0,
  className = "",
}) => {
  return (
    <div
      className={`ux4g-progress-stepper ${className}`}
      aria-label="Verification progress tracker"
    >
      <ol className="list-none p-0 m-0 space-y-4">
        {steps.map((step, idx) => {
          const isCompleted = step.status === "completed";
          const isInProgress = step.status === "in_progress";
          const isFailed = step.status === "failed";
          const isPending = step.status === "pending";

          let icon = (idx + 1).toString();
          let iconBg = "bg-slate-100 text-slate-600 border-slate-300";
          let textColor = "text-slate-500";

          if (isCompleted) {
            icon = "✓";
            iconBg = "bg-[#DFF6E8] text-[#14743F] border-[#86EFAC]";
            textColor = "text-[#14743F] font-bold";
          } else if (isInProgress) {
            iconBg = "bg-[#0B5D9B] text-white border-[#0B5D9B] ring-4 ring-[#0B5D9B]/20";
            textColor = "text-[#0B5D9B] font-bold";
          } else if (isFailed) {
            icon = "✕";
            iconBg = "bg-[#FEE2E2] text-[#991B1B] border-[#FCA5A5]";
            textColor = "text-[#991B1B] font-bold";
          }

          return (
            <li
              key={step.id || idx}
              className="relative flex items-start gap-4"
              aria-current={isInProgress ? "step" : undefined}
            >
              {/* Vertical connector line */}
              {idx < steps.length - 1 && (
                <div
                  className={`absolute top-8 left-4 -ml-px w-0.5 h-[calc(100%-8px)] ${
                    isCompleted ? "bg-[#86EFAC]" : "bg-slate-200"
                  }`}
                  aria-hidden="true"
                />
              )}

              {/* Step indicator circle */}
              <div
                className={`w-8 h-8 rounded-full border-2 flex items-center justify-center text-xs shrink-0 select-none z-10 ${iconBg}`}
                aria-hidden="true"
              >
                {icon}
              </div>

              {/* Content */}
              <div className="flex-1 pt-0.5">
                <div className="flex items-center justify-between gap-2">
                  <span className={`text-sm ${textColor}`}>{step.title}</span>
                  <span className="text-xs uppercase font-bold tracking-wider text-slate-400">
                    {isCompleted && "Complete"}
                    {isInProgress && "In Progress"}
                    {isFailed && "Action Needed"}
                    {isPending && "Pending"}
                  </span>
                </div>
                {step.description && (
                  <p className="text-xs text-slate-500 mt-0.5 mb-0 leading-relaxed">
                    {step.description}
                  </p>
                )}
              </div>
            </li>
          );
        })}
      </ol>
    </div>
  );
};

export interface StepperProps {
  steps: string[];
  currentStep: number;
  className?: string;
}

export const Stepper: React.FC<StepperProps> = ({
  steps,
  currentStep,
  className = "",
}) => {
  return (
    <ol
      className={`flex items-center justify-between list-none p-0 m-0 gap-2 border-b border-slate-200 pb-4 overflow-x-auto ${className}`}
      aria-label="Progress Stepper"
    >
      {steps.map((step, idx) => {
        const isCompleted = idx < currentStep;
        const isCurrent = idx === currentStep;

        return (
          <li
            key={idx}
            className={`flex items-center gap-2 text-xs font-bold whitespace-nowrap ${
              isCurrent
                ? "text-[#0B5D9B]"
                : isCompleted
                ? "text-[#14743F]"
                : "text-slate-400"
            }`}
            aria-current={isCurrent ? "step" : undefined}
          >
            <span
              className={`w-6 h-6 rounded-full flex items-center justify-center text-[11px] font-extrabold border ${
                isCompleted
                  ? "bg-[#DFF6E8] text-[#14743F] border-[#86EFAC]"
                  : isCurrent
                  ? "bg-[#0B5D9B] text-white border-[#0B5D9B]"
                  : "bg-slate-100 text-slate-500 border-slate-300"
              }`}
            >
              {isCompleted ? "✓" : idx + 1}
            </span>
            <span>{step}</span>
            {idx < steps.length - 1 && (
              <span className="text-slate-300 ml-1" aria-hidden="true">→</span>
            )}
          </li>
        );
      })}
    </ol>
  );
};
