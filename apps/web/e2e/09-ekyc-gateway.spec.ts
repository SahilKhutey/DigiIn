import { test, expect } from "@playwright/test";

test.describe("Aadhaar / eKYC Mock Gateway Integration & Demographic Verification", () => {
  test("executes end-to-end simulated OTP flow, establishes demographic match, and elevates document trust signal", async ({
    page,
  }) => {
    await page.goto("/");

    // 1. Locate Citizen Document Center and Click eKYC Verify on a document card
    const walletHeading = page.getByRole("heading", { name: "My Document Wallet & Trust Signals" });
    await walletHeading.scrollIntoViewIfNeeded();

    const ekycBtn = page.locator(".btn-ekyc-trigger").first();
    await expect(ekycBtn).toBeVisible();
    await ekycBtn.click();

    // 2. Assert eKYC Modal & Privacy Assurance Banner
    const ekycModal = page.getByRole("dialog", { name: "Aadhaar eKYC Gateway" });
    await expect(ekycModal).toBeVisible();
    await expect(page.locator(".privacy-assurance-box")).toContainText("Zero Raw Aadhaar Storage Guarantee");

    // 3. Step 1: Select Demo Candidate Profile & Generate Simulated OTP
    await page.getByRole("button", { name: /Sahil Khutey/ }).click();

    // 4. Step 2: Assert OTP Sent Banner & Masked Mobile
    await expect(page.locator(".otp-sent-banner")).toBeVisible();
    await expect(page.locator(".otp-sent-banner")).toContainText("+91 ******9921");

    // 5. Click Auto-fill Demo OTP & Submit Verification
    await page.getByRole("button", { name: "Auto-fill Demo OTP" }).click();
    await page.getByRole("button", { name: "🔐 Verify & Match Identity" }).click();

    // 6. Step 3: Assert Demographic Match & Trust Elevation
    await expect(page.locator(".ekyc-success-banner")).toBeVisible();
    await expect(page.locator(".match-score-badge")).toContainText("100%");
    await expect(page.locator(".elevation-alert-box")).toContainText("Level 4 (Government Verified)");

    // 7. Verify Side-by-Side Demographics Table
    await expect(page.locator(".demographics-diff-table")).toContainText("SAHIL KHUTEY");
    await expect(page.locator(".demographics-diff-table")).toContainText("MATCHED");

    // 8. Close Modal and verify wallet notification banner
    await page.getByRole("button", { name: /Done & Return to Wallet/ }).click();
    await expect(ekycModal).not.toBeVisible();
    await expect(page.locator(".notice")).toContainText("Aadhaar eKYC identity verified");
  });

  test("rejects invalid 6-digit OTP code and maintains security boundary", async ({ page }) => {
    await page.goto("/");

    // 1. Open eKYC Modal from wallet
    const ekycBtn = page.locator(".btn-ekyc-trigger").first();
    await ekycBtn.click();

    // 2. Generate OTP
    await page.getByRole("button", { name: "📲 Generate Simulated OTP" }).click();
    await expect(page.locator(".otp-sent-banner")).toBeVisible();

    // 3. Enter incorrect OTP code
    await page.locator("#ekyc-otp-input").fill("000000");
    await page.getByRole("button", { name: "🔐 Verify & Match Identity" }).click();

    // 4. Assert Error Alert
    await expect(page.locator(".error-alert")).toBeVisible();
    await expect(page.locator(".error-alert")).toContainText("Invalid OTP entered");

    // 5. Close Modal
    await page.getByRole("button", { name: "Close modal" }).click();
  });
});
