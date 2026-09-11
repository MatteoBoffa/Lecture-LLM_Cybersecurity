/**
 * Smoke-test a built lecture bundle: load it like a student would and fail on
 * anything that would show up as a blank page or a broken image.
 *
 * Usage: node tools/check-site.mjs <baseUrl> [lecture]
 */
import { chromium } from "playwright";

const base = process.argv[2];
if (!base) {
  throw new Error("Usage: node tools/check-site.mjs http://localhost:8000/ [lecture]");
}
const lecture = process.argv[3];

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1400, height: 900 } });

const problems = [];
page.on("console", (m) => m.type() === "error" && problems.push(`console: ${m.text()}`));
page.on("requestfailed", (r) => {
  // Browsers abort media requests routinely (seeking, page teardown); the
  // video is checked below by whether it actually loaded metadata.
  if (r.resourceType() !== "media") {
    problems.push(`request failed: ${r.url()}`);
  }
});
page.on("response", (r) => r.status() >= 400 && problems.push(`HTTP ${r.status()}: ${r.url()}`));

// No ?trace on purpose: the landing redirect is part of what we are testing.
await page.goto(lecture ? `${base}?trace=${lecture}` : base, { waitUntil: "load" });
await page.waitForURL(/trace=/, { timeout: 10000 });
await page.waitForSelector(".trace-viewer-container", { timeout: 20000 });
await page.waitForLoadState("networkidle");

const report = await page.evaluate(() => ({
  url: location.href,
  title: document.title,
  lines: document.querySelectorAll(".line").length,
  images: document.images.length,
  broken: Array.from(document.images)
    .filter((img) => !img.complete || img.naturalWidth === 0)
    .map((img) => img.getAttribute("src")),
  videos: Array.from(document.querySelectorAll("video")).map((v) => ({
    src: v.querySelector("source")?.getAttribute("src"),
    // HAVE_METADATA or better means the server served it in a form the
    // browser can actually play (Range requests included).
    playable: v.readyState >= 1,
  })),
}));

// Stepping is the whole point of the viewer, so check it moves.
const before = new URL(page.url()).searchParams.get("step");
await page.keyboard.press("ArrowRight");
await page.waitForTimeout(300);
const after = new URL(page.url()).searchParams.get("step");
if (before === after) {
  problems.push("Arrow-right did not advance the step");
}
if (report.broken.length) {
  problems.push(`Broken images: ${report.broken.join(", ")}`);
}
if (report.lines === 0) {
  problems.push("Viewer rendered no source lines");
}
for (const video of report.videos) {
  if (!video.playable) {
    problems.push(`Video never loaded: ${video.src}`);
  }
}

await browser.close();
console.log(JSON.stringify(report, null, 2));
if (problems.length) {
  console.error("FAILED:\n" + problems.join("\n"));
  process.exit(1);
}
console.log("OK: bundle loads, steps, and renders every image.");
