import { test, expect } from "@playwright/test";

test.describe("Citizen File Upload & OCR Classifier Pipeline", () => {
  test("uploads preset scan, computes SHA-256, extracts OCR entities, and queues case", async ({ page }) => {
    await page.goto("/");

    // 1. Open the upload dropzone
    await page.getByRole("button", { name: "+ Upload & Classify File" }).click();
    await expect(page.locator(".upload-modal-content")).toBeVisible();

    // 2. Select a quick preset: State Land Title Deed (1998) Scan
    await page.getByRole("button", { name: /State Land Title Deed/ }).click();

    // 3. Click Upload & Run OCR Classifier
    await page.getByRole("button", { name: /Upload & Run OCR Classifier/ }).click();

    // 4. Verify OCR extraction preview card appears
    await expect(page.locator(".ocr-preview-card")).toBeVisible({ timeout: 10000 });
    await expect(page.locator(".ocr-preview-header")).toContainText("OCR & Entity Parser Success");

    // 5. Verify extracted structured fields
    await expect(page.locator(".ocr-preview-card")).toContainText("queue_revenue");

    // 6. Close preview modal
    await page.getByRole("button", { name: "Done • View in Citizen Wallet" }).click();
    await expect(page.locator(".upload-modal-content")).not.toBeVisible();
  });
});
