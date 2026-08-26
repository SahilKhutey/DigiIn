import React, { useState } from "react";
import { Button, Card, FormField, Select } from "../../components/ui";
import { useLanguage } from "../../context/LanguageContext";

interface UploadPipelineViewProps {
  onBackToWallet: () => void;
  onSavedToWallet: () => void;
}

export const UploadPipelineView: React.FC<UploadPipelineViewProps> = ({
  onBackToWallet,
  onSavedToWallet,
}) => {
  const { locale } = useLanguage();
  const hi = locale === "hi";

  const [selectedPreset, setSelectedPreset] = useState<string>("cbse_xii");
  const [isProcessing, setIsProcessing] = useState(false);
  const [extractedData, setExtractedData] = useState<{
    docType: string;
    confidence: string;
    fields: { label: string; value: string }[];
  } | null>(null);

  const presets: Record<string, {
    label: string;
    docType: string;
    confidence: string;
    fields: { label: string; value: string }[];
  }> = {
    cbse_xii: {
      label: "CBSE Class XII Certificate (Sample)",
      docType: "Senior Secondary School Certificate (CBSE)",
      confidence: "98.7% High Confidence Match",
      fields: [
        { label: "Candidate Name", value: "RAHUL SHARMA" },
        { label: "Roll Number", value: "26182910" },
        { label: "Passing Year", value: "2026" },
        { label: "Institution", value: "Delhi Public School, R.K. Puram" },
        { label: "Result Status", value: "PASSED (First Division with Distinction)" },
      ],
    },
    dl_sarathi: {
      label: "MoRTH Driving License (Sample)",
      docType: "Motor Vehicle Driving License (MoRTH)",
      confidence: "99.2% High Confidence Match",
      fields: [
        { label: "License Holder", value: "RAHUL SHARMA" },
        { label: "License Number", value: "DL-0420260019283" },
        { label: "Vehicle Class", value: "LMV / MCWG (Non-Transport)" },
        { label: "Validity", value: "Valid till 14 May 2046" },
        { label: "Issuing Authority", value: "RTO Janakpuri, New Delhi" },
      ],
    },
    domicile_delhi: {
      label: "Delhi State Domicile Certificate (Sample)",
      docType: "State Domicile Certificate (Govt. of NCT Delhi)",
      confidence: "97.5% High Confidence Match",
      fields: [
        { label: "Resident Name", value: "RAHUL SHARMA" },
        { label: "Certificate No.", value: "DOM-DEL-2026-918" },
        { label: "Residency Duration", value: "Continuous (Since Birth)" },
        { label: "Tehsil", value: "Vasant Vihar, South West Delhi" },
      ],
    },
  };

  const handleSimulateOcr = (key: string) => {
    setSelectedPreset(key);
    setIsProcessing(true);
    setExtractedData(null);
    setTimeout(() => {
      setExtractedData(presets[key]);
      setIsProcessing(false);
    }, 600);
  };

  return (
    <div className="space-y-8 max-w-4xl mx-auto py-2">
      {/* Top Back Action */}
      <div className="flex items-center justify-between">
        <button
          type="button"
          onClick={onBackToWallet}
          className="inline-flex items-center gap-1.5 text-sm font-bold text-[#0B5D9B] hover:underline cursor-pointer"
        >
          ← {hi ? "वॉलेट पर वापस" : "Back to Document Wallet"}
        </button>

        <span className="text-xs font-semibold text-slate-500">
          ClamAV Virus Protection: <strong className="text-emerald-700">ACTIVE</strong>
        </span>
      </div>

      {/* Main Upload Box */}
      <div className="bg-white border border-[#CBD5E1] rounded-3xl p-6 md:p-8 shadow-xs space-y-6">
        <div className="space-y-2">
          <h1 className="text-2xl md:text-3xl font-extrabold text-[#092F4F] m-0">
            {hi ? "दस्तावेज़ अपलोड और OCR निष्कर्षण" : "Self-Upload & OCR Pipeline"}
          </h1>
          <p className="text-xs md:text-sm text-slate-600 m-0">
            Digitize physical certificates with automatic OCR classification, structured schema extraction, and level 4 registry matching.
          </p>
        </div>

        {/* 1-Click Sample Test Presets */}
        <div className="p-4 bg-[#F8FAFC] border border-slate-200 rounded-2xl space-y-2">
          <div className="text-xs font-bold text-slate-500 uppercase tracking-wide">
            ⚡ Quick Test Presets (Click to Simulate Instant OCR):
          </div>
          <div className="flex flex-wrap gap-2">
            {Object.entries(presets).map(([key, item]) => (
              <button
                key={key}
                type="button"
                onClick={() => handleSimulateOcr(key)}
                className={`px-3 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                  selectedPreset === key && extractedData
                    ? "bg-[#0B5D9B] text-white shadow-xs"
                    : "bg-white border border-slate-300 text-slate-700 hover:bg-slate-50"
                }`}
              >
                📄 {item.label}
              </button>
            ))}
          </div>
        </div>

        {/* Drag & Drop Visual Box */}
        <div
          onClick={() => handleSimulateOcr(selectedPreset)}
          className="border-2 border-dashed border-[#0B5D9B]/50 hover:border-[#0B5D9B] bg-[#F3F7FA] hover:bg-[#EBF4FA] rounded-2xl p-8 text-center cursor-pointer transition-all space-y-3"
        >
          <div className="w-14 h-14 rounded-full bg-white shadow-xs border border-slate-200 flex items-center justify-center text-3xl mx-auto">
            📤
          </div>
          <div>
            <div className="font-extrabold text-sm text-[#092F4F]">
              Drop PDF, JPG, or PNG files here, or click to browse
            </div>
            <div className="text-xs text-slate-500 mt-1">
              Supports documents up to 10MB. End-to-end encrypted storage.
            </div>
          </div>
        </div>

        {/* Loading Spinner */}
        {isProcessing && (
          <div className="text-center py-8 space-y-3">
            <div className="inline-block w-8 h-8 border-4 border-[#0B5D9B] border-t-transparent rounded-full animate-spin" />
            <div className="text-xs font-bold text-slate-700">
              Scanning with ClamAV & Running Tesseract OCR Extraction Engine…
            </div>
          </div>
        )}

        {/* Extracted Data Preview */}
        {extractedData && !isProcessing && (
          <div className="space-y-4 pt-4 border-t border-slate-200">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-xs font-bold text-slate-400 uppercase tracking-wide">
                  Classified Document
                </div>
                <h3 className="text-lg font-bold text-[#092F4F] m-0">
                  {extractedData.docType}
                </h3>
              </div>

              <span className="text-xs font-extrabold px-3 py-1 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-300">
                ✓ {extractedData.confidence}
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
              {extractedData.fields.map((f, i) => (
                <div key={i} className="p-3.5 bg-[#F8FAFC] border border-slate-200 rounded-xl">
                  <div className="text-slate-500 font-medium">{f.label}</div>
                  <div className="text-sm font-bold text-[#092F4F] mt-0.5">{f.value}</div>
                </div>
              ))}
            </div>

            <div className="pt-4 flex flex-col sm:flex-row gap-3">
              <Button
                variant="primary"
                size="lg"
                fullWidth
                onClick={onSavedToWallet}
                className="font-bold shadow-xs"
              >
                Save to Encrypted Wallet & Request Registry Verification →
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
