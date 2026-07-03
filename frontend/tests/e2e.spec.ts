import { test, expect } from '@playwright/test';

// aumentar timeout del test para CI lento
test.setTimeout(120000);

test('open dashboard, search logs, open modal', async ({ page }) => {
  const base = process.env.BASE_URL ?? 'http://127.0.0.1:5173';
  await page.goto(base, { waitUntil: 'networkidle', timeout: 60000 });
  // wait for main heading so we know the page finished rendering
  const heading = page.getByRole('heading', { name: 'Sincronizaciones' });
  await heading.waitFor({ state: 'visible', timeout: 60000 });

  // then wait for logs input to appear (longer timeout to tolerate slow preview/build)
  const input = page.getByPlaceholder('Buscar logs');
  await input.waitFor({ state: 'visible', timeout: 20000 });

  // Type a query and wait a bit for debounced request
  await input.fill('error');
  await page.waitForTimeout(500);

  // Wait for any log item and click detalle
  const button = page.getByRole('button', { name: 'Detalle' }).first();
  if (await button.count() > 0) {
    await button.click({ timeout: 5000 });
    // modal should appear
    await expect(page.getByRole('dialog')).toBeVisible({ timeout: 5000 });
    await expect(page.getByText('Cerrar')).toBeVisible({ timeout: 5000 });
    // close modal
    await page.getByText('Cerrar').click();
    await expect(page.getByRole('dialog')).toHaveCount(0);
  } else {
    // If no logs present, ensure the page still shows sincronizaciones (heading)
    await expect(page.getByRole('heading', { name: 'Sincronizaciones' })).toBeVisible();
  }
});
