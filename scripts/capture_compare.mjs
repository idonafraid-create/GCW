#!/usr/bin/env node

import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { assertSameOriginRedirects, joinSameOrigin, parsePublicHttpUrl, sanitizeText, sanitizeUrl } from "./url_safety.mjs";

const DEFAULT_CLOCK_START = "2026-06-30T00:00:00.000Z";

function parseArgs(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i += 1) {
    if (argv[i] === "--config") args.config = argv[++i];
    else if (argv[i] === "--output") args.output = argv[++i];
    else throw new Error(`Unknown argument: ${argv[i]}`);
  }
  if (!args.config || !args.output) throw new Error("Usage: capture_compare.mjs --config <json> --output <dir>");
  return args;
}

async function loadPlaywright() {
  try {
    return await import("playwright");
  } catch (error) {
    throw new Error(`Playwright is required. Run 'npm install playwright'. Original error: ${error.message}`);
  }
}

function safeId(value) {
  return value.replace(/[^a-zA-Z0-9._-]+/g, "-").replace(/^-|-$/g, "") || "scenario";
}

async function installSeededRandom(context, seed) {
  await context.addInitScript(({ runtimeSeed }) => {
    let state = Number(runtimeSeed) >>> 0;
    Math.random = () => {
      state += 0x6D2B79F5;
      let value = state;
      value = Math.imul(value ^ (value >>> 15), value | 1);
      value ^= value + Math.imul(value ^ (value >>> 7), value | 61);
      return ((value ^ (value >>> 14)) >>> 0) / 4294967296;
    };
  }, { runtimeSeed: seed });
}

async function installNavigationGuard(context, allowedOrigin) {
  await context.route("**/*", async (route) => {
    const request = route.request();
    if (request.resourceType() === "document") {
      const target = new URL(request.url());
      if (target.origin !== allowedOrigin) {
        await route.abort("blockedbyclient");
        return;
      }
    }
    await route.continue();
  });
}

async function initializePage(page, url, scenario) {
  await page.emulateMedia({
    colorScheme: scenario.colorScheme || "light",
    reducedMotion: scenario.reducedMotion || "no-preference",
  });
  if ((scenario.clockMode || "controlled") === "controlled") {
    const clockStart = new Date(scenario.clockStart || DEFAULT_CLOCK_START);
    await page.clock.install({ time: clockStart });
    await page.clock.pauseAt(clockStart);
  }
  const response = await page.goto(url, { waitUntil: "domcontentloaded", timeout: scenario.timeoutMs || 30000 });
  return { status: response?.status() ?? null, finalUrl: page.url(), title: await page.title() };
}

async function isReady(page, scenario) {
  if (scenario.readySelector) {
    return page.locator(scenario.readySelector).first().isVisible().catch(() => false);
  }
  return Boolean(await page.evaluate(scenario.readyFunction));
}

async function advancePair(sourcePage, candidatePage, milliseconds) {
  if (milliseconds <= 0) return;
  await Promise.all([sourcePage.clock.runFor(milliseconds), candidatePage.clock.runFor(milliseconds)]);
}

async function waitPair(sourcePage, candidatePage, milliseconds) {
  if (milliseconds <= 0) return;
  await Promise.all([sourcePage.waitForTimeout(milliseconds), candidatePage.waitForTimeout(milliseconds)]);
}

async function waitForPairedReadiness(sourcePage, candidatePage, scenario) {
  const clockMode = scenario.clockMode || "controlled";
  const timeoutMs = scenario.readyTimeoutMs || 30000;
  if (clockMode === "realtime") {
    const waitOne = async (page) => {
      if (scenario.readySelector) await page.waitForSelector(scenario.readySelector, { state: "visible", timeout: timeoutMs });
      else await page.waitForFunction(scenario.readyFunction, undefined, { timeout: timeoutMs });
      await page.waitForTimeout(scenario.readyDelayMs || 0);
    };
    await Promise.all([waitOne(sourcePage), waitOne(candidatePage)]);
    return { clockMode, advancedMs: null };
  }

  const stepMs = scenario.clockStepMs || 16;
  let advancedMs = 0;
  while (advancedMs <= timeoutMs) {
    const [sourceReady, candidateReady] = await Promise.all([
      isReady(sourcePage, scenario),
      isReady(candidatePage, scenario),
    ]);
    if (sourceReady && candidateReady) break;
    await advancePair(sourcePage, candidatePage, stepMs);
    advancedMs += stepMs;
  }
  const [sourceReady, candidateReady] = await Promise.all([
    isReady(sourcePage, scenario),
    isReady(candidatePage, scenario),
  ]);
  if (!sourceReady || !candidateReady) {
    throw new Error(`Scenario '${scenario.id || scenario.route}' did not reach paired readiness within ${timeoutMs} virtual ms`);
  }
  await advancePair(sourcePage, candidatePage, scenario.readyDelayMs || 0);
  return { clockMode, advancedMs: advancedMs + (scenario.readyDelayMs || 0) };
}

async function applyInput(page, scenario) {
  const scroll = scenario.scroll || { x: 0, y: 0 };
  if (scenario.innerScrollSelector) {
    await page.locator(scenario.innerScrollSelector).evaluate((node, value) => node.scrollTo(value.x || 0, value.y || 0), scroll);
  } else {
    await page.evaluate((value) => window.scrollTo(value.x || 0, value.y || 0), scroll);
  }
  if (scenario.pointer) await page.mouse.move(scenario.pointer.x, scenario.pointer.y);
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const config = JSON.parse(await readFile(path.resolve(args.config), "utf8"));
  const sourceUrl = process.env.GCW_SOURCE_URL || config.sourceUrl;
  const candidateUrl = process.env.GCW_CANDIDATE_URL || config.candidateUrl;
  if (!sourceUrl || !candidateUrl || !Array.isArray(config.scenarios) || !config.scenarios.length) {
    throw new Error("Config requires sourceUrl, candidateUrl and a non-empty scenarios array");
  }
  parsePublicHttpUrl(sourceUrl, "sourceUrl");
  parsePublicHttpUrl(candidateUrl, "candidateUrl");
  const ids = new Set();
  for (const scenario of config.scenarios) {
    if (!scenario.readySelector && !scenario.readyFunction) {
      throw new Error(`Scenario '${scenario.id || scenario.route || "unnamed"}' requires readySelector or readyFunction`);
    }
    const id = safeId(scenario.id || scenario.route || "scenario");
    if (ids.has(id)) throw new Error(`Scenario id collision after filename sanitization: '${id}'`);
    ids.add(id);
    joinSameOrigin(sourceUrl, scenario.route || "/", `Scenario '${id}' route`);
  }

  const { chromium } = await loadPlaywright();
  const executablePath = process.env.GCW_BROWSER_EXECUTABLE || config.browserExecutable || undefined;
  const [sourceBrowser, candidateBrowser] = await Promise.all([
    chromium.launch({ headless: true, executablePath }),
    chromium.launch({ headless: true, executablePath }),
  ]);
  const outputDir = path.resolve(args.output);
  await mkdir(outputDir, { recursive: true });
  const manifest = {
    schemaVersion: 2,
    generatedAt: new Date().toISOString(),
    sourceUrl: sanitizeUrl(sourceUrl),
    candidateUrl: sanitizeUrl(candidateUrl),
    seed: config.seed ?? 1,
    captures: [],
  };

  try {
    for (const scenario of config.scenarios) {
      const id = safeId(scenario.id || scenario.route || "scenario");
      const contextOptions = {
        viewport: scenario.viewport || { width: 1280, height: 720 },
        deviceScaleFactor: scenario.deviceScaleFactor || 1,
        locale: scenario.locale || "en-US",
        timezoneId: scenario.timezoneId || "UTC",
      };
      const [sourceContext, candidateContext] = await Promise.all([
        sourceBrowser.newContext(contextOptions),
        candidateBrowser.newContext(contextOptions),
      ]);
      try {
        await Promise.all([
          installSeededRandom(sourceContext, config.seed ?? 1),
          installSeededRandom(candidateContext, config.seed ?? 1),
          installNavigationGuard(sourceContext, new URL(sourceUrl).origin),
          installNavigationGuard(candidateContext, new URL(candidateUrl).origin),
        ]);
        const route = scenario.route || "/";
        const sourceTarget = joinSameOrigin(sourceUrl, route, `Scenario '${id}' source route`);
        const candidateTarget = joinSameOrigin(candidateUrl, route, `Scenario '${id}' candidate route`);
        await Promise.all([
          assertSameOriginRedirects(sourceTarget, new URL(sourceUrl).origin, `Scenario '${id}' source`, scenario.timeoutMs || 30000),
          assertSameOriginRedirects(candidateTarget, new URL(candidateUrl).origin, `Scenario '${id}' candidate`, scenario.timeoutMs || 30000),
        ]);
        const [sourcePage, candidatePage] = await Promise.all([sourceContext.newPage(), candidateContext.newPage()]);
        const [sourceMeta, candidateMeta] = await Promise.all([
          initializePage(sourcePage, sourceTarget, scenario),
          initializePage(candidatePage, candidateTarget, scenario),
        ]);
        const timing = await waitForPairedReadiness(sourcePage, candidatePage, scenario);
        const phaseMs = scenario.phaseMs ?? 0;
        if (!Number.isFinite(phaseMs) || phaseMs < 0) throw new Error(`Scenario '${id}' phaseMs must be zero or greater`);
        if (timing.clockMode === "controlled") await advancePair(sourcePage, candidatePage, phaseMs);
        else await waitPair(sourcePage, candidatePage, phaseMs);
        await Promise.all([applyInput(sourcePage, scenario), applyInput(candidatePage, scenario)]);
        const afterInputDelayMs = scenario.afterInputDelayMs ?? 100;
        if (!Number.isFinite(afterInputDelayMs) || afterInputDelayMs < 0) throw new Error(`Scenario '${id}' afterInputDelayMs must be zero or greater`);
        if (timing.clockMode === "controlled") {
          await advancePair(sourcePage, candidatePage, afterInputDelayMs);
        } else {
          await waitPair(sourcePage, candidatePage, afterInputDelayMs);
        }

        const sourcePath = path.join(outputDir, `${id}.source.png`);
        const candidatePath = path.join(outputDir, `${id}.candidate.png`);
        const screenshotOptions = { animations: "disabled", fullPage: Boolean(scenario.fullPage) };
        await Promise.all([
          sourcePage.screenshot({ ...screenshotOptions, path: sourcePath }),
          candidatePage.screenshot({ ...screenshotOptions, path: candidatePath }),
        ]);
        manifest.captures.push({
          id,
          route,
          viewport: scenario.viewport || { width: 1280, height: 720 },
          deviceScaleFactor: scenario.deviceScaleFactor || 1,
          timing: { ...timing, phaseMs, afterInputDelayMs },
          scroll: scenario.scroll || { x: 0, y: 0 },
          pointer: scenario.pointer || null,
          source: { ...sourceMeta, finalUrl: sanitizeUrl(sourceMeta.finalUrl), image: path.basename(sourcePath) },
          candidate: { ...candidateMeta, finalUrl: sanitizeUrl(candidateMeta.finalUrl), image: path.basename(candidatePath) },
        });
      } finally {
        await Promise.all([sourceContext.close(), candidateContext.close()]);
      }
    }
  } finally {
    await Promise.all([sourceBrowser.close(), candidateBrowser.close()]);
  }

  const manifestPath = path.join(outputDir, "capture-manifest.json");
  await writeFile(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`, "utf8");
  console.log(JSON.stringify({ output: outputDir, scenarios: manifest.captures.length, manifest: manifestPath }, null, 2));
}

main().catch((error) => {
  console.error(sanitizeText(error.stack || error.message));
  process.exitCode = 1;
});
