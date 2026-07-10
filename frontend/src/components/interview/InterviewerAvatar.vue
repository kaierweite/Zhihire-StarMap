<template>
  <div class="avatar-container" :style="{ width: size + 'px', height: size + 'px' }">
    <canvas ref="canvasRef" :width="size" :height="size" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from "vue"

const props = withDefaults(defineProps<{
  size?: number
  speaking?: boolean
}>(), {
  size: 280,
  speaking: false,
})

const canvasRef = ref<HTMLCanvasElement>()
let animFrame = 0
let blinkTimer: ReturnType<typeof setInterval> | null = null
let mouthPhase = 0

function draw() {
  const c = canvasRef.value
  if (!c) return
  const ctx = c.getContext("2d")
  if (!ctx) return
  const w = c.width
  const h = c.height

  ctx.clearRect(0, 0, w, h)

  // Background circle
  const cx = w / 2
  const cy = h * 0.44
  const r = w * 0.42

  // Gradient background
  const grad = ctx.createRadialGradient(cx - 20, cy - 30, 10, cx, cy, r)
  grad.addColorStop(0, "#e8f4f8")
  grad.addColorStop(0.6, "#d0e8f0")
  grad.addColorStop(1, "#b8d8e8")
  ctx.beginPath()
  ctx.arc(cx, cy, r, 0, Math.PI * 2)
  ctx.fillStyle = grad
  ctx.fill()

  // Hair
  ctx.fillStyle = "#2c3e50"
  ctx.beginPath()
  ctx.ellipse(cx, cy - r * 0.5, r * 0.7, r * 0.5, 0, Math.PI, 0)
  ctx.fill()

  // Hair top
  ctx.beginPath()
  ctx.ellipse(cx, cy - r * 0.7, r * 0.5, r * 0.3, 0, Math.PI, 0)
  ctx.fill()

  // Ears
  ctx.fillStyle = "#f0c8a0"
  ctx.beginPath()
  ctx.ellipse(cx - r * 0.85, cy - r * 0.1, r * 0.12, r * 0.2, 0, 0, Math.PI * 2)
  ctx.fill()
  ctx.beginPath()
  ctx.ellipse(cx + r * 0.85, cy - r * 0.1, r * 0.12, r * 0.2, 0, 0, Math.PI * 2)
  ctx.fill()

  // Face
  ctx.fillStyle = "#f5d0b8"
  ctx.beginPath()
  ctx.ellipse(cx, cy, r * 0.6, r * 0.65, 0, 0, Math.PI * 2)
  ctx.fill()

  // Eyes
  const eyeY = cy - r * 0.1
  const eyeSpacing = r * 0.22
  const eyeR = r * 0.07
  const blinkHeight = Math.abs(Math.sin(Date.now() / 3000)) < 0.05 ? 0.02 : 1

  // Eye whites
  ctx.fillStyle = "#ffffff"
  ctx.beginPath()
  ctx.ellipse(cx - eyeSpacing, eyeY, eyeR, eyeR * blinkHeight, 0, 0, Math.PI * 2)
  ctx.fill()
  ctx.beginPath()
  ctx.ellipse(cx + eyeSpacing, eyeY, eyeR, eyeR * blinkHeight, 0, 0, Math.PI * 2)
  ctx.fill()

  // Iris
  if (blinkHeight > 0.1) {
    ctx.fillStyle = "#2c3e50"
    ctx.beginPath()
    ctx.arc(cx - eyeSpacing + 2, eyeY, eyeR * 0.55, 0, Math.PI * 2)
    ctx.fill()
    ctx.beginPath()
    ctx.arc(cx + eyeSpacing + 2, eyeY, eyeR * 0.55, 0, Math.PI * 2)
    ctx.fill()

    // Pupils
    ctx.fillStyle = "#1a1a2e"
    ctx.beginPath()
    ctx.arc(cx - eyeSpacing + 3, eyeY, eyeR * 0.25, 0, Math.PI * 2)
    ctx.fill()
    ctx.beginPath()
    ctx.arc(cx + eyeSpacing + 3, eyeY, eyeR * 0.25, 0, Math.PI * 2)
    ctx.fill()

    // Eye shine
    ctx.fillStyle = "#ffffff"
    ctx.beginPath()
    ctx.arc(cx - eyeSpacing - 2, eyeY - 3, eyeR * 0.15, 0, Math.PI * 2)
    ctx.fill()
    ctx.beginPath()
    ctx.arc(cx + eyeSpacing - 2, eyeY - 3, eyeR * 0.15, 0, Math.PI * 2)
    ctx.fill()
  }

  // Eyebrows
  ctx.strokeStyle = "#5d4e37"
  ctx.lineWidth = 2
  ctx.beginPath()
  ctx.moveTo(cx - eyeSpacing - eyeR * 0.8, eyeY - eyeR * 1.5)
  ctx.quadraticCurveTo(cx - eyeSpacing, eyeY - eyeR * 2, cx - eyeSpacing + eyeR * 0.8, eyeY - eyeR * 1.5)
  ctx.stroke()
  ctx.beginPath()
  ctx.moveTo(cx + eyeSpacing - eyeR * 0.8, eyeY - eyeR * 1.5)
  ctx.quadraticCurveTo(cx + eyeSpacing, eyeY - eyeR * 2, cx + eyeSpacing + eyeR * 0.8, eyeY - eyeR * 1.5)
  ctx.stroke()

  // Nose
  ctx.strokeStyle = "#d4a88a"
  ctx.lineWidth = 1.5
  ctx.beginPath()
  ctx.moveTo(cx, cy + r * 0.02)
  ctx.lineTo(cx - r * 0.04, cy + r * 0.18)
  ctx.quadraticCurveTo(cx, cy + r * 0.22, cx + r * 0.04, cy + r * 0.18)
  ctx.stroke()

  // Mouth - animated when speaking
  const mouthY = cy + r * 0.28
  const mouthW = r * 0.2

  if (props.speaking) {
    // Animated mouth shape
    mouthPhase += 0.15
    const openAmount = 0.3 + Math.sin(mouthPhase) * 0.2
    ctx.fillStyle = "#c0392b"
    ctx.beginPath()
    ctx.ellipse(cx, mouthY, mouthW * 0.5, mouthW * openAmount * 0.4, 0, 0, Math.PI * 2)
    ctx.fill()

    // Teeth
    ctx.fillStyle = "#ffffff"
    ctx.beginPath()
    ctx.ellipse(cx, mouthY - mouthW * openAmount * 0.15, mouthW * 0.35, mouthW * openAmount * 0.12, 0, 0, Math.PI)
    ctx.fill()
  } else {
    // Normal smile
    ctx.strokeStyle = "#c0392b"
    ctx.lineWidth = 2.5
    ctx.beginPath()
    ctx.arc(cx, mouthY, mouthW * 0.5, 0.1, Math.PI - 0.1)
    ctx.stroke()
  }

  // Suit collar
  ctx.fillStyle = "#1a3a5c"
  ctx.beginPath()
  ctx.moveTo(cx - r * 0.6, cy + r * 0.55)
  ctx.lineTo(cx, cy + r * 0.75)
  ctx.lineTo(cx + r * 0.6, cy + r * 0.55)
  ctx.lineTo(cx + r * 0.4, cy + r * 0.65)
  ctx.lineTo(cx, cy + r * 0.85)
  ctx.lineTo(cx - r * 0.4, cy + r * 0.65)
  ctx.closePath()
  ctx.fill()

  // Tie
  ctx.fillStyle = "#c0392b"
  ctx.beginPath()
  ctx.moveTo(cx - r * 0.06, cy + r * 0.65)
  ctx.quadraticCurveTo(cx, cy + r * 0.95, cx + r * 0.06, cy + r * 0.65)
  ctx.closePath()
  ctx.fill()
}

function animate() {
  draw()
  animFrame = requestAnimationFrame(animate)
}

onMounted(() => {
  animate()
})

onUnmounted(() => {
  cancelAnimationFrame(animFrame)
  if (blinkTimer) clearInterval(blinkTimer)
})
</script>

<style scoped>
.avatar-container {
  border-radius: 50%;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  background: #fff;
  flex-shrink: 0;
}
canvas {
  display: block;
  width: 100%;
  height: 100%;
}
</style>
