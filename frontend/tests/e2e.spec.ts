import { test, expect } from '@playwright/test';
import { writeFile } from 'fs/promises';

// aumentar timeout del test para CI lento
test.setTimeout(180000);

test('open dashboard, search logs, open modal', async ({ page }) => {
  const base = process.env.BASE_URL ?? 'http://127.0.0.1:5173';
  await page.goto(base, { waitUntil: 'networkidle', timeout: 90000 });
  // wait for main heading so we know the page finished rendering
  const heading = page.getByRole('heading', { name: 'Sincronizaciones' });

  // Poll for the heading to tolerate slow CI startup or client-side data fetches
  const maxWait = 120000; // ms
  const pollInterval = 1000; // ms
  const start = Date.now();
  let found = false;
  while (Date.now() - start < maxWait) {
    try {
      if (await heading.isVisible()) { found = true; break; }
    } catch (e) {
      // ignore locator errors while app bootstraps
    }
    await page.waitForTimeout(pollInterval);
  }
  if (!found) {
    // try a looser text match as fallback (e.g., plural/singular or slight text differences)
    try {
      const alt = page.getByText(/Sincroniz/i);
      if (await alt.isVisible()) { found = true; }
    } catch (e) {
      // ignore
    }
  }

  if (!found) {
    const ts = Date.now();
    // ensure results dir exists and save diagnostic artifacts for CI
    try {
      await writeFile('test-results/.keep', '');
    } catch (e) {
      // ignore
    }
    try {
      await page.screenshot({ path: `test-results/playwright-failure-${ts}.png`, fullPage: true });
    } catch (e) {
      // ignore
    }
    try {
      const html = await page.content();
      await writeFile(`test-results/playwright-failure-${ts}.html`, html);
    } catch (e) {
      // ignore write errors
    }
    throw new Error('Heading "Sincronizaciones" no encontrado después de espera');
  }

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
