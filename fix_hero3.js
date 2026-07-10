const fs = require("fs");
const p = "C:\\Users\\Administrator\\Desktop\\Zhihire-StarMap\\frontend\\src\\views\\common\\HomeView.vue";
let content = fs.readFileSync(p, "utf-8");

// Use regex to find and fix the pattern
// The broken pattern: `url(`{img`)`
// Correct pattern: `url(${img})`
const regex = /`url\(`\{img\}`\)`/;
if (regex.test(content)) {
  content = content.replace(regex, "`url(${img})`");
  fs.writeFileSync(p, content, "utf-8");
  console.log("Fixed with regex");
} else {
  console.log("Regex did not match");
  // Show hex dump of the area
  const idx = content.indexOf("backgroundImage");
  const snippet = content.substring(idx, idx + 50);
  console.log("Hex dump:");
  for (let i = 0; i < snippet.length; i++) {
    console.log(`  ${i}: '${snippet[i]}' (0x${snippet.charCodeAt(i).toString(16)})`);
  }
}
