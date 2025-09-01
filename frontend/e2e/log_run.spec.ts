import { test, expect } from "@playwright/test";

test("run logging flow placeholder", async ({ page }) => {
  await page.goto("/login");
  await expect(page.locator("text=Login")).toBeVisible();
});
