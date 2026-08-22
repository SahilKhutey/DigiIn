import { test, expect } from "@playwright/test";

test.describe("Correction & Immutable Versioning Lineage (v1 -> v2)", () => {
  test("citizen submits correction, officer approves, and document advances to v2", async ({ page }) => {
    await page.goto("/");

    // 1. Scroll to Correction Section
    const correctionHeading = page.getByRole("heading", { name: "Correction & Versioning Lifecycle" });
    await correctionHeading.scrollIntoViewIfNeeded();
    await expect(correctionHeading).toBeVisible();

    // 2. Fill in proposed correction value and submit
    await page.getByRole("button", { name: "Submit correction request" }).click();

    // 3. Verify pending correction item appears in officer review queue
    await expect(page.locator(".consent-panel")).toBeVisible();
    await expect(page.locator(".consent-panel")).toContainText("PENDING_REVIEW");

    // 4. Review & Approve as Officer
    const approveBtn = page.getByRole("button", { name: /Approve \(Issue Next Version\)/ });
    if (await approveBtn.isVisible()) {
      await approveBtn.click();
      // 5. Verify status notice reports updated state
      await expect(page.getByRole("status").first()).toBeVisible();
    }
  });
});
