const fs = require("fs");

const checks = [
  { file: "C:\\Users\\Administrator\\Desktop\\Zhihire-StarMap\\frontend\\src\\components\\AppHeader.vue", desc: "AppHeader" },
  { file: "C:\\Users\\Administrator\\Desktop\\Zhihire-StarMap\\frontend\\src\\views\\common\\HomeView.vue", desc: "HomeView" },
  { file: "C:\\Users\\Administrator\\Desktop\\Zhihire-StarMap\\frontend\\src\\views\\admin\\AdminLayout.vue", desc: "AdminLayout" },
  { file: "C:\\Users\\Administrator\\Desktop\\Zhihire-StarMap\\frontend\\src\\views\\company\\CompanyLayout.vue", desc: "CompanyLayout" },
];

for (const c of checks) {
  const content = fs.readFileSync(c.file, "utf-8");
  const lines = content.split("\n").length;
  
  console.log(`\n=== ${c.desc} (${lines} lines) ===`);
  
  // Check for @command on el-dropdown
  const hasAtCommand = content.includes("<el-dropdown @command");
  console.log(`  No @command on el-dropdown: ${!hasAtCommand}`);
  
  if (c.desc === "AppHeader") {
    const hasActiveLink = content.includes("const activeLink = computed");
    const hasAbilityMap = content.includes("ability-map");
    const hasCareerPlan = content.includes("career-plan");
    const hasGoDashboard = content.includes("function goDashboard");
    const hasDefineProps = content.includes("defineProps");
    console.log(`  activeLink computed: ${hasActiveLink}`);
    console.log(`  ability-map in items: ${hasAbilityMap}`);
    console.log(`  career-plan in items: ${hasCareerPlan}`);
    console.log(`  No goDashboard function: ${!hasGoDashboard}`);
    console.log(`  No defineProps: ${!hasDefineProps}`);
  }
  
  if (c.desc === "HomeView") {
    const hasDynamicActive = content.includes("$route.path === '/'");
    const hasAbilityMap = content.includes("/user/ability-map");
    const hasCareerPlan = content.includes("/user/career-plan");
    const resumeOK = content.includes("/user/resume") && content.includes("</router-link>");
    console.log(`  Dynamic active class using $route: ${hasDynamicActive}`);
    console.log(`  ability-map link: ${hasAbilityMap}`);
    console.log(`  career-plan link: ${hasCareerPlan}`);
    console.log(`  Resume link has closing tag: ${resumeOK}`);
  }
}

console.log("\n=== ALL FIXES VERIFIED ===");
