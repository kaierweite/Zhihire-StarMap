const fs = require("fs");
const p = "C:\\Users\\Administrator\\Desktop\\Zhihire-StarMap\\frontend\\src\\views\\common\\HomeView.vue";
const content = fs.readFileSync(p, "utf-8");
const lines = content.split("\n");
console.log("Line 243:", lines[242].substring(0, 200));
