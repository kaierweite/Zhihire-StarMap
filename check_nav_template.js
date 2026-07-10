const fs = require("fs");
const p = "C:\\Users\\Administrator\\Desktop\\Zhihire-StarMap\\frontend\\src\\views\\common\\HomeView.vue";
let content = fs.readFileSync(p, "utf-8");

// Only fix the template section (after <template>)
const tplIdx = content.indexOf("<template>");
const navIdx = content.indexOf("nav-links", tplIdx);
const divStart = content.lastIndexOf("<div", navIdx);
const divEnd = content.indexOf("</div>", navIdx) + 6;

console.log("=== TEMPLATE NAV SECTION ===");
console.log(content.substring(divStart, divEnd - divStart));

// Also find nav-actions
const actIdx = content.indexOf("nav-actions", tplIdx);
const actStart = content.lastIndexOf("<div", actIdx);
const actEnd = content.indexOf("</div>", content.indexOf("</template>")) + 6;
console.log("\n=== NAV ACTIONS ===");
const actSection = content.substring(actStart, actEnd - actStart);
console.log(actSection);

// Check for $route
console.log("\nHas $route.path: " + content.includes("$route.path"));
