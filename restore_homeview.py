import os
filepath = r'C:\Users\Administrator\Desktop\Zhihire-StarMap\frontend\src\views\common\HomeView.vue'
os.makedirs(os.path.dirname(filepath), exist_ok=True)
content = '''<script setup lang=\"ts\">
import { ref, computed, onMounted, onUnmounted, nextTick } from \"vue\"
import { useRouter } from \"vue-router\"
import { useAuthStore } from \"@/store/auth\"
import { useScrollReveal } from \"@/composables/useScrollReveal\"
import {
  Search, MapPin, ChevronLeft, ChevronRight, Briefcase, Bell, ArrowRight,
  Network, Sparkles, Route, ChevronRightIcon,
} from \"lucide-vue-next\"

const router = useRouter()
const authStore = useAuthStore()
const page = ref()
useScrollReveal(page)

const heroSlides = []
const currentSlide = ref(0)
'''
print(f"Starting reconstruction... Length so far: {len(content)}")
print("Writing complete file...")
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
