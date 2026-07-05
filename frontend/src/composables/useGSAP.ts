import { onMounted, onUnmounted, type Ref } from 'vue'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

/**
 * Vue 3 composable for GSAP animations with automatic cleanup.
 * Usage:
 *   const container = ref<HTMLElement>()
 *   useGSAP(container, (gsap, st) => {
 *     gsap.from('.item', { y: 40, autoAlpha: 0, stagger: 0.1 })
 *   })
 */
export function useGSAP(
  scope: Ref<HTMLElement | undefined>,
  setup: (gsap: typeof import('gsap').gsap, st: typeof ScrollTrigger) => void,
) {
  let ctx: gsap.Context

  onMounted(() => {
    if (!scope.value) return
    ctx = gsap.context(() => {
      setup(gsap, ScrollTrigger)
    }, scope.value)
  })

  onUnmounted(() => {
    ctx?.revert()
  })
}

export { gsap, ScrollTrigger }
