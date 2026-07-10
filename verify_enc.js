const fs = require("fs");
const c = fs.readFileSync("C:\\Users\\Administrator\\Desktop\\Zhihire-StarMap\\test_out.txt", "utf-8");
console.log("Read back:", c.length, "chars");
console.log("Contains Chinese:", c.includes("????"));
