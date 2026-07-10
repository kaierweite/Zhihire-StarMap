const fs = require("fs");
const p = "C:\\Users\\Administrator\\Desktop\\Zhihire-StarMap\\frontend\\src\\views\\common\\HomeView.vue";
const content = fs.readFileSync(p, "utf-8");
const lines = content.split("\n");

// Get line 243 (0-indexed: 242)
const line = lines[242];
console.log("Line 243 raw:");
for (let i = 0; i < line.length; i++) {
  process.stdout.write(`[${i}:${line.charCodeAt(i)}/'${line[i]}'] `);
  if (i % 10 === 9) process.stdout.write("\n");
}
