import { useState } from "react";
import type {
  SelectiveDisclosurePreference,
  TokenCheck,
  VerificationRequest,
  VerificationResult,
} from "../../types";
import { JwksViewerModal } from "./JwksViewerModal";
import { SelectiveDisclosureCustomizer } from "./SelectiveDisclosureCustomizer";
import { TokenIntrospect } from "./TokenIntrospect";
import { QrCodeModal } from "../qr/QrCodeModal";

type ProofGatewayProps = {
  verificationRequest: VerificationRequest | null;
  verificationResult: VerificationResult | null;
  tokenCheck: TokenCheck | null;
  onCreateRequest: () => void;
  onAuthorize: (customDisclosure?: SelectiveDisclosurePreference) => void;
  onIntrospect: () => void;
  onOpenScanner?: () => void;
};

export function ProofGateway({
  verificationRequest,
  verificationResult,
  tokenCheck,
  onCreateRequest,
  onAuthorize,
  onIntrospect,
  onOpenScanner,
}: ProofGatewayProps) {
  const [isJwksOpen, setIsJwksOpen] = useState(false);
  const [showQrModal, setShowQrModal] = useState(false);
  const [disclosurePref, setDisclosurePref] = useState<SelectiveDisclosurePreference | undefined>(undefined);


  return (
    <section id="proof" className="card proof-card" aria-labelledby="proof-title">
      <div className="card-heading">
        <div>
          <p className="eyebrow">VERIFICATION GATEWAY</p>
          <h2 id="proof-title">Prove eligibility without uploading documents</h2>
        </div>
        <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
          <button
            type="button"
            className="secondary"
            onClick={() => setIsJwksOpen(true)}
            style={{ margin: 0, padding: "6px 12px", fontSize: ".8rem" }}
          >
            🔑 Public JWKS Keys
          </button>
          <span className="badge resolved">Ed25519 & RS256 Asymmetric</span>
        </div>
      </div>
      <p className="summary">
        A requester asks a question such as “does this citizen meet the exam eligibility
        requirements?” DigiIn returns an asymmetric cryptographic proof signed with sovereign Ed25519 keys,
        verifiable offline via RFC 7517 public JWKS discovery.
      </p>

      <div className="proof-actions">
        <button type="button" onClick={onCreateRequest}>
          Create exam proof request
        </button>
        <button
          className="secondary"
          type="button"
          onClick={() => onAuthorize(disclosurePref)}
          disabled={!verificationRequest || Boolean(verificationResult)}
        >
          Authorize & Issue Proof
        </button>
        <button
          className="secondary"
          type="button"
          onClick={onIntrospect}
          disabled={!verificationResult}
        >
          Validate proof token
        </button>
        {verificationResult && (
          <button
            className="primary-action qr-trigger-btn"
            type="button"
            onClick={() => setShowQrModal(true)}
          >
            📱 View Verifiable QR Code
          </button>
        )}
      </div>


      {verificationRequest && !verificationResult && (
        <section className="consent-panel" aria-label="Consent request">
          <p className="eyebrow">CONSENT REQUEST</p>
          <h3>{verificationRequest.requesterName}</h3>
          <p>{verificationRequest.consentText}</p>
          <div className="request-grid">
            <p>
              <strong>Purpose</strong>
              <span>{verificationRequest.purpose}</span>
            </p>
            <p>
              <strong>Audience</strong>
              <span>{verificationRequest.audience}</span>
            </p>
            <p>
              <strong>Disclosure</strong>
              <span>{verificationRequest.disclosure.mode}</span>
            </p>
          </div>
          <ul className="requirement-list">
            {verificationRequest.requirements.map((item) => (
              <li key={item.credential}>
                <strong>{item.credential}</strong>
                <span>
                  Minimum level {item.minimumLevel}
                  {item.attributes.length ? ` • ${item.attributes.join(", ")}` : ""}
                </span>
              </li>
            ))}
          </ul>

          {/* Interactive Selective Disclosure & Zero-Knowledge Predicate Customizer */}
          <SelectiveDisclosureCustomizer
            requirements={verificationRequest.requirements}
            onPreferenceChange={(pref) => setDisclosurePref(pref)}
          />
        </section>
      )}

      {verificationResult && (
        <section className="result-panel" aria-label="Verification result">
          <div className="stage-title">
            <h3>Verification receipt</h3>
            <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
              {verificationResult.maskedAttributesSummary && verificationResult.maskedAttributesSummary.length > 0 && (
                <span className="badge resolved">
                  🔒 {verificationResult.maskedAttributesSummary.length} PII Fields Masked
                </span>
              )}
              <span className="badge active">
                {verificationResult.proof.algorithm || "EdDSA"} Asymmetric Proof
              </span>
            </div>
          </div>
          <div className="health-grid">
            <p>
              <strong>Verification ID</strong>
              <span>{verificationResult.verificationId}</span>
            </p>
            <p>
              <strong>Disclosure Level</strong>
              <span>{verificationResult.disclosureLevel}</span>
            </p>
            <p>
              <strong>Document shared</strong>
              <span>{verificationResult.receipt.documentShared ? "Yes" : "No (Zero Raw Files)"}</span>
            </p>
          </div>

          {/* Derived Zero-Knowledge Predicate Proofs */}
          {verificationResult.predicateProofs && verificationResult.predicateProofs.length > 0 && (
            <div className="predicate-receipt-block">
              <h4>🛡️ Derived Zero-Knowledge Predicate Proofs:</h4>
              <ul className="predicate-receipt-list">
                {verificationResult.predicateProofs.map((pred) => (
                  <li key={pred.predicateId} className="predicate-receipt-item">
                    <span className="pred-icon">✓</span>
                    <div>
                      <strong>{pred.expression}</strong>
                      <span className="pred-claim">{pred.claimName} • SATISFIED (TRUE)</span>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}

          <ol className="proof-results">
            {verificationResult.results.map((item) => (
              <li
                key={item.credential}
                className={item.verified ? "complete" : "attention"}
              >
                <strong>{item.credential}</strong>
                <span>
                  {item.status} • Level {item.level} • {item.issuer ?? "No issuer"}
                </span>
                {Object.keys(item.disclosedAttributes).length > 0 ? (
                  <code>{JSON.stringify(item.disclosedAttributes)}</code>
                ) : (
                  <span className="zero-pii-label">🛡️ Zero raw attributes disclosed (Predicate Proof Only)</span>
                )}
                {item.maskedAttributes && item.maskedAttributes.length > 0 && (
                  <div className="masked-tags">
                    <small>Masked fields:</small>{" "}
                    {item.maskedAttributes.map((m) => (
                      <span key={m} className="masked-tag-pill">
                        🔒 {m}
                      </span>
                    ))}
                  </div>
                )}
              </li>
            ))}
          </ol>
          <p className="token-preview">
            <strong>Signed proof token ({verificationResult.proof.algorithm || "EdDSA"})</strong>
            <code>{verificationResult.proof.token.slice(0, 96)}...</code>
          </p>
        </section>
      )}

      <TokenIntrospect tokenCheck={tokenCheck} onOpenJwks={() => setIsJwksOpen(true)} />

      <JwksViewerModal isOpen={isJwksOpen} onClose={() => setIsJwksOpen(false)} />

      {verificationResult && (
        <QrCodeModal
          isOpen={showQrModal}
          onClose={() => setShowQrModal(false)}
          onOpenScanner={onOpenScanner}
          title="Verifiable Examination Eligibility Proof"
          token={verificationResult.proof.token}
          metadata={{
            purpose: verificationRequest?.purpose,
            audience: verificationRequest?.audience,
            algorithm: verificationResult.proof.algorithm,
          }}
        />
      )}
    </section>
  );
}



