import { test, expect } from "@playwright/test";

test("login redirect", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveURL(/login/);
});
