const fs = require("fs");
const p = "C:\\Users\\Administrator\\Desktop\\Zhihire-StarMap\\frontend\\src\\views\\common\\HomeView.vue";
let content = fs.readFileSync(p, "utf-8");

// Find where $$$$ appears
let idx = 0;
let count = 0;
while ((idx = content.indexOf("$$$$", idx)) >= 0) {
  count++;
  const ctxStart = Math.max(0, idx - 30);
  const ctxEnd = Math.min(content.length, idx + 30);
  console.log(`Found at pos ${idx}: ...${content.substring(ctxStart, ctxEnd)}...`);
  idx += 1;
}
if (count === 0) console.log("No $$$$ found");
console.log(`Total: ${count} occurrences`);
