/** 冒烟测试 */
import { expect, test } from "@playwright/test";

test("首页加载", async ({ page }) => {
  await page.goto("/");

  await expect(page).toHaveTitle(/Application/);
});
