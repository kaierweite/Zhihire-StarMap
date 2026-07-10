const fs = require("fs");
const p = "C:\\Users\\Administrator\\Desktop\\Zhihire-StarMap\\frontend\\src\\views\\common\\HomeView.vue";

// Start clean: write the script section (same as before, but with ChevronDown import added)
let c = '';
c += '<script setup lang=\"ts\">\n';
c += 'import { ref, computed, onMounted, onUnmounted, nextTick } from \"vue\"\n';
c += 'import { useRouter } from \"vue-router\"\n';
c += 'import { useAuthStore } from \"@/store/auth\"\n';
c += 'import { useScrollReveal } from \"@/composables/useScrollReveal\"\n';
c += 'import {\n';
c += '  Search, MapPin, ChevronLeft, ChevronRight, Briefcase, Bell, ArrowRight,\n';
c += '  Network, Sparkles, Route, ChevronRightIcon, ChevronDown,\n';
c += "} from 'lucide-vue-next'\n\n";

fs.writeFileSync(p, c, "utf-8");
console.log("Script header written: " + c.length + " chars");
