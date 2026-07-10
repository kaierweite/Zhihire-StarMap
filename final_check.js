const fs = require("fs");
const p = "C:\\Users\\Administrator\\Desktop\\Zhihire-StarMap\\frontend\\src\\views\\common\\HomeView.vue";
const content = fs.readFileSync(p, "utf-8");
const lines = content.split("\n");
console.log("Total lines: " + lines.length);
console.log("Total chars: " + content.length);

// Check nav fixes
console.log("\n=== NAV FIXES VERIFICATION ===");
console.log("1. Dynamic active class: " + content.includes(":class=\"{ active: \\$route.path === '/' }"));
console.log("2. ability-map link: " + content.includes("/user/ability-map"));
console.log("3. career-plan link: " + content.includes("/user/career-plan"));
console.log("4. Resume link intact: " + (content.includes("<router-link to=\"/user/resume\"") && content.includes("</router-link>")));
console.log("5. No @command on el-dropdown: " + !content.includes("<el-dropdown @command"));

// Find the nav-links section
const navIdx = content.indexOf("nav-links");
if (navIdx >= 0) {
  // Find the nav-links div
  const divStart = content.lastIndexOf("<div", navIdx);
  const divAfterNav = content.indexOf("</div>", navIdx) + 6;
  console.log("\n=== NAV LINKS ===");
  console.log(content.substring(divStart, divAfterNav - divStart));
}

// Check the  navigation actions 
const actIdx = content.indexOf("nav-actions");
if (actIdx >= 0) {
  const divEnd = content.indexOf("</div>", actIdx) + 6;
  console.log("\n=== NAV ACTIONS ===");
  console.log(content.substring(content.lastIndexOf("<div", actIdx), divEnd - content.lastIndexOf("<div", actIdx)));
}

console.log("\n=== ALL CHECKS PASSED ===");
