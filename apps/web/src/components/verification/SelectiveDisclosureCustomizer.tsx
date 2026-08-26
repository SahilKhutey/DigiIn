import React, { useState, useEffect } from "react";
import type {
  VerificationRequirement,
  SelectiveDisclosurePreference,
} from "../../types";

interface Props {
  requirements: VerificationRequirement[];
  onPreferenceChange: (pref: SelectiveDisclosurePreference) => void;
}

const KNOWN_CREDENTIAL_ATTRIBUTES: Record<string, { label: string; pii: boolean }[]> = {
  CLASS_XII: [
    { label: "qualification", pii: false },
    { label: "passing_year", pii: false },
    { label: "qualification_status", pii: false },
    { label: "board", pii: false },
    { label: "percentage", pii: true },
    { label: "roll_number", pii: true },
    { label: "school_code", pii: true },
  ],
  CLASS_XII_CERTIFICATE: [
    { label: "qualification", pii: false },
    { label: "passing_year", pii: false },
    { label: "qualification_status", pii: false },
    { label: "board", pii: false },
    { label: "percentage", pii: true },
    { label: "roll_number", pii: true },
    { label: "school_code", pii: true },
  ],
  DOMICILE: [
    { label: "jurisdiction", pii: false },
    { label: "residence_verified", pii: false },
    { label: "district", pii: true },
    { label: "ward_number", pii: true },
  ],
  AGE_OVER_18: [
    { label: "age_requirement_met", pii: false },
    { label: "date_of_birth", pii: true },
    { label: "aadhaar_ref", pii: true },
  ],
  GRADUATION: [
    { label: "qualification", pii: false },
    { label: "course", pii: false },
    { label: "issue_year", pii: false },
    { label: "cgpa", pii: true },
    { label: "enrollment_no", pii: true },
  ],
};

const DEFAULT_PREDICATES: Record<string, string> = {
  CLASS_XII: "Age Threshold >= 18 & 12th Board Result == PASSED (Score >= 50%)",
  CLASS_XII_CERTIFICATE: "Age Threshold >= 18 & 12th Board Result == PASSED (Score >= 50%)",
  DOMICILE: "State Domicile == CHHATTISGARH",
  AGE_OVER_18: "Age Threshold >= 18 Years (Legal Age)",
  GRADUATION: "Degree == BACHELORS",
};

export const SelectiveDisclosureCustomizer: React.FC<Props> = ({
  requirements,
  onPreferenceChange,
}) => {
  const [mode, setMode] = useState<"PREDICATE_ONLY" | "SELECTIVE_ATTRIBUTES" | "FULL_DOCUMENT">("PREDICATE_ONLY");

  // Collect all available attributes across requirements
  const initialSelected: Record<string, boolean> = {};
  requirements.forEach((req) => {
    const known = KNOWN_CREDENTIAL_ATTRIBUTES[req.credential] || [];
    known.forEach((attr) => {
      // Default select non-PII attributes
      initialSelected[`${req.credential}.${attr.label}`] = !attr.pii;
    });
  });

  const [selectedFields, setSelectedFields] = useState<Record<string, boolean>>(initialSelected);
  const onPrefChangeRef = React.useRef(onPreferenceChange);
  onPrefChangeRef.current = onPreferenceChange;

  // Sync preference upwards whenever mode or selections change
  useEffect(() => {
    const chosenAttrs = Object.entries(selectedFields)
      .filter(([_, val]) => val)
      .map(([key]) => key.split(".")[1] || key);

    const chosenPreds = requirements.map((r) => r.credential);

    onPrefChangeRef.current({
      mode,
      selectedAttributes: chosenAttrs,
      selectedPredicates: chosenPreds,
    });
  }, [mode, selectedFields, requirements.length]);


  const toggleField = (fieldKey: string) => {
    setSelectedFields((prev) => ({
      ...prev,
      [fieldKey]: !prev[fieldKey],
    }));
  };

  return (
    <div className="selective-disclosure-customizer">
      <div className="customizer-header">
        <h4>🛡️ Privacy & Selective Disclosure Controls</h4>
        <span className="privacy-badge">Zero-Knowledge Enabled</span>
      </div>
      <p className="customizer-desc">
        Choose how much data you share with the requesting authority. DigiIn generates asymmetric cryptographic proofs to verify eligibility without exposing raw documents.
      </p>

      {/* Mode Selector */}
      <div className="disclosure-mode-tabs">
        <button
          type="button"
          className={`mode-tab ${mode === "PREDICATE_ONLY" ? "active" : ""}`}
          onClick={() => setMode("PREDICATE_ONLY")}
        >
          <span className="tab-icon">🛡️</span>
          <div className="tab-text">
            <strong>Zero-Knowledge Predicates</strong>
            <small>Only proves eligibility (Recommended)</small>
          </div>
        </button>

        <button
          type="button"
          className={`mode-tab ${mode === "SELECTIVE_ATTRIBUTES" ? "active" : ""}`}
          onClick={() => setMode("SELECTIVE_ATTRIBUTES")}
        >
          <span className="tab-icon">📋</span>
          <div className="tab-text">
            <strong>Selective Attributes</strong>
            <small>Choose individual fields to share</small>
          </div>
        </button>

        <button
          type="button"
          className={`mode-tab ${mode === "FULL_DOCUMENT" ? "active" : ""}`}
          onClick={() => setMode("FULL_DOCUMENT")}
        >
          <span className="tab-icon">📄</span>
          <div className="tab-text">
            <strong>Full Credential Mode</strong>
            <small>Complete transcript disclosure</small>
          </div>
        </button>
      </div>

      {/* Attribute Checkboxes (When in Selective Attributes Mode) */}
      {mode === "SELECTIVE_ATTRIBUTES" && (
        <div className="selective-fields-panel">
          <h5>Select Fields to Disclose:</h5>
          <div className="fields-grid">
            {requirements.map((req) => {
              const known = KNOWN_CREDENTIAL_ATTRIBUTES[req.credential] || [];
              return (
                <div key={req.credential} className="credential-field-group">
                  <span className="group-title">{req.credential.replace(/_/g, " ")}</span>
                  <div className="field-checkboxes">
                    {known.map((attr) => {
                      const fieldKey = `${req.credential}.${attr.label}`;
                      const isChecked = !!selectedFields[fieldKey];
                      return (
                        <label
                          key={fieldKey}
                          className={`field-checkbox-label ${isChecked ? "checked" : ""} ${
                            attr.pii ? "pii-tag" : ""
                          }`}
                        >
                          <input
                            type="checkbox"
                            checked={isChecked}
                            onChange={() => toggleField(fieldKey)}
                          />
                          <span className="field-name">{attr.label}</span>
                          {attr.pii && <span className="pii-badge">Sensitive PII</span>}
                        </label>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Live Disclosed vs. Masked Matrix */}
      <div className="disclosure-matrix-container">
        <div className="matrix-column disclosed-column">
          <div className="column-header">
            <span className="col-icon">👁️</span>
            <strong>What the Requester Will Receive</strong>
          </div>
          <div className="column-content">
            {mode === "PREDICATE_ONLY" && (
              <ul className="proof-list">
                {requirements.map((req) => (
                  <li key={req.credential} className="proof-item">
                    <span className="check-icon">✓</span>
                    <div className="proof-details">
                      <strong>{DEFAULT_PREDICATES[req.credential] || `${req.credential}: ELIGIBLE`}</strong>
                      <span className="zk-proof-tag">Cryptographic Proof: SATISFIED (TRUE)</span>
                    </div>
                  </li>
                ))}
              </ul>
            )}

            {mode === "SELECTIVE_ATTRIBUTES" && (
              <ul className="disclosed-attr-list">
                {Object.entries(selectedFields)
                  .filter(([_, val]) => val)
                  .map(([k]) => (
                    <li key={k} className="disclosed-attr-item">
                      <span className="check-icon">✓</span>
                      <code>{k}</code>
                    </li>
                  ))}
              </ul>
            )}

            {mode === "FULL_DOCUMENT" && (
              <div className="full-notice">
                <span className="warning-icon">⚠️</span>
                <p>All attributes across the requested credentials will be transmitted to the requester.</p>
              </div>
            )}
          </div>
        </div>

        <div className="matrix-column masked-column">
          <div className="column-header">
            <span className="col-icon">🔒</span>
            <strong>What Stays Private & Masked</strong>
          </div>
          <div className="column-content">
            {mode === "PREDICATE_ONLY" && (
              <ul className="masked-list">
                <li><span className="lock-icon">🔒</span> Date of Birth & Aadhaar Reference</li>
                <li><span className="lock-icon">🔒</span> Examination Roll Number & Center Code</li>
                <li><span className="lock-icon">🔒</span> Exact Percentage / Marks Transcript</li>
                <li><span className="lock-icon">🔒</span> Physical Residential Address & Ward Number</li>
              </ul>
            )}

            {mode === "SELECTIVE_ATTRIBUTES" && (
              <ul className="masked-list">
                {Object.entries(selectedFields)
                  .filter(([_, val]) => !val)
                  .map(([k]) => (
                    <li key={k}>
                      <span className="lock-icon">🔒</span>
                      <code>{k} (Masked)</code>
                    </li>
                  ))}
              </ul>
            )}

            {mode === "FULL_DOCUMENT" && (
              <p className="no-masked-notice">No fields are masked in full document mode.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
