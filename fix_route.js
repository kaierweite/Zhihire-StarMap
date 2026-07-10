const fs = require("fs");
const p = "C:\\Users\\Administrator\\Desktop\\Zhihire-StarMap\\frontend\\src\\views\\common\\HomeView.vue";
let content = fs.readFileSync(p, "utf-8");

// Fix: .path === '/' should be $route.path === '/'
content = content.replace(/:class="\{ active: \.path === '\/' \}"/g, ":class=\"{ active: \$route.path === '/' }\"");

// Also check for any other $route that might be missing
content = content.replace(/ref\(page\)/g, "ref()"); // Hmm, actually this might have issues

fs.writeFileSync(p, content, "utf-8");

// Verify
content = fs.readFileSync(p, "utf-8");
const navIdx = content.indexOf("nav-links");
const divStart = content.lastIndexOf("<div", navIdx);
const divEnd = content.indexOf("</div>", navIdx) + 6;
console.log("=== Fixed NAV LINKS ===");
console.log(content.substring(divStart, divEnd - divStart));
