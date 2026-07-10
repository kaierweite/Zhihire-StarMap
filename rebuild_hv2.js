const fs = require("fs");
const p = "C:\\Users\\Administrator\\Desktop\\Zhihire-StarMap\\frontend\\src\\views\\common\\HomeView.vue";
let c = '';

// ====== SCRIPT ======
c += '<script setup lang=\"ts\">\n';
c += 'import { ref, computed, onMounted, onUnmounted, nextTick } from \"vue\"\n';
c += 'import { useRouter } from \"vue-router\"\n';
c += 'import { useAuthStore } from \"@/store/auth\"\n';
c += 'import { useScrollReveal } from \"@/composables/useScrollReveal\"\n';
c += 'import {\n';
c += '  Search, MapPin, ChevronLeft, ChevronRight, Briefcase, Bell, ArrowRight,\n';
c += '  Network, Sparkles, Route, ChevronRightIcon, ChevronDown,\n';
c += "} from 'lucide-vue-next'\n\n";
c += 'const router = useRouter()\n';
c += 'const authStore = useAuthStore()\n';
c += 'const page = ref()\n';
c += 'useScrollReveal(page)\n\n';

// Hero, promo, search, categories, submenu, jobs, stats data (same as before)
c += "// ====== \u82f1\u96c4\u8f6e\u64ad ======\n";
c += 'const heroSlides = [\n';
c += "  'https://images.unsplash.com/photo-1521737604893-d14cc237f11d?w=1920&q=80&auto=format',\n";
c += "  'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=1920&q=80&auto=format',\n";
c += "  'https://images.unsplash.com/photo-1542744173-8e7e53415bb0?w=1920&q=80&auto=format',\n";
c += "  'https://images.unsplash.com/photo-1559136555-9303baea8ebd?w=1920&q=80&auto=format',\n";
c += ']\n';
c += 'const currentSlide = ref(0)\n';
c += 'let slideTimer = null\n';
c += 'function nextSlide() { currentSlide.value = (currentSlide.value + 1) % heroSlides.length }\n';
c += 'function prevSlide() { currentSlide.value = (currentSlide.value - 1 + heroSlides.length) % heroSlides.length }\n';
c += 'function goToSlide(i) { currentSlide.value = i }\n\n';

c += "// ====== \u63a8\u5e7f\u6a2a\u5e45\u8f6e\u64ad ======\n";
c += 'const promoSlides = [\n';
c += "  'https://images.unsplash.com/photo-1552664730-d307ca884978?w=1200&q=80&auto=format',\n";
c += "  'https://images.unsplash.com/photo-1553877522-43269d4ea984?w=1200&q=80&auto=format',\n";
c += "  'https://images.unsplash.com/photo-1600880292203-757bb62b4baf?w=1200&q=80&auto=format',\n";
c += ']\n';
c += 'const currentPromo = ref(0)\n';
c += 'let promoTimer = null\n';
c += 'function nextPromo() { currentPromo.value = (currentPromo.value + 1) % promoSlides.length }\n';
c += 'function prevPromo() { currentPromo.value = (currentPromo.value - 1 + promoSlides.length) % promoSlides.length }\n\n';

c += "// ====== \u641c\u7d22 ======\n";
c += 'const searchKeyword = ref(\"\")\n';
c += 'const searchCity = ref(\"\")\n';
c += 'function handleSearch() {\n';
c += '  router.push({ path: \"/user/jobs/search\", query: { q: searchKeyword.value, city: searchCity.value } })\n';
c += '}\n\n';

c += "// ====== \u5206\u7c7b\u4fa7\u8fb9\u680f ======\n";
c += "const activeCategoryTab = ref('profession')\n";
c += 'const hoveredCategory = ref(null)\n';
c += 'const professionCategories = [\n';
c += '  { key: \"engineering\", icon: \"\\ud83d\\udce1\", label: \"\u5de5\u5b66\", preview: \"\u5b89\u5168\u79d1\u5b66\u4e0e\u5de5\u7a0b\u7c7b\" },\n';

// (using known-good category data)
fs.writeFileSync(p, c, "utf-8");
console.log("Part 1 done: " + c.length + " chars");
