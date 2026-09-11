import fs from "node:fs";
import { chromium } from "playwright";

const lecture = process.argv[2];
if (!lecture) {
  throw new Error("Usage: node tools/export-pdf.mjs lecture_01 [baseUrl|port]");
}
// A bare port keeps the old dev-server usage working; a full URL lets the
// handout be rendered from the built static site instead.
const target = process.argv[3] ?? "5173";
const base = /^\d+$/.test(target) ? `http://localhost:${target}/` : target;

fs.mkdirSync("pdf", { recursive: true });

const browser = await chromium.launch();
const page = await browser.newPage({
  viewport: { width: 1440, height: 1000 },
});

const url = new URL(base);
url.searchParams.set("trace", lecture);
url.searchParams.set("hideEnv", "1"); // the variable panel is a floating overlay
url.searchParams.set("showNotes", "1"); // otherwise note() content is dropped
url.searchParams.set("animate", "0"); // a handout shows everything, not just what a step reached

await page.goto(url.toString(), { waitUntil: "load" });

// The container only appears once the trace has been fetched and parsed.
try {
  await page.waitForSelector(".trace-viewer-container", { timeout: 15000 });
} catch {
  const message = await page.textContent("body");
  throw new Error(`Viewer did not load trace "${lecture}": ${message?.trim()}`);
}

// Images and plots resolve after React renders; wait for them or the PDF has gaps.
await page.evaluate(() =>
  Promise.all(
    Array.from(document.images)
      .filter((img) => !img.complete)
      .map(
        (img) =>
          new Promise((resolve) => {
            img.onload = img.onerror = resolve;
          }),
      ),
  ),
);
await page.waitForTimeout(1000);

// Make the final PDF look like a handout rather than a live presentation.
await page.addStyleTag({
  content: `
    .icon-buttons { display: none !important; }
    .current-line { background: transparent !important; }
    .line { break-inside: avoid; }

    /* The viewer is laid out for a wide screen: the lines panel reserves
       1000px and scrolls sideways, which on an A4 page simply clips. Let the
       content reflow to whatever width the paper actually offers. */
    .trace-viewer-container { display: block !important; }
    .lines-panel { min-width: 0 !important; overflow-x: visible !important; }
    .renderings { width: auto !important; max-width: 100% !important; }
    .markdown table { width: 100% !important; table-layout: fixed; }
    .markdown td, .markdown th { overflow-wrap: anywhere; }
    img, video { max-width: 100% !important; height: auto !important; }
  `,
});

await page.emulateMedia({ media: "screen" });
await page.pdf({
  path: `pdf/${lecture}.pdf`,
  format: "A4",
  printBackground: true,
  margin: {
    top: "15mm",
    bottom: "15mm",
    left: "15mm",
    right: "30mm",
  },
});

await browser.close();
console.log(`Created pdf/${lecture}.pdf`);