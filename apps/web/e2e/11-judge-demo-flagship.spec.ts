/**
 * 11-judge-demo-flagship.spec.ts
 *
 * DigiIn Phase 39 — Judge Demo Flagship E2E Specification
 * End-to-end Playwright test suite validating the complete 14-phase judge journey:
 * 1. Home Page & Navigation
 * 2. Services Directory & Filter
 * 3. 1-Click Demo Persona Switcher (Rahul Sharma / Priya Verma / DU / CBSE / Admin)
 * 4. Flagship Scholarship Application (0 raw bytes uploaded)
 * 5. Minimal Selective Disclosure & Consent Review
 * 6. Cryptographic Proof Minting & Receipt
 * 7. Verification Lab & Interactive Tamper Attack Demonstration
 * 8. 1-Click Sandbox Reset & Deterministic Seed Reproducibility
 */

import { test, expect } from "@playwright/test";

test.describe("Phase 39: Judge Demo Flagship Suite", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("header")).toBeVisible();
  });

  test("Step 1 — Home page renders branding, hero, trust badges, and navigation", async ({ page }) => {
    await expect(page.locator("h1")).toContainText(/Verify once/i);
    await expect(page.getByRole("button", { name: /Start Verification Journey/i })).toBeVisible();
    await expect(page.getByRole("button", { name: /Open Document Vault/i })).toBeVisible();
    await expect(page.locator("header")).toContainText(/UX4G 3.0/i);
  });

  test("Step 2 — Services catalog discovery, search & filtering", async ({ page }) => {
    // Navigate to Services Catalog
    await page.getByRole("button", { name: /🏛️ Services/i }).click();

    // Verify services header & cards
    await expect(page.locator("h1")).toContainText(/Public Services & Schemes/i);
    await expect(page.locator("body")).toContainText("National Merit-cum-Means Scholarship");
    await expect(page.locator("body")).toContainText("PM-Kisan & State Agricultural Subsidy");
    await expect(page.locator("body")).toContainText("Commercial Driver License Renewal");

    // Test Search input
    const searchInput = page.getByPlaceholder(/Search services/i);
    await searchInput.fill("Scholarship");
    await expect(page.locator("body")).toContainText("National Merit-cum-Means Scholarship");
  });

  test("Step 3 — 1-Click Demo Persona Sign-In (Rahul Sharma)", async ({ page }) => {
    await page.getByRole("button", { name: /Sign In/i }).click();
    await expect(page.locator("body")).toContainText("Select a Demo Persona for 1-click evaluation");

    // Click Rahul Sharma persona
    const rahulBtn = page.locator("button").filter({ hasText: "Rahul Sharma" }).first();
    await expect(rahulBtn).toBeVisible();
    await rahulBtn.click();

    // Should authenticate and navigate to Wallet Vault
    await expect(page.locator("header")).toContainText("Rahul Sharma");
  });

  test("Step 4 — Full Scholarship Journey with Consent & Cryptographic Proof Receipt", async ({ page }) => {
    // Start Scholarship
    await page.getByRole("button", { name: /🎓 Scholarship/i }).click();
    await expect(page.getByRole("alert").filter({ hasText: /SANDBOX DEMO/i })).toBeVisible();

    // Click Use DigiIn
    await page.getByTestId("use-digiin-btn").click();

    // Verify 4 claims discovered
    await expect(page.getByTestId("claims-panel")).toBeVisible({ timeout: 10000 });
    await expect(page.getByTestId("claims-panel")).toContainText("Name");
    await expect(page.getByTestId("claims-panel")).toContainText("Domicile");
    await expect(page.getByTestId("claims-panel")).toContainText("Income");
    await expect(page.getByTestId("claims-panel")).toContainText("Education");

    // Continue to Sharing Review
    await page.getByTestId("review-sharing-btn").click();
    await expect(page.getByTestId("consent-screen")).toBeVisible({ timeout: 8000 });

    // Verify zero raw document transfer
    await expect(page.getByTestId("withheld-section")).toContainText("Aadhaar");
    await expect(page.locator("body")).toContainText("0 bytes");

    // Approve consent
    await page.getByTestId("approve-consent-btn").click();

    // Verify success receipt
    await expect(page.getByTestId("success-screen")).toBeVisible({ timeout: 10000 });
    await expect(page.getByTestId("success-screen")).toContainText("0");
    await expect(page.getByTestId("success-screen")).toContainText("Cryptographically Verified");

    // View Proof & Test Tamper Rejection
    await page.getByTestId("view-proof-btn").click();
    await expect(page.getByTestId("proof-view")).toBeVisible();
    await expect(page.getByTestId("proof-view")).toContainText("VERIFIED");

    // Click Tamper with Proof
    await page.getByTestId("tamper-btn").click();
    await expect(page.getByTestId("signature-invalid-msg")).toBeVisible();
    await expect(page.getByTestId("signature-invalid-msg")).toContainText("SIGNATURE INVALID");
  });

  test("Step 5 — Verification Lab & 1-Click Sandbox Reset", async ({ page }) => {
    // Navigate to Verification Lab
    await page.getByRole("button", { name: /⚗️ Lab/i }).click();

    // Verify Demo Control Center & Lab Header
    await expect(page.locator("body")).toContainText("Judge & Evaluator Sandbox Controls");
    await expect(page.locator("body")).toContainText("Cryptographic Proof Verification Demo");

    // Click 1-Click Sandbox Reset
    const resetBtn = page.getByRole("button", { name: /⚡ 1-Click Sandbox Reset/i });
    await expect(resetBtn).toBeVisible();
    await resetBtn.click();

    // Verify reset alert appears
    await expect(page.locator("body")).toContainText(/Sandbox Deterministic State Restored/i);
  });
});
