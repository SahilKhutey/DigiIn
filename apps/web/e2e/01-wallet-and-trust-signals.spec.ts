import { test, expect } from "@playwright/test";

test.describe("Citizen Document Center & 5 Discrete Trust Signals", () => {
  test("loads wallet credentials and displays 5 discrete trust badges", async ({ page }) => {
    await page.goto("/");

    // 1. Verify Page Header & Brand
    await expect(page.locator(".brand")).toContainText("DigiIn");
    await page.getByRole("button", { name: /🗂️ Vault/i }).click();
    await expect(page.getByRole("heading", { name: "My Document Wallet & Trust Signals" })).toBeVisible();

    // 2. Verify Document Cards are rendered
    const docCards = page.locator(".wallet-card");
    await expect(docCards.first()).toBeVisible();

    // 3. Verify CBSE Secondary School Certificate displays trust signals
    const cbseCard = docCards.filter({ hasText: "Secondary School Certificate (Class XII)" });
    await expect(cbseCard).toBeVisible();

    // Signal 1: Source
    await expect(cbseCard.locator(".trust-cluster")).toContainText("Government Issued");
    // Signal 2: Authenticity
    await expect(cbseCard.locator(".trust-cluster")).toContainText("VERIFIED");
    // Signal 3: Status
    await expect(cbseCard.locator(".trust-cluster")).toContainText("ACTIVE");
    // Signal 4: Version
    await expect(cbseCard.locator(".trust-cluster")).toContainText(/Version \d/);
    // Signal 5: Verification Level
    await expect(cbseCard.locator(".level-header")).toContainText("Level 4: Government Verified");

    // 4. Verify Driving Licence card with EXPIRED status
    const dlCard = docCards.filter({ hasText: "Motor Driving Licence (LMV / MCWG)" });
    await expect(dlCard).toBeVisible();
    await expect(dlCard.locator(".trust-cluster")).toContainText("EXPIRED");

    // 5. Test Filter Buttons
    await page.getByRole("tab", { name: /Expired/ }).click();
    await expect(dlCard).toBeVisible();
    await expect(cbseCard).not.toBeVisible();

    await page.getByRole("tab", { name: /All Records/ }).click();
    await expect(cbseCard).toBeVisible();
  });
});
