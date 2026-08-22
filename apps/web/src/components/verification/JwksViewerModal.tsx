import { useEffect, useState } from "react";
import * as api from "../../api/client";
import type { JwksResponse } from "../../types";

type JwksViewerModalProps = {
  isOpen: boolean;
  onClose: () => void;
};

export function JwksViewerModal({ isOpen, onClose }: JwksViewerModalProps) {
  const [jwksData, setJwksData] = useState<JwksResponse | null>(null);
  const [activeTab, setActiveTab] = useState<"CARDS" | "RAW_JSON">("CARDS");
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (isOpen) {
      api
        .fetchJwks()
        .then((data) => setJwksData(data))
        .catch(() => undefined);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleCopyRaw = () => {
    if (jwksData) {
      navigator.clipboard.writeText(JSON.stringify(jwksData, null, 2)).then(() => {
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      });
    }
  };

  return (
    <div className="modal-overlay" role="dialog" aria-modal="true" aria-label="Public JWKS Key Registry">
      <div className="modal-content jwks-modal-content">
        <div className="modal-header">
          <div>
            <p className="eyebrow">RFC 7517 PUBLIC KEY DISCOVERY</p>
            <h3 style={{ margin: "4px 0" }}>Sovereign Public JWKS Explorer</h3>
          </div>
          <button type="button" className="modal-close" onClick={onClose} aria-label="Close modal">
            &times;
          </button>
        </div>

        <p className="modal-desc">
          Relying parties (universities, employers, state agencies) verify proof tokens offline using
          these public keys. Discovery endpoint: <code>/.well-known/jwks.json</code>
        </p>

        {/* Tab Controls */}
        <div className="jwks-tab-bar">
          <button
            type="button"
            className={`jwks-tab-btn ${activeTab === "CARDS" ? "active" : ""}`}
            onClick={() => setActiveTab("CARDS")}
          >
            Visual Key Inspector ({jwksData?.keys.length ?? 0} Keys)
          </button>
          <button
            type="button"
            className={`jwks-tab-btn ${activeTab === "RAW_JSON" ? "active" : ""}`}
            onClick={() => setActiveTab("RAW_JSON")}
          >
            Raw RFC 7517 JSON
          </button>
        </div>

        {activeTab === "CARDS" ? (
          <div className="jwks-keys-grid">
            {jwksData?.keys.map((key) => (
              <div key={key.kid} className="jwk-card">
                <div className="jwk-card-header">
                  <div>
                    <span className="jwk-alg-badge">{key.alg}</span>
                    <h4 className="jwk-kid">{key.kid}</h4>
                  </div>
                  <span className="jwk-kty-tag">Type: {key.kty}</span>
                </div>

                <div className="jwk-props-list">
                  <div className="jwk-prop-row">
                    <span className="jwk-prop-label">Key Usage:</span>
                    <code>{key.use} (Digital Signature)</code>
                  </div>
                  {key.crv && (
                    <div className="jwk-prop-row">
                      <span className="jwk-prop-label">Curve:</span>
                      <code>{key.crv}</code>
                    </div>
                  )}
                  {key.x && (
                    <div className="jwk-prop-row">
                      <span className="jwk-prop-label">Public Coordinate (x):</span>
                      <code className="jwk-coord-text">{key.x}</code>
                    </div>
                  )}
                  {key.n && (
                    <div className="jwk-prop-row">
                      <span className="jwk-prop-label">Modulus (n):</span>
                      <code className="jwk-coord-text">{key.n.substring(0, 48)}...</code>
                    </div>
                  )}
                  {key.e && (
                    <div className="jwk-prop-row">
                      <span className="jwk-prop-label">Exponent (e):</span>
                      <code>{key.e}</code>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="raw-json-container">
            <pre className="raw-json-code">
              {jwksData ? JSON.stringify(jwksData, null, 2) : "Loading..."}
            </pre>
          </div>
        )}

        <div className="modal-actions-row" style={{ marginTop: "20px" }}>
          <button type="button" className="secondary-action" onClick={handleCopyRaw}>
            {copied ? "✓ Copied JSON" : "📋 Copy JWKS JSON"}
          </button>
          <button type="button" className="primary-action" onClick={onClose}>
            Done
          </button>
        </div>
      </div>
    </div>
  );
}
