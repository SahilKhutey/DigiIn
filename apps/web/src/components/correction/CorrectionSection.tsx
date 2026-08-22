import type {
  CorrectionRequestRecord,
  DocumentVersionRecord,
  PlatformSnapshot,
} from "../../types";
import { CorrectionForm } from "./CorrectionForm";
import { OfficerQueue } from "./OfficerQueue";
import { VersionChain } from "./VersionChain";

type CorrectionSectionProps = {
  snapshot: PlatformSnapshot | null;
  targetDocId: string;
  corrField: string;
  corrCurrentVal: string;
  corrProposedVal: string;
  corrReason: string;
  corrEvidenceDesc: string;
  docVersions: DocumentVersionRecord[];
  corrections: CorrectionRequestRecord[];
  onTargetDocChange: (docId: string) => void;
  onFieldChange: (val: string) => void;
  onCurrentValChange: (val: string) => void;
  onProposedValChange: (val: string) => void;
  onReasonChange: (val: string) => void;
  onEvidenceDescChange: (val: string) => void;
  onSubmitCorrection: () => void;
  onDecideCorrection: (requestId: string, decision: "APPROVE" | "REJECT") => void;
};

export function CorrectionSection({
  snapshot,
  targetDocId,
  corrField,
  corrCurrentVal,
  corrProposedVal,
  corrReason,
  corrEvidenceDesc,
  docVersions,
  corrections,
  onTargetDocChange,
  onFieldChange,
  onCurrentValChange,
  onProposedValChange,
  onReasonChange,
  onEvidenceDescChange,
  onSubmitCorrection,
  onDecideCorrection,
}: CorrectionSectionProps) {
  const hasDocs = Boolean(snapshot && snapshot.documents.length > 0);

  return (
    <section id="correction" className="card" aria-labelledby="correction-title">
      <div className="card-heading">
        <div>
          <p className="eyebrow">MY RECORD IS WRONG</p>
          <h2 id="correction-title">Correction & Versioning Lifecycle</h2>
        </div>
        <span className="badge pending">immutable provenance</span>
      </div>
      <p className="summary">
        DigiIn cannot directly mutate official government source records, and correction never
        destroys historical evidence. Filing a correction creates a review case for the issuing
        authority. When approved, a new version (<code>v2</code>) is issued while prior versions (
        <code>v1</code>) transition to <strong>SUPERSEDED</strong>.
      </p>

      {hasDocs && snapshot ? (
        <div>
          <label>
            <strong>Select Document to Correct: </strong>
            <select
              value={targetDocId}
              onChange={(e) => onTargetDocChange(e.target.value)}
              aria-label="Select Document to Correct"
            >
              {snapshot.documents.map((d) => (
                <option key={d.documentId} value={d.documentId}>
                  {d.documentType} ({d.documentId}) — Current: v{d.currentVersion} [{d.status}]
                </option>
              ))}
            </select>
          </label>

          <CorrectionForm
            field={corrField}
            currentVal={corrCurrentVal}
            proposedVal={corrProposedVal}
            reason={corrReason}
            evidenceDesc={corrEvidenceDesc}
            onFieldChange={onFieldChange}
            onCurrentValChange={onCurrentValChange}
            onProposedValChange={onProposedValChange}
            onReasonChange={onReasonChange}
            onEvidenceDescChange={onEvidenceDescChange}
            onSubmit={onSubmitCorrection}
          />

          <OfficerQueue
            documentId={targetDocId}
            corrections={corrections}
            onDecide={onDecideCorrection}
          />

          <VersionChain versions={docVersions} />
        </div>
      ) : (
        <div
          style={{
            padding: "16px",
            background: "#f8fafc",
            borderRadius: "8px",
            border: "1px dashed #94a3b8",
          }}
        >
          <p style={{ margin: 0, color: "#475569" }}>
            Click <strong>"Run student vertical slice"</strong> above to register an active document
            and inspect the live correction and versioning engine.
          </p>
        </div>
      )}
    </section>
  );
}
