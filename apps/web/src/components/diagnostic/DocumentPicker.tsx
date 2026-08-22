import type { DocumentOption } from "../../types";

type DocumentPickerProps = {
  documents: DocumentOption[];
  selectedDocumentId: string;
  onSelectDocument: (id: string) => void;
};

export function DocumentPicker({
  documents,
  selectedDocumentId,
  onSelectDocument,
}: DocumentPickerProps) {
  const selectedDoc =
    documents.find((item) => item.id === selectedDocumentId) ?? documents[0];

  return (
    <section className="intent scenario-picker" aria-labelledby="intent-title">
      <div>
        <p className="eyebrow">1. START WITH THE OUTCOME</p>
        <h2 id="intent-title">What document do you need?</h2>
      </div>
      <label>
        Document type
        <select
          value={selectedDocumentId}
          onChange={(e) => onSelectDocument(e.target.value)}
          aria-label="Document type selection"
        >
          {documents.map((item) => (
            <option key={item.id} value={item.id}>
              {item.label} — {item.category}
            </option>
          ))}
        </select>
      </label>
      <div className="trust">
        <strong>{selectedDoc?.trustLabel}</strong>
        <span>
          Trust label: this prototype never treats a user-uploaded file as an official issued record.
        </span>
      </div>
    </section>
  );
}
