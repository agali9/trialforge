import { test, expect } from "@playwright/test";

test("compare page placeholder", async ({ page }) => {
  await page.goto("/compare");
  await expect(page.locator("text=Compare Runs")).toBeVisible();
});
