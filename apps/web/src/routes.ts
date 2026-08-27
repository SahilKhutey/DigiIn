/**
 * DigiIn Central Route Map
 * Single authoritative source of truth for all public, citizen, and console route paths.
 */
export const routes = {
  home: "/",
  services: "/services",
  howItWorks: "/how-it-works",
  trust: "/trust",
  support: "/support",
  login: "/login",
  register: "/register",
  otp: "/verify",
  dashboard: "/dashboard",
  identity: "/identity",
  documents: "/documents",
  upload: "/documents/upload",
  credentials: "/credentials",
  verification: "/verification",
  proofs: "/proofs",
  sharing: "/sharing",
  activity: "/activity",
  notifications: "/notifications",
  corrections: "/corrections",
  settings: "/settings",
  issuer: "/issuer",
  verifier: "/verifier",
  admin: "/admin",
  scholarship: "/scholarship",
  zkStudio: "/zk-studio",
  sandbox: "/sandbox",
} as const;

export type AppRoute = typeof routes[keyof typeof routes];
