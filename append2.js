const fs = require('fs');
const p = "C:\\Users\\Administrator\\Desktop\\Zhihire-StarMap\\frontend\\src\\views\\common\\HomeView.vue";
let c = '';

// ====== Hero slides ======
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

// ====== Promo slides ======
c += 'const promoSlides = [\n';
c += "  'https://images.unsplash.com/photo-1552664730-d307ca884978?w=1200&q=80&auto=format',\n";
c += "  'https://images.unsplash.com/photo-1553877522-43269d4ea984?w=1200&q=80&auto=format',\n";
c += "  'https://images.unsplash.com/photo-1600880292203-757bb62b4baf?w=1200&q=80&auto=format',\n";
c += ']\n';
c += 'const currentPromo = ref(0)\n';
c += 'let promoTimer = null\n';
c += 'function nextPromo() { currentPromo.value = (currentPromo.value + 1) % promoSlides.length }\n';
c += 'function prevPromo() { currentPromo.value = (currentPromo.value - 1 + promoSlides.length) % promoSlides.length }\n\n';

// ====== Search ======
c += 'const searchKeyword = ref("")\n';
c += 'const searchCity = ref("")\n';
c += 'function handleSearch() {\n';
c += '  router.push({ path: "/user/jobs/search", query: { q: searchKeyword.value, city: searchCity.value } })\n';
c += '}\n\n';

// ====== Categories ======
c += "const activeCategoryTab = ref('profession')\n";
c += 'const hoveredCategory = ref(null)\n\n';

fs.appendFileSync(p, c, 'utf-8');
console.log('Part 2 done, total appended: ' + c.length + ' chars');
