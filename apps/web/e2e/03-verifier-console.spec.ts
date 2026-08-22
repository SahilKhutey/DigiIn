import { test, expect } from "@playwright/test";

test.describe("Government Verifier Console & Evidence Diff Comparison", () => {
  test("navigates queues, opens evidence diff comparison, and records officer decision", async ({ page }) => {
    await page.goto("/");

    // 1. Switch to Government Verifier Console perspective
    await page.getByRole("button", { name: /Verifier Console/ }).click();
    await expect(page.getByRole("heading", { name: "Government Verifier Console" })).toBeVisible();

    // 2. Select All Departments tab or CBSE Queue tab
    await page.getByRole("tab", { name: /All Departments/ }).click();

    // 3. Find and click a case in the queue
    const caseItem = page.locator(".case-item").first();
    await expect(caseItem).toBeVisible();
    await caseItem.click();

    // 4. Verify Side-by-Side Evidence Diff Inspector is visible
    await expect(page.locator(".evidence-inspector")).toBeVisible();
    await expect(page.locator(".comparison-table")).toBeVisible();

    // 5. If case is pending, execute decision
    const verifyBtn = page.getByRole("button", { name: /Approve & Verify/ });
    if (await verifyBtn.isVisible()) {
      await verifyBtn.click();
      await expect(page.getByText(/decided: VERIFY/)).toBeVisible();
    } else {
      await expect(page.locator(".decision-notice-box")).toBeVisible();
    }
  });
});
