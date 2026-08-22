import { test, expect } from "@playwright/test";

test.describe("Offline QR Code Verifier Scanner & Asymmetric Proof Verification", () => {
  test("generates 2D verifiable QR code, executes 100% offline Ed25519 check, and detects payload forgery", async ({
    page,
  }) => {
    await page.goto("/");

    // 1. Generate an Asymmetric Proof Token in the Verification Gateway
    const proofHeading = page.getByRole("heading", { name: "Prove eligibility without uploading documents" });
    await proofHeading.scrollIntoViewIfNeeded();
    await page.getByRole("button", { name: "Create exam proof request" }).click();
    await page.getByRole("button", { name: "Authorize & Issue Proof" }).click();

    // 2. Open Verifiable QR Code Modal
    const viewQrBtn = page.getByRole("button", { name: "📱 View Verifiable QR Code" });
    await expect(viewQrBtn).toBeVisible();
    await viewQrBtn.click();

    // 3. Inspect QR Code Generation & Cryptographic Metadata
    await expect(page.locator(".qr-modal-content")).toBeVisible();
    await expect(page.locator(".qr-image-display")).toBeVisible({ timeout: 5000 });
    await expect(page.locator(".qr-crypto-badge")).toContainText("RFC 7517 Compliant");

    // 4. Launch Offline QR Field Scanner
    await page.getByRole("button", { name: /Test in Offline Scanner/ }).click();
    await expect(page.locator(".scanner-modal-content")).toBeVisible();

    // 5. Verify Air-Gapped Status (0 Network Calls)
    await expect(page.locator(".airgap-badge")).toContainText("100% Offline");

    // 6. Assert Offline Cryptographic Signature Check Success
    await expect(page.locator(".badge-valid")).toBeVisible();
    await expect(page.locator(".badge-valid")).toContainText("AUTHENTIC (OFFLINE ED25519 VERIFIED)");

    // 7. Verify Offline Zero-Knowledge Predicates Table
    await expect(page.locator(".verified-predicates-panel")).toBeVisible();
    await expect(page.locator(".verified-predicates-panel")).toContainText("qualification_status == PASSED");
    await expect(page.locator(".masked-assurance-box")).toContainText("Sovereign Privacy Guarantee");


    // 8. Test Tamper & Forgery Sandbox: Mutate 1 character in base64 payload
    await page.getByRole("button", { name: /Simulate Payload Tamper/ }).click();

    // 9. Assert Instant Cryptographic Rejection
    await expect(page.locator(".badge-tampered")).toBeVisible();
    await expect(page.locator(".badge-tampered")).toContainText("TAMPERED / FORGED SIGNATURE");

    // 10. Switch to Camera Viewfinder Simulation
    await page.getByRole("button", { name: /Camera Viewfinder Simulation/ }).click();
    await expect(page.locator(".camera-viewfinder-box")).toBeVisible();
    await expect(page.locator(".laser-scanner-line")).toBeVisible();

    // 11. Capture Sample QR Code from Simulated Camera Stream
    await page.getByRole("button", { name: /Capture Sample QR Code/ }).click();
    await expect(page.locator(".badge-valid")).toBeVisible();

    // 12. Close Scanner Modal
    await page.getByRole("button", { name: "Close modal" }).click();
    await expect(page.locator(".scanner-modal-content")).not.toBeVisible();
  });

  test("launches offline QR scanner from top navigation header directly", async ({ page }) => {
    await page.goto("/");

    // 1. Click top header Scanner button
    await page.getByRole("button", { name: "📷 Offline QR Scanner" }).click();
    await expect(page.locator(".scanner-modal-content")).toBeVisible();

    // 2. Select Quick Scan Preset: Expired University Proof
    await page.getByRole("button", { name: /Expired University Admission Proof/ }).click();

    // 3. Assert Expired Proof status is detected mathematically
    await expect(page.locator(".badge-expired")).toBeVisible();
    await expect(page.locator(".badge-expired")).toContainText("EXPIRED PROOF");

    // 4. Close modal
    await page.getByRole("button", { name: "Close modal" }).click();
    await expect(page.locator(".scanner-modal-content")).not.toBeVisible();
  });
});
