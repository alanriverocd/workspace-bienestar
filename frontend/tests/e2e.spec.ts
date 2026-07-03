import { test, expect } from '@playwright/test';

test('open dashboard, search logs, open modal', async ({ page }) => {
  await page.goto('/');
  // wait for logs input to appear (increase timeout to tolerate slow preview/build)
  const input = page.getByPlaceholder('Buscar logs');
  await input.waitFor({ state: 'visible', timeout: 10000 });

  // Type a query and wait a bit for debounced request
  await input.fill('error');
  await page.waitForTimeout(500);

  // Wait for any log item and click detalle
  const button = page.locator('button', { hasText: 'Detalle' }).first();
  if (await button.count() > 0) {
    await button.click();
    // modal should appear
    await expect(page.getByRole('dialog')).toBeVisible();
    await expect(page.getByText('Cerrar')).toBeVisible();
    // close modal
    await page.getByText('Cerrar').click();
    await expect(page.getByRole('dialog')).toHaveCount(0);
  } else {
    // If no logs present, ensure the page still shows sincronizaciones (heading)
    await expect(page.getByRole('heading', { name: 'Sincronizaciones' })).toBeVisible();
  }
});
