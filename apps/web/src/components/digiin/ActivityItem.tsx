import React from "react";

export interface ActivityItemProps {
  time: string;
  title: string;
  actor: string;
  type?: "verification" | "consent" | "document" | "security";
  className?: string;
}

export const ActivityItem: React.FC<ActivityItemProps> = ({
  time,
  title,
  actor,
  type = "verification",
  className = "",
}) => {
  const iconByType = {
    verification: "🛡️",
    consent: "🔐",
    document: "📁",
    security: "🔒",
  };

  return (
    <div
      className={`flex items-center justify-between p-3.5 bg-white border border-slate-200 rounded-xl text-xs hover:border-[#0B5D9B] transition-colors ${className}`}
    >
      <div className="flex items-center gap-3">
        <span className="text-base">{iconByType[type]}</span>
        <div>
          <div className="font-bold text-[#092F4F]">{title}</div>
          <div className="text-slate-400 text-[11px]">Actor: {actor}</div>
        </div>
      </div>
      <span className="text-slate-400 font-mono text-[11px] shrink-0">{time}</span>
    </div>
  );
};
