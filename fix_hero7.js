const fs = require("fs");
const p = "C:\\Users\\Administrator\\Desktop\\Zhihire-StarMap\\frontend\\src\\views\\common\\HomeView.vue";

// Read as buffer to avoid any encoding issues
const buffer = fs.readFileSync(p);

// Find the exact position of the broken sequence
// We know: ...backgroundImage: `url(`{img}`) ...
// The `{img}` at positions 139-144 should be ${img}
// Position 139: ` (0x60) should be $ (0x24)
// Position 140: { (0x7b) stays
// Position 141-143: img stays
// Position 144: ` (0x60) should be } (0x7d)

// Search for the pattern: `url(`{img}`)
// String: \x60url(\x60{img}\x60)\x60
const searchStr = "\u0060url(\u0060{img}\u0060)\u0060";
const replacement = "\u0060url(${img})\u0060";

const content = buffer.toString("utf-8");
const idx = content.indexOf(searchStr);

if (idx >= 0) {
  console.log("Found at byte position: " + idx);
  console.log("Before bytes: " + buffer.slice(idx, idx + 13).toString("hex"));
  
  // Replace in buffer
  const before = buffer.slice(0, idx);
  const replaceBytes = Buffer.from(replacement, "utf-8");
  const after = buffer.slice(idx + 13);
  
  const newBuffer = Buffer.concat([before, replaceBytes, after]);
  fs.writeFileSync(p, newBuffer);
  
  console.log("After bytes: " + Buffer.from(replacement, "utf-8").toString("hex"));
  console.log("Fixed!");
} else {
  console.log("Pattern not found in string form. Trying direct byte manipulation.");
  
  // Direct byte manipulation - find the pattern `url(`{img}`)
  const pattern = [0x60, 0x75, 0x72, 0x6c, 0x28, 0x60, 0x7b, 0x69, 0x6d, 0x67, 0x60, 0x29, 0x60];
  const correct = [0x60, 0x75, 0x72, 0x6c, 0x28, 0x24, 0x7b, 0x69, 0x6d, 0x67, 0x7d, 0x29, 0x60];
  
  let found = -1;
  for (let i = 0; i <= buffer.length - pattern.length; i++) {
    let match = true;
    for (let j = 0; j < pattern.length; j++) {
      if (buffer[i + j] !== pattern[j]) { match = false; break; }
    }
    if (match) { found = i; break; }
  }
  
  if (found >= 0) {
    console.log("Found at byte position: " + found);
    for (let j = 0; j < pattern.length; j++) {
      buffer[found + j] = correct[j];
    }
    fs.writeFileSync(p, buffer);
    console.log("Fixed via byte manipulation!");
  } else {
    console.log("Pattern not found via byte search either.");
  }
}
