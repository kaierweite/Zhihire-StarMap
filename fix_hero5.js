const fs = require("fs");
const p = "C:\\Users\\Administrator\\Desktop\\Zhihire-StarMap\\frontend\\src\\views\\common\\HomeView.vue";
let content = fs.readFileSync(p, "utf-8");

// The broken text: `url(`{img`)`
// Need to fix to: `url(${img})`
// Use char codes to avoid any encoding issues

const correct = "\u0060url(\u0024{img})\u0060";
const broken = "\u0060url(\u0060{img}\u0060)\u0060";

console.log("Broken: " + JSON.stringify(broken));
console.log("Correct: " + JSON.stringify(correct));

const beforeLen = content.length;
content = content.split(broken).join(correct);
const afterLen = content.length;

console.log("Replaced: " + (beforeLen !== afterLen));
console.log("Chars changed: " + (beforeLen - afterLen));

fs.writeFileSync(p, content, "utf-8");

// Verify the line
const lines = content.split("\n");
console.log("Line 243: " + lines[242].substring(0, 130));
