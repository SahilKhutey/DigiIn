import { useState } from "react";
import * as api from "../../api/client";
import type { Diagnostic, SupportSafeSummary } from "../../types";
import { PrintableSupportSheet } from "./PrintableSupportSheet";
import { RecoveryAction } from "./RecoveryAction";

type DiagnosticTimelineProps = {
  diagnostic: Diagnostic;
  scenarioId?: string;
  onRetry: () => void;
  onCopyEvidence: () => void;
};

const FALLBACK_SUPPORT_SUMMARY: SupportSafeSummary = {
  supportCode: "DIGIIN-DEMO-IM-2026",
  timestamp: new Date().toISOString(),
  scenarioId: "identity-mismatch",
  failureStage: "Identity Verification & Name Match",
  diagnosticTitle: "Issuer Record Discrepancy",
  plainLanguageExplanation: "The issuing registry responded with a mismatch in candidate name spelling.",
  affectedAuthority: "Central Board of Secondary Education",
  issuerStatus: "available",
  correlationId: "corr_diag_882910",
  guidanceForCitizen: [
    "Verify spelling against Aadhaar card",
    "Submit an official correction appeal to CBSE",
  ],
  guidanceForDeskOfficer: [
    "Inspect physical certificate scan",
    "Compare with Gazette roll notification",
  ],
  securityNotice: "ZERO PII • No personal credentials stored in this sheet.",
  qrDigest: "SHA256:8f9a2b1c4e7d0f3a6b5c8e9d2a4f7b0e",
};

export function DiagnosticTimeline({
  diagnostic,
  scenarioId = "identity-mismatch",
  onRetry,
  onCopyEvidence,
}: DiagnosticTimelineProps) {
  const [isSheetOpen, setIsSheetOpen] = useState(false);
  const [supportSummary, setSupportSummary] = useState<SupportSafeSummary | null>(FALLBACK_SUPPORT_SUMMARY);

  const handleOpenSupportSheet = () => {
    api
      .fetchSupportSummary(scenarioId)
      .then((data) => {
        setSupportSummary(data);
        setIsSheetOpen(true);
      })
      .catch(() => {
        setSupportSummary(FALLBACK_SUPPORT_SUMMARY);
        setIsSheetOpen(true);
      });
  };

  return (
    <section id="recovery" className="card" aria-labelledby="journey-title">
      <div className="card-heading">
        <div>
          <p className="eyebrow">3. DOCUMENT HEALTH</p>
          <h2 id="journey-title">{diagnostic.documentLabel}</h2>
        </div>
        <span className={`badge ${diagnostic.overallStatus}`}>
          {diagnostic.overallStatus.replace("_", " ")}
        </span>
      </div>

      <div className="health-grid">
        <p>
          <strong>Trust</strong>
          <span>{diagnostic.trustLabel}</span>
        </p>
        <p>
          <strong>Issuer status</strong>
          <span className={diagnostic.issuerStatus}>{diagnostic.issuerStatus}</span>
        </p>
        <p>
          <strong>Diagnostic code</strong>
          <span>{diagnostic.issueCode}</span>
        </p>
      </div>

      <p className="summary">{diagnostic.summary}</p>

      <ol className="timeline" aria-label="Diagnostic step progression">
        {diagnostic.steps.map((item) => (
          <li key={item.name} className={item.status}>
            <div className="marker" aria-hidden="true">
              {item.status === "complete"
                ? "OK"
                : item.status === "attention"
                ? "!"
                : item.status === "blocked"
                ? "X"
                : "·"}
            </div>
            <article>
              <div className="stage-title">
                <h3>{item.name}</h3>
                <span>{item.owner}</span>
              </div>
              <p>{item.message}</p>
              {item.nextAction && (
                <div className="next">
                  <strong>What you can do now</strong>
                  <p>{item.nextAction}</p>
                </div>
              )}
            </article>
          </li>
        ))}
      </ol>

      <RecoveryAction
        diagnostic={diagnostic}
        onRetry={onRetry}
        onCopyEvidence={onCopyEvidence}
        onOpenSupportSheet={handleOpenSupportSheet}
      />

      <PrintableSupportSheet
        summary={supportSummary}
        isOpen={isSheetOpen}
        onClose={() => setIsSheetOpen(false)}
      />
    </section>
  );
}

