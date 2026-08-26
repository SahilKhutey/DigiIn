import React, { useState } from "react";

export interface NotificationRecord {
  id: string;
  title: string;
  message: string;
  timestamp: string;
  type: "ACTION_REQUIRED" | "UNREAD" | "READ";
  actionLabel?: string;
  actionView?: string;
}

const INITIAL_NOTIFICATIONS: NotificationRecord[] = [
  {
    id: "notif_1",
    title: "Verification request",
    message: "NTA requested your Class XII qualification.",
    timestamp: "2 min ago",
    type: "ACTION_REQUIRED",
    actionLabel: "Review",
    actionView: "CONSENT",
  },
  {
    id: "notif_2",
    title: "Document verified",
    message: "Your CBSE certificate has been verified.",
    timestamp: "Yesterday",
    type: "UNREAD",
    actionLabel: "View",
    actionView: "CREDENTIALS",
  },
  {
    id: "notif_3",
    title: "Credential issued",
    message: "Driving Licence (LMV) credential issued by MoRTH.",
    timestamp: "2 days ago",
    type: "READ",
    actionLabel: "View",
    actionView: "WALLET",
  },
];

export interface NotificationsViewProps {
  onNavigate?: (view: any) => void;
}

export const NotificationsView: React.FC<NotificationsViewProps> = ({ onNavigate }) => {
  const [notifications, setNotifications] = useState(INITIAL_NOTIFICATIONS);
  const [filter, setFilter] = useState<"ALL" | "ACTION_REQUIRED" | "UNREAD">("ALL");

  const filtered = notifications.filter((n) => {
    if (filter === "ACTION_REQUIRED") return n.type === "ACTION_REQUIRED";
    if (filter === "UNREAD") return n.type === "UNREAD" || n.type === "ACTION_REQUIRED";
    return true;
  });

  const markAllRead = () => {
    setNotifications((prev) =>
      prev.map((n) => (n.type === "UNREAD" ? { ...n, type: "READ" } : n))
    );
  };

  return (
    <div className="space-y-6 max-w-3xl mx-auto py-2">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#092F4F] m-0">
            Notifications
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 m-0">
            Important updates about your DigiIn account.
          </p>
        </div>

        <div>
          <button
            type="button"
            onClick={markAllRead}
            className="text-xs font-bold text-[#0B5D9B] hover:underline cursor-pointer"
          >
            Mark all as read
          </button>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-200 pb-3 text-xs font-bold">
        {[
          { key: "ALL", label: "All" },
          { key: "ACTION_REQUIRED", label: "Action Required" },
          { key: "UNREAD", label: "Unread" },
        ].map((tab) => (
          <button
            key={tab.key}
            type="button"
            onClick={() => setFilter(tab.key as any)}
            className={`px-3 py-1.5 rounded-full transition-all cursor-pointer ${
              filter === tab.key
                ? "bg-[#0B5D9B] text-white shadow-xs"
                : "bg-slate-100 text-slate-600 hover:bg-slate-200"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Notifications List */}
      <div className="space-y-3">
        {filtered.map((item) => {
          const isActionRequired = item.type === "ACTION_REQUIRED";
          const isUnread = item.type === "UNREAD";

          return (
            <div
              key={item.id}
              className={`p-4 rounded-2xl border transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-3 ${
                isActionRequired
                  ? "bg-amber-50/70 border-amber-200"
                  : isUnread
                  ? "bg-white border-blue-200 shadow-2xs"
                  : "bg-white border-slate-200 opacity-80"
              }`}
            >
              <div className="flex items-start gap-3">
                <div className="mt-1">
                  {isActionRequired ? (
                    <span className="w-2.5 h-2.5 rounded-full bg-amber-500 block" />
                  ) : isUnread ? (
                    <span className="w-2.5 h-2.5 rounded-full bg-blue-600 block" />
                  ) : (
                    <span className="w-2.5 h-2.5 rounded-full bg-slate-300 block" />
                  )}
                </div>

                <div className="space-y-0.5">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-bold text-[#092F4F]">
                      {item.title}
                    </span>
                    <span className="text-[11px] text-slate-400 font-medium">
                      · {item.timestamp}
                    </span>
                  </div>
                  <p className="text-xs text-slate-600 m-0">
                    {item.message}
                  </p>
                </div>
              </div>

              {item.actionLabel && (
                <div className="shrink-0 pt-1 sm:pt-0">
                  <button
                    type="button"
                    onClick={() => item.actionView && onNavigate?.(item.actionView)}
                    className="px-3.5 py-1.5 rounded-xl text-xs font-bold bg-[#0B5D9B] text-white hover:bg-[#074B7D] transition-all cursor-pointer"
                  >
                    {item.actionLabel} →
                  </button>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
