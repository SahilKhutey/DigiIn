import { test, expect } from "@playwright/test";

test.describe("Selective Disclosure & Zero-Knowledge Predicates Gateway", () => {
  test("customizes disclosure mode, inspects privacy matrix, authorizes, and validates token", async ({ page }) => {
    await page.goto("/");

    // 1. Scroll to Verification Proof Gateway
    const proofHeading = page.getByRole("heading", { name: "Prove eligibility without uploading documents" });
    await proofHeading.scrollIntoViewIfNeeded();
    await expect(proofHeading).toBeVisible();

    // 2. Click Create Exam Proof Request
    await page.getByRole("button", { name: "Create exam proof request" }).click();

    // 3. Verify Request Consent Card & Selective Disclosure Customizer
    await expect(page.locator(".selective-disclosure-customizer")).toBeVisible();
    await expect(page.locator(".customizer-header")).toContainText("Privacy & Selective Disclosure Controls");

    // 4. Verify 3 Mode Tabs
    await expect(page.getByRole("button", { name: /Zero-Knowledge Predicates/ })).toBeVisible();
    await expect(page.getByRole("button", { name: /Selective Attributes/ })).toBeVisible();
    await expect(page.getByRole("button", { name: /Full Credential Mode/ })).toBeVisible();

    // 5. Check Live Privacy Matrix in Zero-Knowledge Mode (Default)
    await expect(page.locator(".disclosed-column")).toContainText("Age Threshold >= 18");
    await expect(page.locator(".masked-column")).toContainText("Examination Roll Number");


    // 6. Switch to Selective Attribute Mode
    await page.getByRole("button", { name: /Selective Attributes/ }).click();
    await expect(page.locator(".selective-fields-panel")).toBeVisible();

    // 7. Switch back to ZK Predicate Mode
    await page.getByRole("button", { name: /Zero-Knowledge Predicates/ }).click();

    // 8. Authorize Verification
    await page.getByRole("button", { name: "Authorize & Issue Proof" }).click();

    // 9. Verify Verification Receipt & Derived Predicates Block
    await expect(page.locator(".predicate-receipt-block")).toBeVisible();
    await expect(page.locator(".zero-pii-label").first()).toContainText("Zero raw attributes");

    // 10. Introspect Asymmetric Proof Token
    await page.getByRole("button", { name: "Validate proof token" }).click();
    await expect(page.locator(".token-check.valid")).toBeVisible();
    await expect(page.locator(".token-crypto-meta")).toContainText("RFC 7517 Compliant");
  });
});

