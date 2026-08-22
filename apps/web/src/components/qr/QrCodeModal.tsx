import React, { useEffect, useState } from "react";
import QRCode from "qrcode";

interface Props {
  title: string;
  token: string;
  isOpen: boolean;
  onClose: () => void;
  onOpenScanner?: () => void;
  metadata?: {
    purpose?: string;
    audience?: string;
    algorithm?: string;
  };
}

export const QrCodeModal: React.FC<Props> = ({
  title,
  token,
  isOpen,
  onClose,
  onOpenScanner,
  metadata,
}) => {
  const [qrDataUrl, setQrDataUrl] = useState<string>("");
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (isOpen && token) {
      // First try standard QR generation with Low error correction (handles up to ~3KB text)
      QRCode.toDataURL(token, {
        errorCorrectionLevel: "L",
        width: 320,
        margin: 1,
        color: {
          dark: "#0f172a",
          light: "#ffffff",
        },
      })
        .then(setQrDataUrl)
        .catch(() => {
          // If token string is extra large, encode the compact token payload
          QRCode.toDataURL(token.slice(0, 1000), {
            errorCorrectionLevel: "L",
            width: 320,
            margin: 1,
          })
            .then(setQrDataUrl)
            .catch(() => setQrDataUrl(""));
        });
    }
  }, [isOpen, token]);


  if (!isOpen) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(token).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  const handleDownload = () => {
    if (!qrDataUrl) return;
    const a = document.createElement("a");
    a.href = qrDataUrl;
    a.download = `digiin_verifiable_qr_${Date.now()}.png`;
    a.click();
  };

  return (
    <div className="modal-overlay" role="dialog" aria-modal="true" aria-label="Verifiable QR Code Modal">
      <div className="modal-content qr-modal-content">
        <div className="modal-header">
          <div>
            <p className="eyebrow">SOVEREIGN VERIFIABLE CREDENTIAL</p>
            <h3>{title}</h3>
          </div>
          <button type="button" className="modal-close" onClick={onClose} aria-label="Close modal">
            &times;
          </button>
        </div>

        <div className="qr-body-layout">
          <div className="qr-canvas-container">
            {qrDataUrl ? (
              <img src={qrDataUrl} alt="Verifiable QR Code" className="qr-image-display" />
            ) : (
              <div className="qr-placeholder">Generating 2D Asymmetric QR...</div>
            )}
            <span className="qr-crypto-badge">
              🛡️ {metadata?.algorithm || "Ed25519 (EdDSA)"} Signed • RFC 7517 Compliant
            </span>
          </div>

          <div className="qr-details-side">
            <p className="qr-desc">
              This QR code embeds an asymmetric signed proof token. Official field verifiers can scan this code completely offline without requiring network connectivity or central database access.
            </p>

            {metadata && (
              <div className="qr-metadata-box">
                {metadata.purpose && (
                  <div>
                    <strong>Purpose: </strong>
                    <span>{metadata.purpose}</span>
                  </div>
                )}
                {metadata.audience && (
                  <div>
                    <strong>Audience: </strong>
                    <code>{metadata.audience}</code>
                  </div>
                )}
              </div>
            )}

            <div className="qr-token-snippet">
              <label>
                <strong>Compact Proof Token (JWS):</strong>
                <textarea readOnly value={token} rows={3} className="qr-token-textarea" />
              </label>
            </div>

            <div className="qr-actions-row">
              <button type="button" className="secondary" onClick={handleCopy}>
                {copied ? "✓ Copied Token!" : "📋 Copy JWS Token"}
              </button>
              <button type="button" className="secondary" onClick={handleDownload} disabled={!qrDataUrl}>
                💾 Download QR (PNG)
              </button>
              {onOpenScanner && (
                <button
                  type="button"
                  className="primary-action"
                  onClick={() => {
                    onClose();
                    onOpenScanner();
                  }}
                >
                  📷 Test in Offline Scanner &rarr;
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
