import { useLanguage } from "../../context/LanguageContext";

export function LanguageToggle() {
  const { locale, setLocale } = useLanguage();

  return (
    <div className="language-selector" role="group" aria-label="Language selection mode">
      <button
        type="button"
        className={`lang-btn ${locale === "en" ? "active" : ""}`}
        onClick={() => setLocale("en")}
        aria-pressed={locale === "en"}
        title="Switch to English"
      >
        🇬🇧 English
      </button>
      <button
        type="button"
        className={`lang-btn ${locale === "hi" ? "active" : ""}`}
        onClick={() => setLocale("hi")}
        aria-pressed={locale === "hi"}
        title="हिन्दी में बदलें"
      >
        🇮🇳 हिन्दी
      </button>
    </div>
  );
}
