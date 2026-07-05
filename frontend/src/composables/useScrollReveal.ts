import { onMounted, onUnmounted, type Ref } from 'vue'

/**
 * 轻量滚动渐入 composable — 基于 IntersectionObserver，无外部依赖。
 * 元素进入视口时自动添加 .revealed 类，配合 CSS transition 实现渐入。
 */
export function useScrollReveal(container: Ref<HTMLElement | undefined>) {
  let observer: IntersectionObserver | null = null

  onMounted(() => {
    if (!container.value) return
    observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('revealed')
            observer?.unobserve(entry.target)
          }
        })
      },
      { threshold: 0.15, rootMargin: '0px 0px -60px 0px' },
    )
    container.value.querySelectorAll('.reveal').forEach((el) => {
      observer!.observe(el)
    })
  })

  onUnmounted(() => {
    observer?.disconnect()
  })
}
