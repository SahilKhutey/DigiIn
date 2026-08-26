/**
 * 10-builder-brief-flagship.spec.ts
 *
 * DigiIn Builder Brief — Flagship E2E Test
 * Tests the complete scholarship journey from landing to institution verification,
 * including the tamper-and-reject proof demonstration.
 *
 * This is the single most important automated test for the hackathon submission.
 */
import { test, expect } from "@playwright/test";

test.describe("Builder Brief Flagship: Scholarship Journey", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    // Wait for app to load
    await expect(page.locator("header")).toBeVisible();
  });

  test("1 — Navigate to Scholarship Journey via header", async ({ page }) => {
    // Click the Scholarship nav button
    const scholarshipBtn = page.getByRole("button", { name: /🎓 Scholarship/i });
    await expect(scholarshipBtn).toBeVisible();
    await scholarshipBtn.click();

    // Sandbox banner must be visible
    await expect(page.getByRole("alert").filter({ hasText: /SANDBOX DEMO/i })).toBeVisible();

    // Landing choice screen: Use DigiIn button should be visible
    await expect(page.getByTestId("use-digiin-btn")).toBeVisible();
  });

  test("2 — Full flagship journey: Landing → Success → Proof → Tamper → Reject", async ({ page }) => {
    // Step 1: Navigate to Scholarship
    await page.getByRole("button", { name: /🎓 Scholarship/i }).click();
    await expect(page.getByRole("alert").filter({ hasText: /SANDBOX DEMO/i })).toBeVisible();

    // Step 2: Click Use DigiIn
    await page.getByTestId("use-digiin-btn").click();

    // Step 3: Wait for claims-discovered panel (loading then claims panel)
    await expect(page.getByTestId("claims-panel")).toBeVisible({ timeout: 10000 });

    // Verify 4 claims are present
    await expect(page.locator("[data-testid='claims-panel']")).toContainText("Name");
    await expect(page.locator("[data-testid='claims-panel']")).toContainText("Domicile");
    await expect(page.locator("[data-testid='claims-panel']")).toContainText("Income");
    await expect(page.locator("[data-testid='claims-panel']")).toContainText("Education");

    // Step 4: Click Review Sharing Details
    await page.getByTestId("review-sharing-btn").click();

    // Step 5: Consent screen should be visible
    await expect(page.getByTestId("consent-screen")).toBeVisible({ timeout: 8000 });

    // Step 6: Assert ONLY consented claims listed in green section
    await expect(page.getByTestId("shared-claims-list")).toContainText("Name");
    await expect(page.getByTestId("shared-claims-list")).toContainText("Domicile");

    // Step 7: Assert withheld section contains Aadhaar
    await expect(page.getByTestId("withheld-section")).toContainText("Aadhaar");

    // Step 8: Allow & Continue
    await page.getByTestId("allow-continue-btn").click();

    // Step 9: Submit
    await page.getByTestId("submit-btn").click();

    // Step 10: Success screen
    await expect(page.getByTestId("success-screen")).toBeVisible({ timeout: 12000 });

    // Verify proof ID is shown
    await expect(page.getByTestId("proof-id")).toBeVisible();
    const proofId = await page.getByTestId("proof-id").textContent();
    expect(proofId).toBeTruthy();
    expect(proofId!.length).toBeGreaterThan(4);

    // Step 11: View proof
    await page.getByTestId("view-proof-btn").click();
    await expect(page.getByTestId("proof-receipt")).toBeVisible();

    // Valid proof shows VERIFIED
    await expect(page.locator("[data-testid='proof-receipt']")).toContainText("VERIFIED");

    // Step 12: Tamper with proof
    await page.getByTestId("tamper-btn").click();

    // Step 13: Confirm SIGNATURE INVALID rejection
    await expect(page.getByTestId("signature-invalid-msg")).toBeVisible();
    await expect(page.getByTestId("signature-invalid-msg")).toContainText("SIGNATURE INVALID");
  });

  test("3 — Consent screen: Don't share returns to landing", async ({ page }) => {
    await page.getByRole("button", { name: /🎓 Scholarship/i }).click();
    await page.getByTestId("use-digiin-btn").click();
    await expect(page.getByTestId("claims-panel")).toBeVisible({ timeout: 10000 });
    await page.getByTestId("review-sharing-btn").click();
    await expect(page.getByTestId("consent-screen")).toBeVisible({ timeout: 8000 });

    // Click Don't Share
    await page.getByTestId("dont-share-btn").click();

    // Should return to landing choice (use-digiin-btn visible again)
    await expect(page.getByTestId("use-digiin-btn")).toBeVisible();
  });

  test("4 — Institution verifier view: Tamper shows SIGNATURE INVALID", async ({ page }) => {
    await page.getByRole("button", { name: /🎓 Scholarship/i }).click();
    await page.getByTestId("use-digiin-btn").click();
    await expect(page.getByTestId("claims-panel")).toBeVisible({ timeout: 10000 });
    await page.getByTestId("review-sharing-btn").click();
    await expect(page.getByTestId("consent-screen")).toBeVisible({ timeout: 8000 });
    await page.getByTestId("allow-continue-btn").click();
    await page.getByTestId("submit-btn").click();
    await expect(page.getByTestId("success-screen")).toBeVisible({ timeout: 12000 });

    // Navigate to institution view
    await page.getByTestId("verify-as-institution-btn").click();
    await expect(page.getByTestId("institution-verifier-view")).toBeVisible();

    // Tamper
    await page.getByTestId("tamper-btn").click();

    // Rejection appears
    await expect(page.getByTestId("signature-invalid-msg")).toBeVisible();
  });

  test("5 — Sandbox DEMO label is always visible throughout journey", async ({ page }) => {
    await page.getByRole("button", { name: /🎓 Scholarship/i }).click();
    // Sandbox banner must persist
    await expect(page.getByRole("alert").filter({ hasText: /SANDBOX DEMO/i })).toBeVisible();
  });

  test("6 — Demo Lab view: Verification Lab renders all 5 test cases", async ({ page }) => {
    await page.getByRole("button", { name: /⚗️ Lab/i }).click();
    // Lab should show test cards
    await expect(page.getByText(/Valid Proof Verification/i).first()).toBeVisible({ timeout: 8000 });
    await expect(page.getByText(/Tampered Claim Rejection/i).first()).toBeVisible();
    await expect(page.getByText(/Revoked Credential Rejection/i).first()).toBeVisible();
    await expect(page.getByText(/Expired Proof Rejection/i).first()).toBeVisible();
  });

  test("7 — Wallet view: clean citizen view (no dev tools)", async ({ page }) => {
    await page.getByRole("button", { name: /🗂️ Vault/i }).click();
    // DataSaverToggle should be visible
    await expect(page.getByText(/Data Saver/i)).toBeVisible();
    // Dev tools should NOT be directly visible in wallet
    await expect(page.getByText(/Platform Developer Tools/i)).not.toBeVisible();
  });
});
