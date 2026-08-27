import React, { useState, useEffect } from "react";
import QRCode from "qrcode";

export interface DigiInIDCardProps {
  idNumber?: string;
  holderName?: string;
  status?: string;
  className?: string;
}

export const DigiInIDCard: React.FC<DigiInIDCardProps> = ({
  idNumber = "DI-7K4M-9Q2X-8P6R",
  holderName = "Rahul Sharma",
  status = "Active & Sovereign",
  className = "",
}) => {
  const [copied, setCopied] = useState(false);
  const [showQrModal, setShowQrModal] = useState(false);
  const [qrDataUrl, setQrDataUrl] = useState<string>("");
  const [tempCode, setTempCode] = useState<string>("482913");
  const [secondsRemaining, setSecondsRemaining] = useState<number>(600);

  const handleCopy = () => {
    navigator.clipboard.writeText(idNumber);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleGenerateNewCode = () => {
    const newCode = Math.floor(100000 + Math.random() * 900000).toString();
    setTempCode(newCode);
    setSecondsRemaining(600);
  };

  useEffect(() => {
    const payload = `digiin://verify?id=${idNumber}&t=${Date.now()}&code=${tempCode}`;
    QRCode.toDataURL(payload, { width: 220, margin: 2, color: { dark: "#092F4F", light: "#FFFFFF" } })
      .then((url) => setQrDataUrl(url))
      .catch((err) => console.error("Error generating QR code:", err));
  }, [idNumber, tempCode]);

  useEffect(() => {
    if (secondsRemaining <= 0) return;
    const timer = setInterval(() => {
      setSecondsRemaining((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);
    return () => clearInterval(timer);
  }, [secondsRemaining]);

  const formatTimer = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <>
      <div className={`bg-gradient-to-br from-[#092F4F] via-[#0B4F71] to-[#0B5D9B] text-white rounded-2xl p-6 shadow-md relative overflow-hidden ${className}`}>
        <div className="flex justify-between items-start mb-4">
          <div>
            <span className="text-[10px] uppercase font-bold tracking-widest text-slate-300 block">
              Digital Public Infrastructure
            </span>
            <h4 className="text-lg font-bold text-white m-0">DigiIn Sovereign ID</h4>
          </div>
          <div className="text-2xl" aria-hidden="true">🇮🇳</div>
        </div>

        <div className="my-4">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-300 block">Universal Public Account Reference</span>
            <span className="text-[10px] font-bold text-cyan-200 bg-white/10 px-2 py-0.5 rounded-full border border-white/20">
              Identifier Only • Non-Bearer
            </span>
          </div>
          <code className="text-2xl font-extrabold font-mono tracking-wider text-cyan-300 block mt-1">
            {idNumber}
          </code>
        </div>

        <div className="flex items-center justify-between pt-4 border-t border-white/20 text-xs">
          <div>
            <span className="text-slate-300 block text-[11px]">Holder: {holderName}</span>
            <span className="font-bold text-emerald-300 flex items-center gap-1 mt-0.5">
              ✓ {status}
            </span>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setShowQrModal(true)}
              className="px-3 py-1.5 rounded-lg bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-200 font-bold transition-colors cursor-pointer border border-cyan-400/30 flex items-center gap-1.5"
            >
              <span>📱 QR & OTP</span>
            </button>

            <button
              type="button"
              onClick={handleCopy}
              className="px-3 py-1.5 rounded-lg bg-white/10 hover:bg-white/20 text-white font-bold transition-colors cursor-pointer border border-white/30"
            >
              {copied ? "✓ Copied" : "Copy ID"}
            </button>
          </div>
        </div>
      </div>

      {/* QR Code & Temporary Verification Code Modal */}
      {showQrModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-xs p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-200 text-slate-900 animate-in fade-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3 mb-4">
              <div className="flex items-center gap-2">
                <span className="text-xl">🛡️</span>
                <h3 className="font-extrabold text-base text-[#092F4F] m-0">In-Person & Kiosk Verification</h3>
              </div>
              <button
                type="button"
                onClick={() => setShowQrModal(false)}
                className="text-slate-400 hover:text-slate-700 font-bold text-lg cursor-pointer"
              >
                ✕
              </button>
            </div>

            <div className="space-y-4 text-center">
              <div>
                <span className="text-xs text-slate-500 block uppercase font-bold tracking-wider">Citizen Public ID</span>
                <code className="text-lg font-extrabold font-mono text-[#0B5D9B] bg-slate-100 px-3 py-1 rounded-lg inline-block mt-1">
                  {idNumber}
                </code>
              </div>

              {/* Dynamic QR Code */}
              <div className="flex justify-center p-2 bg-slate-50 rounded-xl border border-slate-200 inline-block mx-auto">
                {qrDataUrl ? (
                  <img src={qrDataUrl} alt="DigiIn Verification QR" className="w-48 h-48 rounded-lg" />
                ) : (
                  <div className="w-48 h-48 flex items-center justify-center text-slate-400 text-xs">Generating QR...</div>
                )}
              </div>

              {/* Temporary 6-digit Code */}
              <div className="bg-blue-50/70 border border-blue-200 rounded-xl p-3 text-center">
                <div className="text-xs font-bold text-blue-900 uppercase tracking-wide">
                  Temporary Counter Verification Code
                </div>
                <div className="text-2xl font-mono font-extrabold tracking-widest text-[#092F4F] my-1">
                  {tempCode}
                </div>
                <div className="text-[11px] text-slate-600 flex items-center justify-center gap-2">
                  <span>⏱️ Valid for: <strong className="text-blue-700 font-mono">{formatTimer(secondsRemaining)}</strong></span>
                  <span>•</span>
                  <button
                    type="button"
                    onClick={handleGenerateNewCode}
                    className="text-[#0B5D9B] font-bold hover:underline cursor-pointer"
                  >
                    Refresh Code ⟳
                  </button>
                </div>
              </div>

              {/* Security Invariant Callout */}
              <div className="text-left bg-slate-50 border border-slate-200 rounded-xl p-3 text-xs text-slate-600 space-y-1">
                <div className="font-bold text-slate-800 flex items-center gap-1">
                  <span>🔒</span> Security Model:
                </div>
                <p className="m-0 leading-relaxed">
                  Possession of this ID alone grants <strong>zero access</strong> to your documents. The requesting department receives only verified assertions you explicitly consent to.
                </p>
              </div>

              <button
                type="button"
                onClick={() => setShowQrModal(false)}
                className="w-full py-2.5 bg-[#092F4F] text-white font-bold rounded-xl hover:bg-[#074B7D] transition-all cursor-pointer text-sm"
              >
                Close Window
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

