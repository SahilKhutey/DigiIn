import React, { useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { useLanguage } from "../../context/LanguageContext";
import { Button, Switch, Badge, DigiInIDCard } from "../../components/ui";

export const SettingsView: React.FC = () => {
  const { user } = useAuth();
  const { locale, setLocale } = useLanguage();
  const [passkeysEnabled, setPasskeysEnabled] = useState(true);
  const [offlineCacheEnabled, setOfflineCacheEnabled] = useState(true);
  const [autoVerifyPredicates, setAutoVerifyPredicates] = useState(true);
  const [notice, setNotice] = useState<string | null>(null);

  const handleSave = () => {
    setNotice("Settings successfully updated and cryptographically synchronized.");
    setTimeout(() => setNotice(null), 3000);
  };

  return (
    <div className="space-y-8 max-w-4xl mx-auto py-2">
      <div>
        <h1 className="text-2xl md:text-3xl font-extrabold text-[#092F4F] m-0">
          Account & Security Settings
        </h1>
        <p className="text-xs md:text-sm text-slate-500 mt-1 m-0">
          Manage your sovereign biometric passkeys, local cryptographic cache, and verification preferences.
        </p>
      </div>

      {notice && (
        <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-300 text-xs font-bold text-emerald-900 flex items-center justify-between" role="status">
          <span>✓ {notice}</span>
        </div>
      )}

      {/* 1. Sovereign Identity Card */}
      <div className="space-y-4">
        <DigiInIDCard
          idNumber={user?.digiinId || "DI-7K4M-9Q2X-8P6R"}
          holderName={user?.name || "Rahul Sharma"}
          status="Active & Sovereign"
        />

        <div className="bg-white border border-[#CBD5E1] rounded-2xl p-5 shadow-xs space-y-3">
          <h2 className="text-sm font-bold text-[#092F4F] m-0 flex items-center gap-2">
            <span>👤</span> Personal Account Attributes (Private)
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div className="bg-slate-50 p-3 rounded-xl border border-slate-200 space-y-1">
              <span className="text-slate-500 font-medium">Citizen Full Name:</span>
              <div className="font-bold text-slate-900">{user?.name || "Rahul Sharma"}</div>
            </div>
            <div className="bg-slate-50 p-3 rounded-xl border border-slate-200 space-y-1">
              <span className="text-slate-500 font-medium">Account Role:</span>
              <div className="font-bold text-slate-900">{user?.role || "CITIZEN"}</div>
            </div>
            <div className="bg-slate-50 p-3 rounded-xl border border-slate-200 space-y-1 sm:col-span-2 font-mono">
              <span className="font-sans text-slate-500 font-medium">Ed25519 Root Key Fingerprint:</span>
              <div className="text-[11px] text-slate-700 break-all">SHA256:8f9a2b1c4e7d0f3a6b5c8e9d2a4f7b0e3c6a9d1f5e8b2a4c</div>
            </div>
          </div>
        </div>
      </div>

      {/* 2. Security & Passkeys */}
      <div className="bg-white border border-[#CBD5E1] rounded-2xl p-6 shadow-xs space-y-6">
        <h2 className="text-base font-bold text-[#092F4F] m-0 flex items-center gap-2">
          <span>🔐</span> Authentication & Biometrics
        </h2>

        <div className="space-y-4 divide-y divide-slate-100 text-xs">
          <div className="flex items-center justify-between pt-2">
            <div>
              <strong className="text-sm font-bold text-slate-900 block">FIDO2 / WebAuthn Passkeys</strong>
              <span className="text-slate-500">Sign in securely using device fingerprint or Face ID without SMS OTP</span>
            </div>
            <Switch checked={passkeysEnabled} onChange={setPasskeysEnabled} />
          </div>

          <div className="flex items-center justify-between pt-4">
            <div>
              <strong className="text-sm font-bold text-slate-900 block">Offline Verifiable JWKS Cache</strong>
              <span className="text-slate-500">Pre-cache official CBSE, UIDAI, and MoRTH public keys for zero-network validation</span>
            </div>
            <Switch checked={offlineCacheEnabled} onChange={setOfflineCacheEnabled} />
          </div>

          <div className="flex items-center justify-between pt-4">
            <div>
              <strong className="text-sm font-bold text-slate-900 block">Enforce Zero-Knowledge Predicates</strong>
              <span className="text-slate-500">Always default to mathematical boolean assertions instead of sharing raw dates or marks</span>
            </div>
            <Switch checked={autoVerifyPredicates} onChange={setAutoVerifyPredicates} />
          </div>
        </div>
      </div>

      {/* 3. Language & Localization */}
      <div className="bg-white border border-[#CBD5E1] rounded-2xl p-6 shadow-xs space-y-4">
        <h2 className="text-base font-bold text-[#092F4F] m-0 flex items-center gap-2">
          <span>🌐</span> Language & Regional Interface
        </h2>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
          {[
            { code: "en", label: "English", sub: "National Standard" },
            { code: "hi", label: "हिन्दी (Hindi)", sub: "राजभाषा" },
            { code: "bn", label: "বাংলা (Bengali)", sub: "পশ্চিমবঙ্গ" },
            { code: "ta", label: "தமிழ் (Tamil)", sub: "தமிழ்நாடு" },
          ].map((lang) => (
            <button
              key={lang.code}
              type="button"
              onClick={() => setLocale(lang.code as any)}
              className={`p-3.5 rounded-xl border text-left transition-all cursor-pointer ${
                locale === lang.code
                  ? "bg-[#EBF4FA] border-[#0B5D9B] text-[#092F4F] font-bold shadow-xs"
                  : "bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100"
              }`}
            >
              <div className="font-bold text-sm">{lang.label}</div>
              <div className="text-[11px] text-slate-500 mt-0.5">{lang.sub}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Actions */}
      <div className="flex justify-end gap-3 pt-2">
        <Button variant="primary" size="md" onClick={handleSave} className="font-bold shadow-xs">
          Save Settings & Sync
        </Button>
      </div>
    </div>
  );
};
