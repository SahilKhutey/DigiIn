import { test, expect } from "@playwright/test";

test.describe("Printable Support-Safe Diagnostic Sheet", () => {
  test("generates support-safe reference and renders printable summary sheet modal", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("button", { name: /⚗️ Lab/i }).click();

    // 1. Scroll to Diagnostic Timeline & Recovery section
    const recoverySection = page.locator("#recovery");
    await recoverySection.scrollIntoViewIfNeeded();
    await expect(recoverySection).toBeVisible();

    // 2. Click "Print Official Support Report" button
    const openSheetBtn = page.getByRole("button", { name: /Print Official Support Report/ });
    await expect(openSheetBtn).toBeVisible();
    await openSheetBtn.click();

    // 3. Verify Printable Support Sheet Modal appears
    await expect(page.locator(".support-sheet-modal")).toBeVisible();
    await expect(page.locator(".sheet-brand h2")).toContainText("DigiIn");

    // 4. Verify Confidential Support Code Banner & Zero PII Safe Badge
    await expect(page.locator(".sheet-code-banner")).toBeVisible();
    await expect(page.locator(".safe-badge")).toContainText("ZERO PII");

    // 5. Verify Diagnostic Details and Stage Information
    await expect(page.locator(".sheet-info-box").first()).toBeVisible();
    await expect(page.locator(".sheet-info-box").first()).toContainText("Failure Stage");

    // 6. Verify Physical Operator Verification Checklist
    await expect(page.locator(".sheet-guidance-box.operator-box")).toBeVisible();
    await expect(page.locator(".sheet-guidance-box.operator-box")).toContainText("Verification Desk Operator Checklist");

    // 7. Close Modal
    await page.getByRole("button", { name: "Close modal" }).click();
    await expect(page.locator(".support-sheet-modal")).not.toBeVisible();
  });
});
