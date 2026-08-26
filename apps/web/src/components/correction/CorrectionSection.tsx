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

const FALLBACK_SNAPSHOT_DOCS = [
  { documentId: "doc_cbse_xii_2026", documentType: "CLASS_XII_CERTIFICATE", currentVersion: 1, status: "ACTIVE" },
];

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
  const docsList = snapshot?.documents?.length ? snapshot.documents : FALLBACK_SNAPSHOT_DOCS;
  const currentDocId = targetDocId || docsList[0].documentId;

  return (
    <section id="correction" className="card space-y-4" aria-labelledby="correction-title">
      <div className="card-heading">
        <div>
          <h2 id="correction-title" className="text-2xl font-extrabold text-[#092F4F] m-0">Correction & Versioning Lifecycle</h2>
          <p className="text-xs text-slate-500 m-0 mt-0.5">Report a problem — tell us what is incorrect in this document.</p>
        </div>
        <span className="badge pending">Immutable Lineage</span>
      </div>

      <div>
        <label>
          <strong>Select Document to Correct: </strong>
          <select
            value={currentDocId}
            onChange={(e) => onTargetDocChange(e.target.value)}
            aria-label="Select Document to Correct"
          >
            {docsList.map((d) => (
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
          documentId={currentDocId}
          corrections={corrections}
          onDecide={onDecideCorrection}
        />

        <VersionChain versions={docVersions} />
      </div>
    </section>
  );
}
