import { useLanguage } from "../../context/LanguageContext";
import { LanguageToggle } from "./LanguageToggle";

type HeaderProps = {
  viewMode: "CITIZEN" | "VERIFIER" | "CONSENT";
  onViewModeChange: (mode: "CITIZEN" | "VERIFIER" | "CONSENT") => void;
  onOpenScanner?: () => void;
};

export function Header({ viewMode, onViewModeChange, onOpenScanner }: HeaderProps) {
  const { t } = useLanguage();

  return (
    <header>
      <div className="header-left">
        <p className="brand">
          {t("app.title")} <span>{t("app.subtitle")}</span>
        </p>
      </div>

      {/* Role Switcher Pill */}
      <div className="role-switcher" role="group" aria-label="Perspective switcher">
        <button
          type="button"
          className={`role-btn ${viewMode === "CITIZEN" ? "active" : ""}`}
          onClick={() => onViewModeChange("CITIZEN")}
        >
          {t("role.citizen")}
        </button>
        <button
          type="button"
          className={`role-btn ${viewMode === "VERIFIER" ? "active" : ""}`}
          onClick={() => onViewModeChange("VERIFIER")}
        >
          {t("role.verifier")}
        </button>
        <button
          type="button"
          className={`role-btn ${viewMode === "CONSENT" ? "active" : ""}`}
          onClick={() => onViewModeChange("CONSENT")}
        >
          {t("role.consent")}
        </button>
        {onOpenScanner && (
          <button
            type="button"
            className="scanner-header-btn"
            onClick={onOpenScanner}
            title="Air-gapped offline asymmetric cryptographic proof verification"
          >
            {t("btn.scanner")}
          </button>
        )}
      </div>

      <div className="header-right">
        <LanguageToggle />
      </div>

      {viewMode === "CITIZEN" && (
        <nav aria-label="Main navigation">
          <a href="#wallet">{t("nav.wallet")}</a>
          <a href="#proof">{t("nav.proof")}</a>
          <a href="#ekyc">{t("nav.ekyc")}</a>
          <a href="#correction">{t("nav.correction")}</a>
          <a href="#recovery">{t("nav.recovery")}</a>
          <a href="#privacy">{t("nav.privacy")}</a>
        </nav>
      )}
    </header>
  );
}
