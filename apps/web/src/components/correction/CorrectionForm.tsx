type CorrectionFormProps = {
  field: string;
  currentVal: string;
  proposedVal: string;
  reason: string;
  evidenceDesc: string;
  onFieldChange: (val: string) => void;
  onCurrentValChange: (val: string) => void;
  onProposedValChange: (val: string) => void;
  onReasonChange: (val: string) => void;
  onEvidenceDescChange: (val: string) => void;
  onSubmit: () => void;
};

export function CorrectionForm({
  field,
  currentVal,
  proposedVal,
  reason,
  evidenceDesc,
  onFieldChange,
  onCurrentValChange,
  onProposedValChange,
  onReasonChange,
  onEvidenceDescChange,
  onSubmit,
}: CorrectionFormProps) {
  return (
    <div>
      <div className="form-grid">
        <label>
          Field to Correct
          <input
            type="text"
            value={field}
            onChange={(e) => onFieldChange(e.target.value)}
            placeholder="e.g. student_name"
          />
        </label>
        <label>
          Current Value in Record
          <input
            type="text"
            value={currentVal}
            onChange={(e) => onCurrentValChange(e.target.value)}
            placeholder="e.g. SAHIL KHTEY"
          />
        </label>
        <label>
          Proposed Corrected Value
          <input
            type="text"
            value={proposedVal}
            onChange={(e) => onProposedValChange(e.target.value)}
            placeholder="e.g. SAHIL KHUTEY"
          />
        </label>
        <label>
          Reason for Correction
          <input
            type="text"
            value={reason}
            onChange={(e) => onReasonChange(e.target.value)}
            placeholder="e.g. Transcription spelling error"
          />
        </label>
      </div>

      <label
        style={{
          display: "grid",
          gap: "6px",
          marginTop: "12px",
          color: "#244a65",
          fontWeight: 700,
          fontSize: ".9rem",
        }}
      >
        Supporting Evidence Reference
        <input
          type="text"
          value={evidenceDesc}
          onChange={(e) => onEvidenceDescChange(e.target.value)}
          placeholder="e.g. Secondary School Certificate & Aadhaar eKYC Name Transcript"
        />
      </label>

      <div style={{ marginTop: "16px" }}>
        <button type="button" onClick={onSubmit}>
          Submit correction request
        </button>
      </div>
    </div>
  );
}
