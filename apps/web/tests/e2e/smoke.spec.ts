import { expect, test } from "@playwright/test";

// Playwright 夹具为库定义的可变类型，无法只读化
// eslint-disable-next-line typescript/prefer-readonly-parameter-types
test("首页可访问", async ({ page }) => {
  // 打开根路径
  await page.goto("/");
  // 校验页面标题
  await expect(page).toHaveTitle(/应用/u);
});
