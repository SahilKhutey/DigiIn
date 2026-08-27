import React from "react";

type NoticeBannerProps = {
  notice: string;
  onBackToHome?: () => void;
  isHome?: boolean;
};

export function NoticeBanner({ notice, onBackToHome, isHome = false }: NoticeBannerProps) {
  if (!notice) return null;

  return (
    <footer className="notice mt-12 pt-6 pb-4 border-t border-slate-200/80 text-center text-xs text-slate-500 space-y-2" role="status" aria-live="polite">
      <p className="m-0 max-w-2xl mx-auto leading-relaxed text-slate-600 font-medium">
        {notice}
      </p>
      {!isHome && onBackToHome && (
        <div className="pt-1">
          <button
            type="button"
            onClick={onBackToHome}
            className="inline-flex items-center gap-1 text-xs font-bold text-[#0B5D9B] hover:text-[#074B7D] hover:underline cursor-pointer transition-colors"
          >
            ← Back to Home
          </button>
        </div>
      )}
    </footer>
  );
}
