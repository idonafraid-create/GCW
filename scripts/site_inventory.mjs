#!/usr/bin/env node

import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import process from "node:process";

const SENSITIVE_QUERY_KEYS = /^(key|api[-_]?key|token|access[-_]?token|auth|authorization|signature|secret|password)$/i;

function sanitizeUrl(value) {
  try {
    const url = new URL(value);
    for (const key of [...url.searchParams.keys()]) {
      if (SENSITIVE_QUERY_KEYS.test(key)) url.searchParams.set(key, "REDACTED");
    }
    return url.href;
  } catch {
    return value;
  }
}

function sanitizeSurface(surface) {
  for (const field of ["iframes", "images", "scripts", "stylesheets", "anchors"]) {
    surface[field] = surface[field].map(sanitizeUrl);
  }
  surface.videos = surface.videos.map((video) => ({ ...video, src: sanitizeUrl(video.src) }));
  surface.performanceResources = surface.performanceResources.map((resource) => ({ ...resource, url: sanitizeUrl(resource.url) }));
  return surface;
}

function parseArgs(argv) {
  const args = { maxRoutes: 25, timeout: 20000, settleMs: 700, executablePath: "" };
  for (let i = 0; i < argv.length; i += 1) {
    const key = argv[i];
    const value = argv[i + 1];
    if (key === "--url") args.url = value, i += 1;
    else if (key === "--out") args.out = value, i += 1;
    else if (key === "--max-routes") args.maxRoutes = Number(value), i += 1;
    else if (key === "--timeout") args.timeout = Number(value), i += 1;
    else if (key === "--settle-ms") args.settleMs = Number(value), i += 1;
    else if (key === "--executable-path") args.executablePath = value, i += 1;
    else throw new Error(`Unknown argument: ${key}`);
  }
  if (!args.url || !args.out) {
    throw new Error("Usage: site_inventory.mjs --url <url> --out <file> [--max-routes 25]");
  }
  return args;
}

async function loadPlaywright() {
  try {
    return await import("playwright");
  } catch (error) {
    throw new Error(`Playwright is required. Run 'npm install playwright'. Original error: ${error.message}`);
  }
}

function normalizeRoute(href, origin) {
  try {
    const url = new URL(href, origin);
    if (url.origin !== origin || !["http:", "https:"].includes(url.protocol)) return null;
    url.hash = "";
    for (const key of [...url.searchParams.keys()]) {
      if (SENSITIVE_QUERY_KEYS.test(key)) url.searchParams.delete(key);
    }
    return `${url.pathname}${url.search}` || "/";
  } catch {
    return null;
  }
}

async function inspectPage(page) {
  return page.evaluate(() => {
    const canvases = [...document.querySelectorAll("canvas")].map((canvas, index) => {
      let context = "unknown";
      let attributes = null;
      for (const type of ["webgl2", "webgl", "experimental-webgl", "2d", "bitmaprenderer"]) {
        try {
          const candidate = canvas.getContext(type);
          if (candidate) {
            context = type;
            attributes = typeof candidate.getContextAttributes === "function" ? candidate.getContextAttributes() : null;
            break;
          }
        } catch {
          // The canvas may already be bound to a different context type.
        }
      }
      const rect = canvas.getBoundingClientRect();
      return {
        index,
        context,
        attributes,
        width: canvas.width,
        height: canvas.height,
        clientRect: { x: rect.x, y: rect.y, width: rect.width, height: rect.height },
        className: String(canvas.className || ""),
      };
    });

    const resources = performance.getEntriesByType("resource").map((entry) => ({
      url: entry.name,
      initiatorType: entry.initiatorType,
      duration: Number(entry.duration.toFixed(3)),
      transferSize: entry.transferSize || 0,
      decodedBodySize: entry.decodedBodySize || 0,
    }));

    return {
      title: document.title,
      readyState: document.readyState,
      scrollSize: { width: document.documentElement.scrollWidth, height: document.documentElement.scrollHeight },
      canvases,
      iframes: [...document.querySelectorAll("iframe")].map((node) => node.src),
      videos: [...document.querySelectorAll("video")].map((node) => ({ src: node.currentSrc || node.src, autoplay: node.autoplay, loop: node.loop })),
      images: [...document.images].map((node) => node.currentSrc || node.src).filter(Boolean),
      scripts: [...document.scripts].map((node) => node.src).filter(Boolean),
      stylesheets: [...document.querySelectorAll('link[rel="stylesheet"]')].map((node) => node.href),
      fonts: document.fonts ? [...document.fonts].map((font) => ({ family: font.family, style: font.style, weight: font.weight, status: font.status })) : [],
      anchors: [...document.querySelectorAll("a[href]")].map((node) => node.href),
      performanceResources: resources,
    };
  });
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const canonical = new URL(args.url);
  const { chromium } = await loadPlaywright();
  const executablePath = args.executablePath || process.env.GCW_BROWSER_EXECUTABLE || undefined;
  const browser = await chromium.launch({ headless: true, executablePath });
  const context = await browser.newContext({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
  const page = await context.newPage();
  page.setDefaultTimeout(args.timeout);

  const resources = new Map();
  context.on("request", (request) => {
    const url = request.url();
    if (!resources.has(url)) {
      resources.set(url, { url: sanitizeUrl(url), method: request.method(), resourceType: request.resourceType(), status: null, mimeType: null });
    }
  });
  context.on("response", async (response) => {
    const request = response.request();
    const current = resources.get(response.url()) || { url: sanitizeUrl(response.url()), method: request.method(), resourceType: request.resourceType() };
    current.status = response.status();
    current.mimeType = (await response.headerValue("content-type")) || null;
    resources.set(response.url(), current);
  });

  const queue = [normalizeRoute(canonical.href, canonical.origin) || "/"];
  const queued = new Set(queue);
  const visited = new Set();
  const routes = [];

  while (queue.length && routes.length < args.maxRoutes) {
    const route = queue.shift();
    if (visited.has(route)) continue;
    visited.add(route);
    const url = new URL(route, canonical.origin).href;
    const record = { route, url, status: null, error: null, surface: null };
    try {
      const response = await page.goto(url, { waitUntil: "domcontentloaded", timeout: args.timeout });
      record.status = response?.status() ?? null;
      await page.waitForTimeout(args.settleMs);
      record.surface = sanitizeSurface(await inspectPage(page));
      for (const href of record.surface.anchors) {
        const candidate = normalizeRoute(href, canonical.origin);
        if (candidate && !queued.has(candidate) && !visited.has(candidate)) {
          queued.add(candidate);
          queue.push(candidate);
        }
      }
    } catch (error) {
      record.error = error.message;
    }
    routes.push(record);
  }

  await browser.close();
  const output = {
    schemaVersion: 1,
    generatedAt: new Date().toISOString(),
    canonicalUrl: canonical.href,
    origin: canonical.origin,
    limits: { maxRoutes: args.maxRoutes, timeout: args.timeout, settleMs: args.settleMs },
    routes,
    resources: [...resources.values()].sort((a, b) => a.url.localeCompare(b.url)),
  };
  await mkdir(path.dirname(path.resolve(args.out)), { recursive: true });
  await writeFile(path.resolve(args.out), `${JSON.stringify(output, null, 2)}\n`, "utf8");
  console.log(JSON.stringify({ out: path.resolve(args.out), routes: routes.length, resources: output.resources.length }, null, 2));
}

main().catch((error) => {
  console.error(error.stack || error.message);
  process.exitCode = 1;
});
