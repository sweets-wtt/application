import { expect, test } from "@playwright/test";

test("首页可访问", async ({ page }) => {
  // 打开根路径
  await page.goto("/");
  // 校验页面标题
  await expect(page).toHaveTitle(/应用/u);
});
