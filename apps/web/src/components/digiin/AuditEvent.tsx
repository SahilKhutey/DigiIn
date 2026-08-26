import React from "react";
import type { PlatformEvent } from "../../types";

export interface AuditEventProps {
  event: PlatformEvent;
}

export const AuditEvent: React.FC<AuditEventProps> = ({ event }) => {
  return (
    <div className="audit-event-item flex items-start gap-4 p-4 rounded-xl border border-slate-200 bg-white shadow-2xs transition-all hover:border-slate-300">
      <div className="h-8 w-8 rounded-full bg-blue-50 text-blue-700 flex items-center justify-center font-bold text-sm shrink-0 border border-blue-200">
        🔒
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between gap-2 mb-1">
          <span className="text-xs font-bold uppercase tracking-wider text-[#0B5D9B]">
            {event.type}
          </span>
          <span className="text-[11px] text-slate-500 font-medium">
            {event.createdAt ? new Date(event.createdAt).toLocaleString() : "Just now"}
          </span>
        </div>
        <p className="text-sm font-semibold text-slate-800 leading-snug mb-1.5">{event.message}</p>
        <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500 font-mono">
          <span>Actor: <strong className="font-sans text-slate-700">{event.actor}</strong></span>
          <span>Ref: <code className="bg-slate-100 px-1.5 py-0.5 rounded text-[11px] text-slate-700">{event.aggregateId || event.eventId}</code></span>
        </div>
      </div>
    </div>
  );
};
