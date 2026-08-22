import { test, expect } from "@playwright/test";

test.describe("Citizen Consent Management & Cryptographic Revocation Dashboard", () => {
  test("inspects active consents, revokes proof authorization, and audits timeline", async ({ page }) => {
    // 1. First create and authorize a proof on the citizen gateway
    await page.goto("/");
    const proofHeading = page.getByRole("heading", { name: "Prove eligibility without uploading documents" });
    await proofHeading.scrollIntoViewIfNeeded();
    await page.getByRole("button", { name: "Create exam proof request" }).click();
    await page.getByRole("button", { name: "Authorize & Issue Proof" }).click();

    // 2. Switch to Consent & Audit Dashboard perspective
    await page.getByRole("button", { name: "🛡️ Consent & Audit" }).click();
    await expect(page.getByRole("heading", { name: "Citizen Consent & Cryptographic Audit Dashboard" })).toBeVisible();

    // 3. Verify Metrics Row is visible
    await expect(page.locator(".metric-card.active-card")).toBeVisible();
    await expect(page.locator(".metric-card.audit-card")).toBeVisible();

    // 4. Inspect Active Authorizations Table
    await expect(page.locator(".consent-table")).toBeVisible();
    const activeRow = page.locator(".consent-row.active").first();
    await expect(activeRow).toBeVisible();
    await expect(activeRow).toContainText("Demo Examination Portal");

    // 5. Click Revoke Button on the active consent grant
    await activeRow.getByRole("button", { name: "Revoke" }).click();

    // 6. Verify Revocation Modal appears
    await expect(page.locator(".revocation-modal")).toBeVisible();
    await expect(page.locator(".revocation-warning")).toContainText("Once revoked, any offline or online introspection check");

    // 7. Fill revocation reason and confirm
    await page.locator(".revocation-reason-input").fill("Citizen withdrew university application.");
    await page.getByRole("button", { name: "Confirm Revocation" }).click();

    // 8. Verify grant status transitions to REVOKED
    await expect(page.locator(".revocation-modal")).not.toBeVisible();
    await expect(page.locator(".consent-row.revoked").first()).toBeVisible();

    // 9. Test Sovereign Audit Trail Timeline is rendered
    await expect(page.locator(".audit-timeline")).toBeVisible();
    await expect(page.locator(".audit-event-item").first()).toBeVisible();
  });
});
