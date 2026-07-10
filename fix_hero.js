const fs = require("fs");
const p = "C:\\Users\\Administrator\\Desktop\\Zhihire-StarMap\\frontend\\src\\views\\common\\HomeView.vue";
let content = fs.readFileSync(p, "utf-8");

// Fix: `url(`{img`)`  should be  `url(${img})`
content = content.replace('`url(`{img}`)', "`url(${img})`");

fs.writeFileSync(p, content, "utf-8");
console.log("Fixed hero template literal");

// Verify
content = fs.readFileSync(p, "utf-8");
const line = content.split("\n")[242]; // 0-indexed, so line 243 is index 242
console.log("Line 243:", line.trim());
