const fs = require("fs");
const p = "C:\\Users\\Administrator\\Desktop\\Zhihire-StarMap\\frontend\\src\\views\\common\\HomeView.vue";
let content = fs.readFileSync(p, "utf-8");

// Find the exact position of the broken template literal
const idx = content.indexOf("backgroundImage:");
const start = content.indexOf("\u0060url(", idx);  // url(

// Extract what's there
const broken = content.substring(start, start + 13);
console.log("Bytes around area:");
for (let i = 0; i < 15; i++) {
  console.log("  " + i + ": " + content.charCodeAt(start + i) + " = '" + content.charAt(start + i) + "'");
}

// Build the correct replacement
const correct = "\u0060url()\u0060";
const brokenTarget = "\u0060url(\u0060{img}\u0060)\u0060";

console.log("\\nBroken: " + JSON.stringify(brokenTarget));
console.log("Correct: " + JSON.stringify(correct));

content = content.replace(brokenTarget, correct);
fs.writeFileSync(p, content, "utf-8");

// Verify
content = fs.readFileSync(p, "utf-8");
const contains = content.includes(correct);
console.log("\\nFix applied: " + contains);
const line242 = content.split("\\n")[242];
console.log("Line 243: " + line242.substring(0, 120) + "...");
