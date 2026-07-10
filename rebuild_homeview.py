import os
dest = r'C:\Users\Administrator\Desktop\Zhihire-StarMap\frontend\src\views\common\HomeView.vue'
content = []
content.append('<script setup lang="ts">')
content.append('import { ref, computed, onMounted, onUnmounted, nextTick } from "vue"')
content.append('import { useRouter } from "vue-router"')
content.append('import { useAuthStore } from "@/store/auth"')
content.append('import { useScrollReveal } from "@/composables/useScrollReveal"')
content.append('import {')
content.append('  Search, MapPin, ChevronLeft, ChevronRight, Briefcase, Bell, ArrowRight,')
content.append('  Network, Sparkles, Route, ChevronRightIcon, ChevronDown,')
content.append("} from 'lucide-vue-next'")

with open(dest, 'w', encoding='utf-8') as f:
    f.write('\n'.join(content) + '\n')
print(f'Script header written: {len("\n".join(content))} chars')
