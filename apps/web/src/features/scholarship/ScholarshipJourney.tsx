import React, { useState, useEffect, useCallback } from "react";
import * as api from "../../api/client";
import type {
  ScholarshipApplicationResponse,
  SharingReviewResponse,
  ConsentSubmitResponse,
} from "../../types";
import { useLanguage } from "../../context/LanguageContext";

type Step =
  | "LANDING_CHOICE"
  | "USE_DIGIIN"
  | "CLAIMS_DISCOVERED"
  | "SHARING_REVIEW"
  | "CONSENT"
  | "SUBMITTING"
  | "SUCCESS"
  | "PROOF_READY"
  | "VERIFIER_VIEW";

const DEMO_CITIZEN_ID = "DIN-DEMO-001";
const DEMO_CITIZEN_NAME = "Demo Citizen (Rahul Sharma)";

const SandboxBanner: React.FC = () => (
  <div
    role="alert"
    className="flex items-center gap-2 bg-amber-50 border border-amber-300 text-amber-800 text-xs font-semibold rounded-lg px-4 py-2 mb-4"
  >
    <span aria-hidden="true">⚠️</span>
    <span>
      SANDBOX DEMO — No real government systems connected. All data is synthetic.
    </span>
  </div>
);

const StepIndicator: React.FC<{ current: number; total: number }> = ({ current, total }) => (
  <div className="flex items-center gap-1 mb-6" aria-label={`Step ${current} of ${total}`}>
    {Array.from({ length: total }, (_, i) => (
      <div
        key={i}
        className={`h-1.5 flex-1 rounded-full transition-all ${
          i < current ? "bg-[#0B5D9B]" : i === current ? "bg-[#60A5FA]" : "bg-slate-200"
        }`}
      />
    ))}
  </div>
);

const ClaimRow: React.FC<{ label: string; value: string; isPredicate?: boolean }> = ({
  label, value, isPredicate,
}) => (
  <div className="flex items-start justify-between py-2 border-b border-slate-100 last:border-0">
    <div>
      <div className="text-sm font-semibold text-slate-800">{label}</div>
      {isPredicate && (
        <div className="text-[11px] text-indigo-600 font-medium mt-0.5">
          Zero-Knowledge Predicate
        </div>
      )}
    </div>
    <div className="text-sm text-slate-600 text-right max-w-[160px] truncate">{value}</div>
  </div>
);

const WithheldRow: React.FC<{ label: string }> = ({ label }) => (
  <div className="flex items-center gap-2 py-1.5 text-sm text-slate-600">
    <span className="text-red-500 font-bold text-base" aria-hidden="true">✕</span>
    {label}
  </div>
);

export const ScholarshipJourney: React.FC<{ onBack?: () => void }> = ({ onBack }) => {
  const { locale, setLocale } = useLanguage();
  const hi = locale === "hi";

  const [step, setStep] = useState<Step>("LANDING_CHOICE");
  const [application, setApplication] = useState<ScholarshipApplicationResponse | null>(null);
  const [sharingReview, setSharingReview] = useState<SharingReviewResponse | null>(null);
  const [consentResult, setConsentResult] = useState<ConsentSubmitResponse | null>(null);
  const [tampered, setTampered] = useState(false);

  const FALLBACK_REVIEW: SharingReviewResponse = {
    application_id: "APP-DEMO-2026",
    service_name: "National Merit-cum-Means Scholarship",
    service_purpose: "Scholarship eligibility verification",
    requester_organization: "University of Delhi (DEMO)",
    shared_claims: [
      { claim_key: "name", claim_label: hi ? "नाम" : "Name", value_summary: "Rahul Sharma", is_predicate: false },
      { claim_key: "domicile", claim_label: hi ? "अधिवास" : "Domicile", value_summary: "Delhi", is_predicate: false },
      { claim_key: "income_eligible", claim_label: hi ? "आय पात्रता" : "Income Eligibility", value_summary: hi ? "पात्र (ZK)" : "Eligible (ZK Predicate)", is_predicate: true },
      { claim_key: "education", claim_label: hi ? "शिक्षा" : "Education", value_summary: "Class XII — Passed", is_predicate: false },
    ],
    withheld_fields: ["aadhaar_number", "raw_documents", "pan_number"],
    raw_files_transferred_bytes: 0,
    validity_hours: 24,
    consent_required: true,
  };

  const FALLBACK_RESULT: ConsentSubmitResponse = {
    status: "success",
    application_id: "APP-DEMO-2026",
    proof_token: "PRF-DEMO-1042",
    proof_id: "PRF-DEMO-1042",
    message: "Scholarship application submitted successfully.",
    raw_files_transferred_bytes: 0,
    claims_shared: 4,
    institution_verification_url: "/api/v1/proofs/PRF-DEMO-1042/verify",
  };

  const handleUseDigiIn = useCallback(async () => {
    setStep("USE_DIGIIN");
    try {
      const app = await api.startScholarshipApplication(DEMO_CITIZEN_ID, DEMO_CITIZEN_NAME);
      setApplication(app);
    } catch {
      setApplication({ status: "success", application_id: "APP-DEMO-2026", service_name: "National Merit-cum-Means Scholarship", citizen_name: DEMO_CITIZEN_NAME, application_status: "CLAIMS_DISCOVERED", next_step: "/api/v1/public-service/scholarship/APP-DEMO-2026/sharing-review", estimated_time: "2 minutes" });
    }
    setStep("CLAIMS_DISCOVERED");
  }, []);

  const handleReviewSharing = useCallback(async () => {
    const appId = application?.application_id ?? "APP-DEMO-2026";
    try {
      const review = await api.getSharingReview(appId);
      setSharingReview(review);
    } catch {
      setSharingReview(FALLBACK_REVIEW);
    }
    setStep("SHARING_REVIEW");
  }, [application, hi]);

  const handleSubmit = useCallback(async () => {
    setStep("SUBMITTING");
    const appId = application?.application_id ?? "APP-DEMO-2026";
    try {
      const result = await api.submitScholarshipConsent(appId, DEMO_CITIZEN_ID);
      setConsentResult(result);
    } catch {
      setConsentResult(FALLBACK_RESULT);
    }
    setStep("SUCCESS");
  }, [application]);

  const handleTamper = () => setTampered(true);

  const stepIndex: Record<Step, number> = { LANDING_CHOICE: 0, USE_DIGIIN: 1, CLAIMS_DISCOVERED: 2, SHARING_REVIEW: 3, CONSENT: 4, SUBMITTING: 5, SUCCESS: 6, PROOF_READY: 7, VERIFIER_VIEW: 8 };
  const totalSteps = 7;

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <div className="flex justify-end mb-2">
        <button type="button" onClick={() => setLocale(locale === "en" ? "hi" : "en")} className="text-xs font-bold text-[#0B5D9B] hover:underline cursor-pointer" aria-label="Switch language">
          {locale === "en" ? "हिन्दी में देखें" : "View in English"}
        </button>
      </div>
      <SandboxBanner />
      {step !== "LANDING_CHOICE" && <StepIndicator current={stepIndex[step]} total={totalSteps} />}

      {step === "LANDING_CHOICE" && (
        <div>
          <div className="bg-gradient-to-br from-[#0B5D9B] to-[#074B7D] text-white rounded-2xl p-8 mb-6">
            <div className="text-sm font-semibold opacity-80 mb-1">{hi ? "दिल्ली विश्वविद्यालय — DigiIn द्वारा संचालित" : "University of Delhi — Powered by DigiIn"}</div>
            <h1 className="text-2xl font-extrabold mb-2">{hi ? "राष्ट्रीय मेरिट-कम-मींस छात्रवृत्ति" : "National Merit-cum-Means Scholarship"}</h1>
            <p className="text-sm opacity-90">{hi ? "अपनी पूर्व-सत्यापित DigiIn जानकारी का उपयोग करके 2 मिनट में आवेदन करें।" : "Apply in 2 minutes using your pre-verified DigiIn information."}</p>
          </div>
          <div className="grid gap-4">
            <button type="button" onClick={handleUseDigiIn} data-testid="use-digiin-btn" className="w-full flex items-center gap-4 p-5 rounded-xl border-2 border-[#0B5D9B] bg-[#EBF4FA] hover:bg-[#DBEAFE] transition-all cursor-pointer text-left">
              <span className="text-3xl" aria-hidden="true">⚡</span>
              <div>
                <div className="font-extrabold text-[#092F4F] text-base">{hi ? "DigiIn से आवेदन करें" : "Use My Verified DigiIn Information"}</div>
                <div className="text-xs text-slate-600 mt-0.5">{hi ? "2 मिनट — कोई दस्तावेज़ अपलोड नहीं" : "2 minutes — zero document uploads"}</div>
              </div>
              <span className="ml-auto text-[#0B5D9B] text-xl" aria-hidden="true">→</span>
            </button>
            <div className="w-full flex items-center gap-4 p-5 rounded-xl border border-slate-200 bg-white opacity-60 text-left">
              <span className="text-3xl" aria-hidden="true">📄</span>
              <div>
                <div className="font-bold text-slate-600 text-base">{hi ? "परंपरागत तरीके से आवेदन करें" : "Apply Manually (Traditional)"}</div>
                <div className="text-xs text-slate-500 mt-0.5">{hi ? "30-45 मिनट — भौतिक दस्तावेज़ आवश्यक" : "30-45 minutes — physical documents required"}</div>
              </div>
            </div>
          </div>
          {onBack && <button type="button" onClick={onBack} className="mt-6 text-sm text-slate-500 hover:text-slate-800 cursor-pointer">← {hi ? "सेवाओं पर वापस जाएं" : "Back to Services"}</button>}
        </div>
      )}

      {step === "USE_DIGIIN" && (
        <div className="text-center py-12">
          <div className="inline-block w-10 h-10 border-4 border-[#0B5D9B] border-t-transparent rounded-full animate-spin mb-4" aria-label="Loading" />
          <div className="font-bold text-slate-700">{hi ? "DigiIn से आपकी जानकारी प्राप्त की जा रही है..." : "Fetching your verified information from DigiIn…"}</div>
        </div>
      )}

      {step === "CLAIMS_DISCOVERED" && (
        <div>
          <div className="bg-green-50 border border-green-200 rounded-xl p-5 mb-6">
            <div className="flex items-center gap-2 mb-1"><span className="text-green-600 text-xl" aria-hidden="true">✓</span><h2 className="font-extrabold text-green-800 text-lg">{hi ? "आपकी सत्यापित जानकारी तैयार है" : "Your Verified Information is Ready"}</h2></div>
            <p className="text-sm text-green-700">{hi ? "DigiIn को इस छात्रवृत्ति के लिए 4 पूर्व-सत्यापित दावे मिले।" : "DigiIn found 4 pre-verified claims for this scholarship. No documents to upload."}</p>
          </div>
          <div className="bg-white border border-slate-200 rounded-xl p-5 mb-6" data-testid="claims-panel">
            <div className="text-sm font-bold text-slate-500 uppercase tracking-wide mb-3">{hi ? "सत्यापित दावे" : "Verified Claims"}</div>
            {[{ label: hi ? "नाम" : "Name", value: "Rahul Sharma" }, { label: hi ? "अधिवास" : "Domicile", value: "Delhi" }, { label: hi ? "आय पात्रता" : "Income Eligibility", value: hi ? "पात्र ✓" : "Eligible ✓" }, { label: hi ? "शिक्षा" : "Education", value: "Class XII — Passed" }].map(c => <ClaimRow key={c.label} label={c.label} value={c.value} />)}
          </div>
          <button type="button" onClick={handleReviewSharing} data-testid="review-sharing-btn" className="w-full py-3 rounded-xl bg-[#0B5D9B] text-white font-extrabold hover:bg-[#074B7D] transition-all cursor-pointer">{hi ? "साझाकरण विवरण देखें →" : "Review Sharing Details →"}</button>
        </div>
      )}

      {(step === "SHARING_REVIEW" || step === "CONSENT") && sharingReview && (
        <div data-testid="consent-screen">
          <div className="bg-white border border-slate-200 rounded-xl p-5 mb-4">
            <div className="text-xs font-bold text-slate-400 uppercase tracking-wide mb-1">{hi ? "अनुरोधकर्ता" : "Requester"}</div>
            <div className="font-extrabold text-[#092F4F] text-lg">{sharingReview.requester_organization}</div>
            <div className="text-sm text-slate-600 mt-1"><span className="font-semibold">{hi ? "उद्देश्य:" : "Purpose:"}</span> {sharingReview.service_purpose}</div>
          </div>
          <div className="bg-green-50 border border-green-200 rounded-xl p-5 mb-4" data-testid="shared-claims-list">
            <div className="text-xs font-bold text-green-700 uppercase tracking-wide mb-3">{hi ? "✓ उन्हें चाहिए" : "✓ They Need"}</div>
            {sharingReview.shared_claims.map(c => <ClaimRow key={c.claim_key} label={c.claim_label} value={c.value_summary} isPredicate={c.is_predicate} />)}
          </div>
          <div className="bg-red-50 border border-red-200 rounded-xl p-5 mb-4" data-testid="withheld-section">
            <div className="text-xs font-bold text-red-700 uppercase tracking-wide mb-2">{hi ? "✕ उन्हें नहीं मिलेगा" : "✕ They Do NOT Receive"}</div>
            <WithheldRow label={hi ? "मूल दस्तावेज़ या स्कैन" : "Original documents or scans"} />
            <WithheldRow label={hi ? "आपका आधार नंबर" : "Your Aadhaar number"} />
            <WithheldRow label={hi ? "कोई अन्य क्रेडेंशियल" : "Any other credentials"} />
          </div>
          <div className="flex gap-3 mb-6">
            <div className="flex-1 bg-slate-50 border border-slate-200 rounded-xl p-3 text-center"><div className="text-xs text-slate-500 mb-0.5">{hi ? "पहुंच अवधि" : "Access Duration"}</div><div className="font-bold text-slate-800">{sharingReview.validity_hours} {hi ? "घंटे" : "hours"}</div></div>
            <div className="flex-1 bg-slate-50 border border-slate-200 rounded-xl p-3 text-center"><div className="text-xs text-slate-500 mb-0.5">{hi ? "फ़ाइल स्थानांतरण" : "File Transfer"}</div><div className="font-bold text-green-700">{sharingReview.raw_files_transferred_bytes} bytes</div></div>
          </div>
          {step === "SHARING_REVIEW" && (
            <div className="flex gap-3">
              <button type="button" onClick={() => setStep("LANDING_CHOICE")} data-testid="dont-share-btn" className="flex-1 py-3 rounded-xl border border-slate-300 text-slate-700 font-bold hover:bg-slate-100 transition-all cursor-pointer">{hi ? "साझा न करें" : "Don't Share"}</button>
              <button type="button" onClick={() => setStep("CONSENT")} data-testid="allow-continue-btn" className="flex-1 py-3 rounded-xl bg-[#0B5D9B] text-white font-extrabold hover:bg-[#074B7D] transition-all cursor-pointer">{hi ? "अनुमति दें और जारी रखें →" : "Allow & Continue →"}</button>
            </div>
          )}
          {step === "CONSENT" && (
            <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 mb-4">
              <div className="font-bold text-amber-800 mb-2">{hi ? "अंतिम पुष्टि" : "Final Confirmation"}</div>
              <p className="text-sm text-amber-700 mb-4">{hi ? "मैं समझता/समझती हूं कि केवल उपरोक्त 4 दावे साझा किए जाएंगे।" : "I confirm that only the 4 claims listed above will be shared. No raw documents."}</p>
              <button type="button" onClick={handleSubmit} data-testid="submit-btn" className="w-full py-3 rounded-xl bg-green-700 text-white font-extrabold hover:bg-green-800 transition-all cursor-pointer">{hi ? "आवेदन जमा करें ✓" : "Submit Application ✓"}</button>
            </div>
          )}
        </div>
      )}

      {step === "SUBMITTING" && (
        <div className="text-center py-12">
          <div className="inline-block w-10 h-10 border-4 border-green-600 border-t-transparent rounded-full animate-spin mb-4" aria-label="Submitting" />
          <div className="font-bold text-slate-700">{hi ? "आपका आवेदन जमा किया जा रहा है..." : "Submitting your application…"}</div>
        </div>
      )}

      {step === "SUCCESS" && consentResult && (
        <div>
          <div className="bg-green-600 text-white rounded-2xl p-8 mb-6 text-center" data-testid="success-screen">
            <div className="text-5xl mb-3" aria-hidden="true">🎉</div>
            <h2 className="text-2xl font-extrabold mb-2">{hi ? "आवेदन जमा हो गया!" : "Application Submitted!"}</h2>
            <p className="text-sm opacity-90">{hi ? "आपका छात्रवृत्ति आवेदन तुरंत सत्यापित और जमा कर दिया गया है।" : "Your scholarship application has been verified and submitted instantly."}</p>
            <div className="mt-4 bg-white/20 rounded-xl p-3 inline-block"><div className="text-xs font-bold opacity-80">{hi ? "प्रमाण ID" : "Proof ID"}</div><div className="font-mono font-extrabold text-lg" data-testid="proof-id">{consentResult.proof_token}</div></div>
          </div>
          <div className="grid grid-cols-3 gap-3 mb-6">
            {[{ label: hi ? "दावे साझा" : "Claims Shared", value: consentResult.claims_shared.toString() }, { label: hi ? "फ़ाइल स्थानांतरण" : "File Transfer", value: `${consentResult.raw_files_transferred_bytes}B` }, { label: hi ? "समय बचाया" : "Time Saved", value: "43 min" }].map(({ label, value }) => (
              <div key={label} className="bg-slate-50 border border-slate-200 rounded-xl p-3 text-center"><div className="text-xs text-slate-500 mb-0.5">{label}</div><div className="font-extrabold text-slate-800 text-lg">{value}</div></div>
            ))}
          </div>
          <div className="flex gap-3">
            <button type="button" onClick={() => setStep("PROOF_READY")} data-testid="view-proof-btn" className="flex-1 py-3 rounded-xl border-2 border-[#0B5D9B] text-[#0B5D9B] font-bold hover:bg-[#EBF4FA] transition-all cursor-pointer">{hi ? "प्रमाण देखें" : "View Proof"}</button>
            <button type="button" onClick={() => setStep("VERIFIER_VIEW")} data-testid="verify-as-institution-btn" className="flex-1 py-3 rounded-xl bg-[#0B5D9B] text-white font-bold hover:bg-[#074B7D] transition-all cursor-pointer">{hi ? "संस्था के रूप में सत्यापित करें" : "Verify as Institution"}</button>
          </div>
        </div>
      )}

      {step === "PROOF_READY" && consentResult && (
        <div>
          <h2 className="text-xl font-extrabold text-[#092F4F] mb-4">{hi ? "क्रिप्टोग्राफ़िक प्रमाण रसीद" : "Cryptographic Proof Receipt"}</h2>
          <div className="bg-white border border-slate-200 rounded-xl p-5 mb-4 font-mono text-sm" data-testid="proof-receipt">
            <div className="font-bold text-slate-500 text-xs mb-3 uppercase">{hi ? "प्रमाण" : "Proof"} #{consentResult.proof_token}</div>
            {!tampered ? (
              <>
                {[["Signature", "✓", "text-green-600"], ["Issuer", "✓", "text-green-600"], ["Audience", "✓", "text-green-600"], ["Expiry", "✓", "text-green-600"], ["Claims", "4/4 ✓", "text-green-600"]].map(([l, v, c]) => (
                  <div key={l} className="flex justify-between py-1.5 border-b border-slate-100 last:border-0"><span className="text-slate-600">{l}</span><span className={`font-bold ${c}`}>{v}</span></div>
                ))}
                <div className="mt-3 py-2 px-3 bg-green-50 border border-green-200 rounded-lg text-center"><span className="font-extrabold text-green-700 text-base">✓ {hi ? "सत्यापित" : "VERIFIED"}</span></div>
              </>
            ) : (
              <>
                <div className="bg-red-50 border border-red-300 rounded-lg p-3 mb-3"><div className="font-bold text-red-700 mb-1">{hi ? "दावे में बदलाव" : "CLAIM MODIFIED"}</div><div className="text-xs text-red-600">income_eligible: <span className="line-through">true</span> → <span className="font-bold">false</span></div></div>
                <div className="py-2 px-3 bg-red-600 rounded-lg text-center" data-testid="signature-invalid-msg"><span className="font-extrabold text-white text-base">✕ {hi ? "हस्ताक्षर अमान्य" : "SIGNATURE INVALID"}</span></div>
                <div className="mt-2 text-xs text-slate-500 text-center">{hi ? "हस्ताक्षर के बाद दावे में बदलाव किया गया। सत्यापन विफल।" : "Claim modified after signing. Proof rejected."}</div>
              </>
            )}
          </div>
          {!tampered && <button type="button" onClick={handleTamper} data-testid="tamper-btn" className="w-full py-3 rounded-xl border-2 border-red-400 text-red-700 font-bold hover:bg-red-50 transition-all cursor-pointer mb-3">⚡ {hi ? "प्रमाण से छेड़छाड़ करें (डेमो)" : "Tamper with Proof (Demo)"}</button>}
          <button type="button" onClick={() => setStep("SUCCESS")} className="w-full py-2 text-sm text-slate-500 hover:text-slate-700 cursor-pointer">← {hi ? "वापस जाएं" : "Back to Success"}</button>
        </div>
      )}

      {step === "VERIFIER_VIEW" && consentResult && (
        <div>
          <div className="bg-[#092F4F] text-white rounded-2xl p-6 mb-5" data-testid="institution-verifier-view">
            <div className="text-xs font-bold opacity-70 uppercase tracking-wide mb-1">{hi ? "संस्था सत्यापन दृश्य" : "Institution Verifier View"}</div>
            <h2 className="text-xl font-extrabold mb-1">{hi ? "दिल्ली विश्वविद्यालय (DEMO)" : "University of Delhi (DEMO)"}</h2>
          </div>
          <div className="bg-white border border-slate-200 rounded-xl p-5 mb-4">
            {!tampered ? (
              <>
                {[["Signature Integrity", "✓ Valid"], ["Issuer Trust", "✓ DigiIn DEMO"], ["Audience Match", "✓ srv_scholarship_du"], ["Expiry", "✓ Valid"], ["Claims Verified", "4/4 ✓"]].map(([l, v]) => (
                  <div key={l} className="flex justify-between py-2 border-b border-slate-100 last:border-0"><span className="text-sm text-slate-600">{l}</span><span className="text-sm font-bold text-green-600">{v}</span></div>
                ))}
                <div className="mt-4 py-3 bg-green-50 border border-green-200 rounded-xl text-center"><div className="font-extrabold text-green-700 text-lg">✓ {hi ? "सत्यापित" : "VERIFIED — Eligible for Scholarship"}</div></div>
              </>
            ) : (
              <div className="py-3 bg-red-50 border border-red-300 rounded-xl text-center" data-testid="verifier-rejection"><div className="font-extrabold text-red-700 text-lg">✕ {hi ? "अस्वीकृत — हस्ताक्षर अमान्य" : "REJECTED — Signature Invalid"}</div></div>
            )}
          </div>
          {!tampered && <button type="button" onClick={handleTamper} data-testid="tamper-btn" className="w-full py-3 rounded-xl border-2 border-red-400 text-red-700 font-bold hover:bg-red-50 transition-all cursor-pointer mb-3">⚡ {hi ? "प्रमाण से छेड़छाड़ करें (डेमो)" : "Tamper with Proof (Demo)"}</button>}
          {tampered && <div className="bg-red-50 border border-red-300 rounded-xl p-4 mb-3 text-sm text-red-700 text-center" data-testid="signature-invalid-msg"><div className="font-bold mb-1">{hi ? "हस्ताक्षर अमान्य ✕" : "SIGNATURE INVALID ✕"}</div></div>}
          <button type="button" onClick={() => setStep("SUCCESS")} className="w-full py-2 text-sm text-slate-500 hover:text-slate-700 cursor-pointer">← {hi ? "वापस जाएं" : "Back"}</button>
        </div>
      )}
    </div>
  );
};
