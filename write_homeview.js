const fs = require('fs');
const path = r'C:\Users\Administrator\Desktop\Zhihire-StarMap\frontend\src\views\common\HomeView.vue';

let content = '';
content += '<script setup lang="ts">\n';
content += 'import { ref, computed, onMounted, onUnmounted, nextTick } from "vue"\n';
content += 'import { useRouter } from "vue-router"\n';
content += 'import { useAuthStore } from "@/store/auth"\n';
content += 'import { useScrollReveal } from "@/composables/useScrollReveal"\n';
content += 'import {\n';
content += '  Search, MapPin, ChevronLeft, ChevronRight, Briefcase, Bell, ArrowRight,\n';
content += '  Network, Sparkles, Route, ChevronRightIcon,\n';
content += "} from 'lucide-vue-next'\n";

fs.writeFileSync(path, content, 'utf-8');
console.log('Partial write done: ' + content.length + ' chars');
