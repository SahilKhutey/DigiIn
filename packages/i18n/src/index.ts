import en from "./locales/en.json";
import hi from "./locales/hi.json";

export type Locale = "en" | "hi";

export const translations = {
  en,
  hi,
} as const;

export function getTranslation(key: string, locale: Locale = "en"): string {
  const parts = key.split(".");
  let current: any = translations[locale] || translations.en;

  for (const part of parts) {
    if (current && typeof current === "object" && part in current) {
      current = current[part];
    } else {
      // Fallback to English
      let fallback: any = translations.en;
      for (const p of parts) {
        if (fallback && typeof fallback === "object" && p in fallback) {
          fallback = fallback[p];
        } else {
          return key;
        }
      }
      return typeof fallback === "string" ? fallback : key;
    }
  }

  return typeof current === "string" ? current : key;
}

export const t = getTranslation;
