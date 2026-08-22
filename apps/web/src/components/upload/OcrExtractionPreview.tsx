import type { DocumentClassificationResult, WalletDocument } from "../../types";

type OcrExtractionPreviewProps = {
  classification: DocumentClassificationResult;
  walletDocument: WalletDocument;
  onClose: () => void;
  onSwitchToVerifier?: () => void;
};

export function OcrExtractionPreview({
  classification,
  walletDocument,
  onClose,
  onSwitchToVerifier,
}: OcrExtractionPreviewProps) {
  return (
    <div className="ocr-preview-card" aria-label="OCR Extraction and Classification Results">
      <div className="ocr-preview-header">
        <div>
          <span className="badge active">OCR & Entity Parser Success</span>
          <h3>{walletDocument.title}</h3>
          <p className="ocr-meta">
            Target Queue: <code>{classification.suggestedQueue}</code> • Level:{" "}
            <strong>Level 2 (Enqueued for Officer Review)</strong>
          </p>
        </div>

        <div className="match-score-card">
          <span className="score-label">OCR Confidence</span>
          <div className="score-badge-row">
            <span
              className={`score-badge ${
                classification.confidenceScore >= 85
                  ? "high-match"
                  : classification.confidenceScore >= 65
                  ? "med-match"
                  : "low-match"
              }`}
            >
              {classification.confidenceScore}%
            </span>
          </div>
        </div>
      </div>

      {/* SHA-256 Provenance Digest */}
      <div className="sha-provenance-box">
        <span className="sha-label">SHA-256 Document Checksum:</span>
        <code>{classification.sha256}</code>
      </div>

      {/* Extracted Fields Table */}
      <div className="extracted-fields-table-wrapper">
        <h4>Extracted Structured Entities</h4>
        <table className="comparison-table">
          <thead>
            <tr>
              <th>Entity Key</th>
              <th>Extracted Value</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(classification.extractedFields).map(([key, val]) => (
              <tr key={key}>
                <td>
                  <strong>{key.replace(/_/g, " ").toUpperCase()}</strong>
                </td>
                <td>
                  <code className="claim-text citizen-claim">{String(val)}</code>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Classification Notes */}
      {classification.classificationNotes.length > 0 && (
        <div className="classification-notes-box">
          <strong>OCR Classifier Intelligence Notes:</strong>
          <ul>
            {classification.classificationNotes.map((note, i) => (
              <li key={i}>{note}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Actions */}
      <div className="ocr-preview-actions">
        <button type="button" className="primary-action" onClick={onClose}>
          Done • View in Citizen Wallet
        </button>
        {onSwitchToVerifier && (
          <button
            type="button"
            className="secondary-action"
            onClick={() => {
              onClose();
              onSwitchToVerifier();
            }}
          >
            Switch to Verifier Console to Review
          </button>
        )}
      </div>
    </div>
  );
}
