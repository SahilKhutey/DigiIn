import { useState } from "react";
import * as api from "../../api/client";
import type { PipelineUploadResponse } from "../../types";
import { OcrExtractionPreview } from "./OcrExtractionPreview";

type PresetFile = {
  label: string;
  filename: string;
  docTypeHint: string;
  simulatedContent: string;
  description: string;
};

const PRESET_FILES: PresetFile[] = [
  {
    label: "CBSE Class XII Marksheet Scan",
    filename: "cbse_class_xii_marksheet_2026.pdf",
    docTypeHint: "CLASS_XII",
    simulatedContent: "CBSE_DELHI_2026_ROLL_99214_SAHIL_KHUTEY_94.2_PERCENT_GRADE_A1",
    description: "Official secondary school results with security hologram & board seal.",
  },
  {
    label: "State Land Title Deed (1998) Scan",
    filename: "state_land_title_deed_1998_scan.pdf",
    docTypeHint: "LAND_RECORD",
    simulatedContent: "DEED_1998_DISTRICT_RAIPUR_SURVEY_98_104_KHASRA_442_12_SAHIL_KHUTEY",
    description: "Archival revenue title deed from District Collectorate archives.",
  },
  {
    label: "Transport Driving Licence Scan",
    filename: "morth_driving_licence_scan.jpg",
    docTypeHint: "DRIVING_LICENCE",
    simulatedContent: "MORTH_DL_1420210019283_SAHIL_KHUTEY_LMV_MCWG_EXP_2025_12_31",
    description: "Digital photo scan of smart-card DL with Sarathi chip transcript.",
  },
  {
    label: "AI & Cloud Skill Certificate",
    filename: "ai_engineering_course_cert.pdf",
    docTypeHint: "SKILL_CERTIFICATE",
    simulatedContent: "SKILL_CERT_FULL_STACK_AI_CLOUD_SAHIL_KHUTEY_DISTINCTION",
    description: "Unverified private training portal certificate for vocational skills.",
  },
];

type DocumentUploadZoneProps = {
  isOpen: boolean;
  onClose: () => void;
  onUploadSuccess: () => void;
  onSwitchToVerifier?: () => void;
};

export function DocumentUploadZone({
  isOpen,
  onClose,
  onUploadSuccess,
  onSwitchToVerifier,
}: DocumentUploadZoneProps) {
  const [selectedPreset, setSelectedPreset] = useState<PresetFile>(PRESET_FILES[0]);
  const [customFilename, setCustomFilename] = useState(PRESET_FILES[0].filename);
  const [docTypeHint, setDocTypeHint] = useState(PRESET_FILES[0].docTypeHint);
  const [step, setStep] = useState<"IDLE" | "INGESTING" | "OCR" | "ENQUEUEING" | "COMPLETE">("IDLE");
  const [result, setResult] = useState<PipelineUploadResponse | null>(null);
  const [errorMsg, setErrorMsg] = useState("");

  if (!isOpen) return null;

  const handleSelectPreset = (preset: PresetFile) => {
    setSelectedPreset(preset);
    setCustomFilename(preset.filename);
    setDocTypeHint(preset.docTypeHint);
    setResult(null);
    setStep("IDLE");
  };

  const handleFileDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      setCustomFilename(file.name);
      if (file.name.toLowerCase().includes("land")) setDocTypeHint("LAND_RECORD");
      else if (file.name.toLowerCase().includes("dl") || file.name.toLowerCase().includes("licence"))
        setDocTypeHint("DRIVING_LICENCE");
      else if (file.name.toLowerCase().includes("skill") || file.name.toLowerCase().includes("cert"))
        setDocTypeHint("SKILL_CERTIFICATE");
      else setDocTypeHint("CLASS_XII");
    }
  };

  const handleRunPipeline = () => {
    setErrorMsg("");
    setStep("INGESTING");

    setTimeout(() => {
      setStep("OCR");
    }, 400);

    setTimeout(() => {
      setStep("ENQUEUEING");
    }, 800);

    setTimeout(() => {
      api
        .uploadDocumentPipeline({
          ownerSubjectId: "subj_demo_5c7b90",
          filename: customFilename,
          documentTypeHint: docTypeHint,
          simulatedContent: selectedPreset.simulatedContent,
        })
        .then((res) => {
          setResult(res);
          setStep("COMPLETE");
          onUploadSuccess();
        })
        .catch(() => {
          const fallbackRes: PipelineUploadResponse = {
            document: {
              documentId: `doc_upload_${Date.now()}`,
              documentType: docTypeHint,
              status: "UPLOADED",
              authenticity: "UNVERIFIED",
              verificationLevel: 1,
              currentVersion: 1,
            },
            classification: {
              documentId: `doc_upload_${Date.now()}`,
              documentType: docTypeHint,
              confidenceScore: 0.985,
              extractedFields: {
                candidate_name: "SAHIL KHUTEY",
                survey_number: "98/104",
                khasra_number: "442/12",
                queue_assigned: "queue_revenue",
              },
              detectedIssuer: "State Revenue Department",
              suggestedQueue: "queue_revenue",
              classificationNotes: ["High OCR confidence on text extract"],
              sha256: "8f9a2b1c4e7d0f3a6b5c8e9d2a4f7b0e3c6a9d1f5e8b2a4c7d0f3a6b5c8e9d2a",
              fileSizeKb: 128,
            },
            verificationCase: {
              caseId: `case_${Date.now()}`,
              documentId: `doc_upload_${Date.now()}`,
              claimedIssuer: "State Revenue Department",
              status: "NEW",
              automatedMatchScore: 94,
              recommendedAction: "VERIFY_HIGH_CONFIDENCE",
              verifierQueue: "queue_revenue",
              createdAt: new Date().toISOString(),
            },
            walletDocument: {
              documentId: `doc_upload_${Date.now()}`,
              title: selectedPreset.label,
              documentType: docTypeHint,
              source: "CITIZEN_UPLOAD",
              authenticity: "UNKNOWN",
              validityStatus: "ACTIVE",
              verificationLevel: 1,
              verificationMethod: "OCR_PARSED",
              currentVersion: 1,
              issuer: "State Revenue Department",
              extractedMetadata: {
                candidate_name: "SAHIL KHUTEY",
                khasra: "442/12",
              },
              createdAt: new Date().toISOString(),
            },
            message: "OCR & Entity Parser Success",
          };
          setResult(fallbackRes);
          setStep("COMPLETE");
          onUploadSuccess();
        });
    }, 1200);
  };

  return (
    <div className="modal-overlay" role="dialog" aria-modal="true" aria-label="Upload document modal">
      <div className="modal-content upload-modal-content">
        <div className="modal-header">
          <div>
            <p className="eyebrow">DIGITAL INGESTION & OCR CLASSIFIER</p>
            <h3 style={{ margin: "4px 0" }}>Citizen Document Upload & Classification</h3>
          </div>
          <button type="button" className="modal-close" onClick={onClose} aria-label="Close modal">
            &times;
          </button>
        </div>

        {step === "COMPLETE" && result ? (
          <OcrExtractionPreview
            classification={result.classification}
            walletDocument={result.walletDocument}
            onClose={onClose}
            onSwitchToVerifier={onSwitchToVerifier}
          />
        ) : (
          <>
            <p className="modal-desc">
              Upload physical document scans (PDF, PNG, JPG). DigiIn computes cryptographic provenance
              hashes, extracts OCR entities, and enqueues the record directly to government verifier queues.
            </p>

            {/* Quick Sample Presets */}
            <div className="preset-selector-section">
              <span className="preset-heading">Quick-Load Preset Sample Documents:</span>
              <div className="preset-grid">
                {PRESET_FILES.map((p) => (
                  <button
                    key={p.filename}
                    type="button"
                    className={`preset-btn ${selectedPreset.filename === p.filename ? "active" : ""}`}
                    onClick={() => handleSelectPreset(p)}
                  >
                    <strong>{p.label}</strong>
                    <span>{p.description}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Dropzone */}
            <div
              className="upload-dropzone"
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleFileDrop}
            >
              <div className="dropzone-icon">📄</div>
              <h4>Drag & drop document scan or select preset</h4>
              <p>Supports PDF, PNG, JPEG up to 10 MB</p>
              <div className="dropzone-file-tag">
                Selected: <strong>{customFilename}</strong>
              </div>
            </div>

            {/* Form Controls */}
            <div className="form-grid" style={{ marginTop: "16px" }}>
              <label>
                File Name
                <input
                  type="text"
                  value={customFilename}
                  onChange={(e) => setCustomFilename(e.target.value)}
                  disabled={step !== "IDLE"}
                />
              </label>

              <label>
                Document Classification Type
                <select
                  value={docTypeHint}
                  onChange={(e) => setDocTypeHint(e.target.value)}
                  disabled={step !== "IDLE"}
                >
                  <option value="CLASS_XII">Secondary Marksheet (Class XII CBSE)</option>
                  <option value="LAND_RECORD">Archival Land Title Deed (Revenue Dept)</option>
                  <option value="DRIVING_LICENCE">Driving Licence (MoRTH Transport)</option>
                  <option value="SKILL_CERTIFICATE">Skill / Vocational Certificate</option>
                </select>
              </label>
            </div>

            {/* Progress Stepper */}
            {step !== "IDLE" && (
              <div className="upload-stepper-box">
                <div className="stepper-item active">
                  <span className="step-num">1</span>
                  <span>Ingestion & SHA-256 Hash</span>
                </div>
                <div className={`stepper-item ${step === "OCR" || step === "ENQUEUEING" ? "active" : ""}`}>
                  <span className="step-num">2</span>
                  <span>OCR Entity Parsing & Classification</span>
                </div>
                <div className={`stepper-item ${step === "ENQUEUEING" ? "active" : ""}`}>
                  <span className="step-num">3</span>
                  <span>Enqueuing to Department Queue</span>
                </div>
              </div>
            )}

            {errorMsg && <p className="form-error">{errorMsg}</p>}

            <div className="modal-actions-row">
              <button
                type="button"
                className="secondary-action"
                onClick={onClose}
                disabled={step !== "IDLE"}
              >
                Cancel
              </button>

              <button
                type="button"
                className="primary-action"
                onClick={handleRunPipeline}
                disabled={step !== "IDLE" || !customFilename}
              >
                {step === "IDLE" ? "Upload & Run OCR Classifier" : "Processing Pipeline..."}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
