const fs = require("fs");
const p = "C:\\Users\\Administrator\\Desktop\\Zhihire-StarMap\\frontend\\src\\views\\common\\HomeView.vue";
let content = fs.readFileSync(p, "utf-8");

// Read the raw line to see what we're working with
const lines = content.split("\n");
console.log("Line 243 raw:", JSON.stringify(lines[242]));

// Fix the template literal: replace `url(`{img}`)` with `url(${img})`
const oldStr = "`url(`{img}`)";
const newStr = "`url(${img})";
if (content.includes(oldStr)) {
  content = content.replace(oldStr, newStr);
  fs.writeFileSync(p, content, "utf-8");
  console.log("Fixed using exact string match");
} else {
  console.log("Exact string not found, trying alternatives");
  // Check for what characters are actually there
  const idx = content.indexOf("url(");
  if (idx >= 0) {
    const ctx = content.substring(idx, idx + 50);
    console.log("Context around url():", JSON.stringify(ctx));
    
    // Find the style attribute with backgroundImage
    const styleIdx = content.indexOf("backgroundImage");
    if (styleIdx >= 0) {
      const ctx2 = content.substring(styleIdx, styleIdx + 60);
      console.log("backgroundImage context:", JSON.stringify(ctx2));
    }
  }
}
