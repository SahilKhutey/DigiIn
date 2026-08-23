import React from "react";

export interface TimelineStepItem {
  id: string;
  title: string;
  desc?: string;
}

export interface VerificationTimelineProps {
  steps: TimelineStepItem[];
  currentStepIndex: number;
  className?: string;
}

export const VerificationTimeline: React.FC<VerificationTimelineProps> = ({
  steps,
  currentStepIndex,
  className = "",
}) => {
  return (
    <div className={`space-y-4 ${className}`} aria-live="polite" aria-label="Verification Pipeline Progress">
      {steps.map((step, idx) => {
        const isCompleted = idx < currentStepIndex;
        const isActive = idx === currentStepIndex;

        return (
          <div key={step.id} className="flex items-start gap-3.5 relative">
            {idx < steps.length - 1 && (
              <div
                className={`absolute left-3.5 top-7 -bottom-4 w-0.5 ${
                  isCompleted ? "bg-[#86EFAC]" : "bg-slate-200"
                }`}
                aria-hidden="true"
              />
            )}

            <div
              className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold shrink-0 z-10 ${
                isCompleted
                  ? "bg-[#DFF6E8] text-[#14743F] border border-[#86EFAC]"
                  : isActive
                  ? "bg-[#EBF4FA] text-[#0B5D9B] border-2 border-[#0B5D9B] ring-4 ring-[#EBF4FA]"
                  : "bg-slate-100 text-slate-500 border border-slate-300"
              }`}
            >
              {isCompleted ? "✓" : idx + 1}
            </div>

            <div className="flex-1 pt-0.5">
              <span
                className={`text-sm block ${
                  isActive ? "font-bold text-[#0B5D9B]" : isCompleted ? "font-semibold text-[#092F4F]" : "text-slate-500"
                }`}
              >
                {step.title}
              </span>
              {step.desc && <p className="text-xs text-slate-500 mt-0.5 mb-0">{step.desc}</p>}
            </div>
          </div>
        );
      })}
    </div>
  );
};
