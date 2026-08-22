import { createContext, useContext, useState, ReactNode } from "react";

export type Locale = "en" | "hi";

const TRANSLATIONS = {
  en: {
    "app.title": "DigiLocker X",
    "app.subtitle": "• Sovereign Document Trust Platform",
    "nav.wallet": "Document Wallet",
    "nav.proof": "Verify Proof",
    "nav.ekyc": "eKYC Gateway",
    "nav.correction": "Correct Record",
    "nav.recovery": "Recovery",
    "nav.privacy": "Privacy First",
    "role.citizen": "🗂️ Citizen Wallet",
    "role.verifier": "🏛️ Verifier Console",
    "role.consent": "🛡️ Consent & Audit",
    "btn.scanner": "📷 Offline QR Scanner",
    "banner.title": "Sovereign Verifiable Credentials Active",
    "banner.desc": "Zero raw document files are ever transferred to third-party requesters. Verifications execute via cryptographically signed Ed25519 claims.",
    "lang.en": "English",
    "lang.hi": "हिन्दी",
  },
  hi: {
    "app.title": "डिजिलॉकर एक्स (DigiLocker X)",
    "app.subtitle": "• संप्रभु दस्तावेज़ विश्वास मंच",
    "nav.wallet": "दस्तावेज़ वॉलेट",
    "nav.proof": "प्रमाण सत्यापन",
    "nav.ekyc": "ई-केवाईसी गेटवे",
    "nav.correction": "रिकॉर्ड सुधार",
    "nav.recovery": "पुनर्प्राप्ति",
    "nav.privacy": "गोपनीयता प्राथमिकता",
    "role.citizen": "🗂️ नागरिक वॉलेट",
    "role.verifier": "🏛️ सत्यापनकर्ता कंसोल",
    "role.consent": "🛡️ सहमति और ऑडिट",
    "btn.scanner": "📷 ऑफ़लाइन क्यूआर स्कैनर",
    "banner.title": "संप्रभु सत्यापन योग्य प्रमाणपत्र सक्रिय",
    "banner.desc": "तृतीय-पक्ष अनुरोधकर्ताओं को कभी कोई कच्चा दस्तावेज़ स्थानांतरित नहीं किया जाता है। सत्यापन क्रिप्टोग्राफ़िक रूप से हस्ताक्षरित Ed25519 दावों के माध्यम से निष्पादित होते हैं।",
    "lang.en": "English",
    "lang.hi": "हिन्दी",
  },
} as const;

type LanguageContextType = {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  t: (key: keyof typeof TRANSLATIONS.en) => string;
};

const LanguageContext = createContext<LanguageContextType>({
  locale: "en",
  setLocale: () => {},
  t: (key) => TRANSLATIONS.en[key] || key,
});

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [locale, setLocale] = useState<Locale>("en");

  const t = (key: keyof typeof TRANSLATIONS.en): string => {
    const dict = TRANSLATIONS[locale] || TRANSLATIONS.en;
    return dict[key] || TRANSLATIONS.en[key] || key;
  };

  return (
    <LanguageContext.Provider value={{ locale, setLocale, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  return useContext(LanguageContext);
}
