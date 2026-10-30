import path from "node:path";
import { fileURLToPath } from "node:url";
import { defineConfig, devices } from "@playwright/test";

const webDirectory = path.dirname(fileURLToPath(import.meta.url));
const repositoryRoot = path.resolve(webDirectory, "../..");
const pythonCommand = process.env.CIVIA_PYTHON ? `"${process.env.CIVIA_PYTHON}"` : "python";

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 2 : 0,
  reporter: process.env.CI ? "line" : "list",
  use: {
    baseURL: "http://localhost:5173",
    trace: "on-first-retry",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: [
    {
      command: `${pythonCommand} -m uvicorn app.main:app --app-dir services/api --host 127.0.0.1 --port 8000`,
      cwd: repositoryRoot,
      url: "http://127.0.0.1:8000/api/health",
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
    },
    {
      command: "npm run dev -- --host 127.0.0.1 --port 5173",
      cwd: webDirectory,
      url: "http://127.0.0.1:5173",
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
    },
  ],
});
