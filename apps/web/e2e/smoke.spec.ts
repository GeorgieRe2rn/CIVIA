import { test, expect } from "@playwright/test";

test.describe("CIVIA web", () => {
  test("loads real catalog data and navigates to historical data", async ({ page }) => {
    await page.goto("/");

    await expect(page.getByText("API conectada", { exact: true })).toBeVisible();
    await expect(page.getByLabel("Territorio")).toBeVisible();
    await expect(page.getByLabel("Elección de referencia")).toBeVisible();
    await expect(page.getByRole("heading", { name: "Comprende la participación ciudadana", exact: true }).first()).toBeVisible();

    await page.locator("nav.main-nav").getByRole("button", { name: /Datos$/ }).click();
    await expect(page.getByRole("heading", { name: "Explora los datos históricos", exact: true }).first()).toBeVisible();
    await expect(page.getByRole("table", { name: "Histórico de participación observada" })).toBeVisible();
    await expect(page.getByText("Fuente", { exact: true }).last()).toBeVisible();
  });

  test("calculates a scenario through the API", async ({ page }) => {
    await page.goto("/");
    await page.getByLabel("Elección de referencia").selectOption("federal-2024");
    await page.locator("nav.main-nav").getByRole("button", { name: /Escenarios$/ }).click();

    await expect(page.getByRole("heading", { name: "¿Qué cambia bajo tus supuestos?", exact: true }).first()).toBeVisible();
    await page.getByRole("button", { name: "Calcular escenario", exact: true }).click();
    await expect(page.getByText("Respuesta de API", { exact: true })).toBeVisible();
    await expect(page.getByText("Simulación hipotética", { exact: true })).toBeVisible();
  });

  test("keeps the map honest when geometry is unavailable", async ({ page }) => {
    await page.goto("/");
    await page.locator("nav.main-nav").getByRole("button", { name: /Mapa$/ }).click();

    await expect(page.getByRole("heading", { name: "La geometría todavía no está disponible.", exact: true })).toBeVisible();
    await expect(page.getByText("No se dibuja un mapa falso", { exact: true })).toBeVisible();
  });
});
