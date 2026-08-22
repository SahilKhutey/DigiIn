type HeaderProps = {
  viewMode: "CITIZEN" | "VERIFIER" | "CONSENT";
  onViewModeChange: (mode: "CITIZEN" | "VERIFIER" | "CONSENT") => void;
};

export function Header({ viewMode, onViewModeChange }: HeaderProps) {
  return (
    <header>
      <p className="brand">
        DigiIn <span>• Document trust platform</span>
      </p>

      {/* Role Switcher Pill */}
      <div className="role-switcher" role="group" aria-label="Perspective switcher">
        <button
          type="button"
          className={`role-btn ${viewMode === "CITIZEN" ? "active" : ""}`}
          onClick={() => onViewModeChange("CITIZEN")}
        >
          🗂️ Citizen Wallet
        </button>
        <button
          type="button"
          className={`role-btn ${viewMode === "VERIFIER" ? "active" : ""}`}
          onClick={() => onViewModeChange("VERIFIER")}
        >
          🏛️ Verifier Console
        </button>
        <button
          type="button"
          className={`role-btn ${viewMode === "CONSENT" ? "active" : ""}`}
          onClick={() => onViewModeChange("CONSENT")}
        >
          🛡️ Consent & Audit
        </button>
      </div>

      {viewMode === "CITIZEN" && (
        <nav aria-label="Main navigation">
          <a href="#wallet">Document Wallet</a>
          <a href="#proof">Verify proof</a>
          <a href="#correction">Correct record</a>
          <a href="#recovery">Recover</a>
          <a href="#privacy">Privacy first</a>
        </nav>
      )}
    </header>
  );
}


