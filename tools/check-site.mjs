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

const report = await page.evaluate(() => {
  const images = Array.from(document.images);
  const videos = Array.from(document.querySelectorAll("video"));
  const sourceOf = (v) => v.querySelector("source")?.getAttribute("src") ?? v.getAttribute("src");
  return {
    url: location.href,
    title: document.title,
    lines: document.querySelectorAll(".line").length,
    images: images.length,
    // An element with no source at all asked the server for nothing, so it says
    // nothing about the bundle: it is prose that emitted a stray tag. Reported,
    // but not a failure - this tool checks what was shipped, not what was written.
    broken: images.filter((img) => img.getAttribute("src") && img.naturalWidth === 0)
      .map((img) => img.getAttribute("src")),
    empty: images.filter((img) => !img.getAttribute("src")).length
      + videos.filter((v) => !sourceOf(v)).length,
    videos: videos.filter(sourceOf).map((v) => ({
      src: sourceOf(v),
      // HAVE_METADATA or better means the server served it in a form the
      // browser can actually play (Range requests included).
      playable: v.readyState >= 1,
    })),
  };
});

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
if (report.empty) {
  console.log(`Note: ${report.empty} media element(s) with no source - a stray tag in the lecture's prose, not a bundle problem.`);
}
if (problems.length) {
  console.error("FAILED:\n" + problems.join("\n"));
  process.exit(1);
}
console.log("OK: bundle loads, steps, and renders every image.");
