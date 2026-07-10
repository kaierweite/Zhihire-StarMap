<template>
  <div class="avatar-container" :class="{ 'speaking': speaking }">
    <canvas ref="canvasRef" :width="canvasWidth" :height="canvasHeight" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from "vue"

const props = withDefaults(defineProps<{
  size?: number
  speaking?: boolean
}>(), {
  size: 400,
  speaking: false,
})

const canvasWidth = computed(() => props.size * 0.8)
const canvasHeight = computed(() => props.size)

const canvasRef = ref<HTMLCanvasElement>()
let animFrame = 0
let mouthPhase = 0

function draw() {
  const c = canvasRef.value
  if (!c) return
  const ctx = c.getContext("2d")
  if (!ctx) return
  const w = c.width
  const h = c.height

  ctx.clearRect(0, 0, w, h)

  const cx = w / 2
  const cy = h / 2
  const scale = w / 400

  const breathingOffset = Math.sin(Date.now() / 2500) * 3 * scale
  const idleHeadOffset = Math.sin(Date.now() / 4000) * 2 * scale
  const eyeYOffset = Math.sin(Date.now() / 3000) * 1 * scale

  // Background gradient
  const bgGrad = ctx.createLinearGradient(0, 0, 0, h)
  bgGrad.addColorStop(0, '#e8e8e8')
  bgGrad.addColorStop(1, '#d0d0d0')
  ctx.fillStyle = bgGrad
  ctx.fillRect(0, 0, w, h)

  // Face shape
  const faceY = cy - h * 0.05 + idleHeadOffset
  const faceWidth = w * 0.65
  const faceHeight = w * 0.8
  
  const faceGrad = ctx.createRadialGradient(
    cx - faceWidth * 0.15, faceY - faceHeight * 0.15, 10 * scale,
    cx, faceY, faceWidth * 0.6
  )
  faceGrad.addColorStop(0, '#fdf0e6')
  faceGrad.addColorStop(0.5, '#f5e6d3')
  faceGrad.addColorStop(1, '#e8d5c4')

  ctx.fillStyle = faceGrad
  ctx.beginPath()
  ctx.ellipse(cx + idleHeadOffset, faceY, faceWidth * 0.5, faceHeight * 0.5, 0, 0, Math.PI * 2)
  ctx.fill()

  // Neck
  const neckWidth = faceWidth * 0.25
  const neckHeight = faceHeight * 0.25
  ctx.fillStyle = '#f0d8c0'
  ctx.beginPath()
  ctx.moveTo(cx - neckWidth * 0.5 + idleHeadOffset * 0.3, faceY + faceHeight * 0.45)
  ctx.lineTo(cx - neckWidth * 0.4 + idleHeadOffset * 0.3, faceY + faceHeight * 0.45 + neckHeight + breathingOffset)
  ctx.lineTo(cx + neckWidth * 0.4 + idleHeadOffset * 0.3, faceY + faceHeight * 0.45 + neckHeight + breathingOffset)
  ctx.lineTo(cx + neckWidth * 0.5 + idleHeadOffset * 0.3, faceY + faceHeight * 0.45)
  ctx.closePath()
  ctx.fill()

  // Hair - realistic dark brown
  ctx.fillStyle = '#3d3d3d'
  ctx.beginPath()
  ctx.ellipse(cx + idleHeadOffset * 0.5, faceY - faceHeight * 0.4, faceWidth * 0.55, faceHeight * 0.35, 0, Math.PI, 0)
  ctx.fill()

  ctx.fillStyle = '#2d2d2d'
  ctx.beginPath()
  ctx.ellipse(cx - faceWidth * 0.55 + idleHeadOffset * 0.3, faceY - faceHeight * 0.05 + idleHeadOffset, faceWidth * 0.15, faceHeight * 0.25, -0.2, 0, Math.PI * 2)
  ctx.fill()
  ctx.beginPath()
  ctx.ellipse(cx + faceWidth * 0.55 + idleHeadOffset * 0.3, faceY - faceHeight * 0.05 + idleHeadOffset, faceWidth * 0.15, faceHeight * 0.25, 0.2, 0, Math.PI * 2)
  ctx.fill()

  // Hair highlights
  ctx.fillStyle = '#4a4a4a'
  ctx.beginPath()
  ctx.ellipse(cx + idleHeadOffset * 0.5, faceY - faceHeight * 0.35, faceWidth * 0.45, faceHeight * 0.25, 0, Math.PI, 0)
  ctx.fill()

  // Eyebrows
  const browY = faceY - faceHeight * 0.12 + eyeYOffset
  const browSpacing = faceWidth * 0.22
  
  ctx.strokeStyle = '#4a3a2a'
  ctx.lineWidth = 2.5 * scale
  ctx.lineCap = 'round'
  
  ctx.beginPath()
  ctx.moveTo(cx - browSpacing - faceWidth * 0.08 + idleHeadOffset * 0.3, browY)
  ctx.quadraticCurveTo(cx - browSpacing + idleHeadOffset * 0.3, browY - faceHeight * 0.05, cx - browSpacing + faceWidth * 0.08 + idleHeadOffset * 0.3, browY)
  ctx.stroke()
  
  ctx.beginPath()
  ctx.moveTo(cx + browSpacing - faceWidth * 0.08 + idleHeadOffset * 0.3, browY)
  ctx.quadraticCurveTo(cx + browSpacing + idleHeadOffset * 0.3, browY - faceHeight * 0.05, cx + browSpacing + faceWidth * 0.08 + idleHeadOffset * 0.3, browY)
  ctx.stroke()

  // Eyes
  const eyeY = faceY - faceHeight * 0.02 + eyeYOffset
  const eyeSpacing = faceWidth * 0.22
  const eyeR = faceWidth * 0.08
  
  const blinkHeight = Math.abs(Math.sin(Date.now() / 4500)) < 0.06 ? 0.05 : 1

  // Eye whites
  ctx.fillStyle = '#ffffff'
  ctx.beginPath()
  ctx.ellipse(cx - eyeSpacing + idleHeadOffset * 0.3, eyeY, eyeR, eyeR * blinkHeight, 0.03, 0, Math.PI * 2)
  ctx.fill()
  ctx.beginPath()
  ctx.ellipse(cx + eyeSpacing + idleHeadOffset * 0.3, eyeY, eyeR, eyeR * blinkHeight, -0.03, 0, Math.PI * 2)
  ctx.fill()

  if (blinkHeight > 0.1) {
    // Iris
    ctx.fillStyle = '#4a6fa5'
    ctx.beginPath()
    ctx.arc(cx - eyeSpacing + 1 * scale + idleHeadOffset * 0.3, eyeY, eyeR * 0.55, 0, Math.PI * 2)
    ctx.fill()
    ctx.beginPath()
    ctx.arc(cx + eyeSpacing + 1 * scale + idleHeadOffset * 0.3, eyeY, eyeR * 0.55, 0, Math.PI * 2)
    ctx.fill()

    // Pupil
    ctx.fillStyle = '#2c3e50'
    ctx.beginPath()
    ctx.arc(cx - eyeSpacing + 2 * scale + idleHeadOffset * 0.3, eyeY + 1 * scale, eyeR * 0.28, 0, Math.PI * 2)
    ctx.fill()
    ctx.beginPath()
    ctx.arc(cx + eyeSpacing + 2 * scale + idleHeadOffset * 0.3, eyeY + 1 * scale, eyeR * 0.28, 0, Math.PI * 2)
    ctx.fill()

    // Eye shine
    ctx.fillStyle = '#ffffff'
    ctx.beginPath()
    ctx.arc(cx - eyeSpacing - 1 * scale + idleHeadOffset * 0.3, eyeY - 2 * scale, eyeR * 0.15, 0, Math.PI * 2)
    ctx.fill()
    ctx.beginPath()
    ctx.arc(cx + eyeSpacing - 1 * scale + idleHeadOffset * 0.3, eyeY - 2 * scale, eyeR * 0.15, 0, Math.PI * 2)
    ctx.fill()
  }

  // Eye bags
  ctx.fillStyle = 'rgba(200, 180, 160, 0.25)'
  ctx.beginPath()
  ctx.ellipse(cx - eyeSpacing + idleHeadOffset * 0.3, eyeY + eyeR * 0.7, eyeR * 0.8, eyeR * 0.3, 0, 0, Math.PI * 2)
  ctx.fill()
  ctx.beginPath()
  ctx.ellipse(cx + eyeSpacing + idleHeadOffset * 0.3, eyeY + eyeR * 0.7, eyeR * 0.8, eyeR * 0.3, 0, 0, Math.PI * 2)
  ctx.fill()

  // Nose
  const noseY = faceY + faceHeight * 0.08
  ctx.strokeStyle = '#d4b8a0'
  ctx.lineWidth = 1.8 * scale
  
  ctx.beginPath()
  ctx.moveTo(cx + idleHeadOffset * 0.3, noseY)
  ctx.lineTo(cx - faceWidth * 0.03 + idleHeadOffset * 0.3, noseY + faceHeight * 0.1)
  ctx.quadraticCurveTo(cx + idleHeadOffset * 0.3, noseY + faceHeight * 0.13, cx + faceWidth * 0.03 + idleHeadOffset * 0.3, noseY + faceHeight * 0.1)
  ctx.stroke()

  // Nose bridge shadow
  ctx.fillStyle = 'rgba(200, 180, 160, 0.15)'
  ctx.beginPath()
  ctx.moveTo(cx + idleHeadOffset * 0.3, noseY)
  ctx.lineTo(cx + faceWidth * 0.08 + idleHeadOffset * 0.3, noseY + faceHeight * 0.08)
  ctx.lineTo(cx + faceWidth * 0.03 + idleHeadOffset * 0.3, noseY + faceHeight * 0.1)
  ctx.closePath()
  ctx.fill()

  // Glasses
  ctx.strokeStyle = '#3d3d3d'
  ctx.lineWidth = 2 * scale
  const glassR = eyeR * 1.4
  
  ctx.beginPath()
  ctx.ellipse(cx - eyeSpacing + idleHeadOffset * 0.3, eyeY, glassR, glassR * 0.8, 0.03, 0, Math.PI * 2)
  ctx.stroke()
  ctx.beginPath()
  ctx.ellipse(cx + eyeSpacing + idleHeadOffset * 0.3, eyeY, glassR, glassR * 0.8, -0.03, 0, Math.PI * 2)
  ctx.stroke()
  
  ctx.beginPath()
  ctx.moveTo(cx - eyeSpacing + glassR * 0.8 + idleHeadOffset * 0.3, eyeY)
  ctx.lineTo(cx + eyeSpacing - glassR * 0.8 + idleHeadOffset * 0.3, eyeY)
  ctx.stroke()
  
  ctx.beginPath()
  ctx.moveTo(cx - eyeSpacing - glassR * 0.8 + idleHeadOffset * 0.3, eyeY - glassR * 0.25)
  ctx.lineTo(cx - faceWidth * 0.55 + idleHeadOffset * 0.3, faceY - faceHeight * 0.3)
  ctx.stroke()
  ctx.beginPath()
  ctx.moveTo(cx + eyeSpacing + glassR * 0.8 + idleHeadOffset * 0.3, eyeY - glassR * 0.25)
  ctx.lineTo(cx + faceWidth * 0.55 + idleHeadOffset * 0.3, faceY - faceHeight * 0.3)
  ctx.stroke()

  // Glasses reflection
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)'
  ctx.lineWidth = 1 * scale
  ctx.beginPath()
  ctx.moveTo(cx - eyeSpacing - glassR * 0.5 + idleHeadOffset * 0.3, eyeY - glassR * 0.4)
  ctx.lineTo(cx - eyeSpacing - glassR * 0.1 + idleHeadOffset * 0.3, eyeY - glassR * 0.2)
  ctx.stroke()
  ctx.beginPath()
  ctx.moveTo(cx + eyeSpacing - glassR * 0.5 + idleHeadOffset * 0.3, eyeY - glassR * 0.4)
  ctx.lineTo(cx + eyeSpacing - glassR * 0.1 + idleHeadOffset * 0.3, eyeY - glassR * 0.2)
  ctx.stroke()

  // Mouth
  const mouthY = faceY + faceHeight * 0.25

  if (props.speaking) {
    mouthPhase += 0.18
    const openAmount = 0.2 + Math.sin(mouthPhase) * 0.15
    
    // Mouth opening
    ctx.fillStyle = '#3d2822'
    ctx.beginPath()
    ctx.ellipse(cx + idleHeadOffset * 0.3, mouthY + faceHeight * 0.02, faceWidth * 0.15, faceHeight * 0.08 * openAmount, 0, 0, Math.PI * 2)
    ctx.fill()

    // Tongue
    ctx.fillStyle = '#c05555'
    ctx.beginPath()
    ctx.ellipse(cx + idleHeadOffset * 0.3, mouthY + faceHeight * 0.03 + faceHeight * 0.04 * openAmount, faceWidth * 0.1, faceHeight * 0.03 * openAmount, 0, 0, Math.PI)
    ctx.fill()

    // Teeth
    ctx.fillStyle = '#ffffff'
    ctx.beginPath()
    ctx.ellipse(cx + idleHeadOffset * 0.3, mouthY - faceHeight * 0.01, faceWidth * 0.12, faceHeight * 0.02, 0, Math.PI, 0)
    ctx.fill()
  } else {
    // Closed mouth
    ctx.strokeStyle = '#8b4557'
    ctx.lineWidth = 2 * scale
    ctx.beginPath()
    ctx.arc(cx + idleHeadOffset * 0.3, mouthY, faceWidth * 0.14, 0.15, Math.PI - 0.15)
    ctx.stroke()

    // Lip color
    ctx.fillStyle = 'rgba(139, 69, 87, 0.15)'
    ctx.beginPath()
    ctx.arc(cx + idleHeadOffset * 0.3, mouthY, faceWidth * 0.14, 0.15, Math.PI - 0.15)
    ctx.fill()
  }

  // Smile lines
  ctx.strokeStyle = 'rgba(200, 180, 160, 0.3)'
  ctx.lineWidth = 1.5 * scale
  ctx.beginPath()
  ctx.moveTo(cx - faceWidth * 0.15 + idleHeadOffset * 0.3, mouthY - faceHeight * 0.03)
  ctx.quadraticCurveTo(cx - faceWidth * 0.25 + idleHeadOffset * 0.3, mouthY, cx - faceWidth * 0.28 + idleHeadOffset * 0.3, mouthY + faceHeight * 0.05)
  ctx.stroke()
  ctx.beginPath()
  ctx.moveTo(cx + faceWidth * 0.15 + idleHeadOffset * 0.3, mouthY - faceHeight * 0.03)
  ctx.quadraticCurveTo(cx + faceWidth * 0.25 + idleHeadOffset * 0.3, mouthY, cx + faceWidth * 0.28 + idleHeadOffset * 0.3, mouthY + faceHeight * 0.05)
  ctx.stroke()

  // Cheeks
  ctx.fillStyle = 'rgba(255, 180, 180, 0.2)'
  ctx.beginPath()
  ctx.ellipse(cx - faceWidth * 0.28 + idleHeadOffset * 0.3, faceY + faceHeight * 0.12, faceWidth * 0.12, faceHeight * 0.08, -0.1, 0, Math.PI * 2)
  ctx.fill()
  ctx.beginPath()
  ctx.ellipse(cx + faceWidth * 0.28 + idleHeadOffset * 0.3, faceY + faceHeight * 0.12, faceWidth * 0.12, faceHeight * 0.08, 0.1, 0, Math.PI * 2)
  ctx.fill()

  // Face shadow
  ctx.fillStyle = 'rgba(0, 0, 0, 0.05)'
  ctx.beginPath()
  ctx.ellipse(cx + faceWidth * 0.15 + idleHeadOffset * 0.3, faceY + faceHeight * 0.1, faceWidth * 0.3, faceHeight * 0.4, 0.1, 0, Math.PI * 2)
  ctx.fill()

  // Suit jacket
  const jacketY = faceY + faceHeight * 0.42 + breathingOffset
  
  ctx.fillStyle = '#2c3e50'
  ctx.beginPath()
  ctx.moveTo(cx - faceWidth * 0.75, faceY + faceHeight * 0.42)
  ctx.lineTo(cx - faceWidth * 0.55, jacketY + faceHeight * 0.25)
  ctx.lineTo(cx - faceWidth * 0.4, jacketY + faceHeight * 0.6)
  ctx.lineTo(cx, jacketY + faceHeight * 0.85)
  ctx.lineTo(cx + faceWidth * 0.4, jacketY + faceHeight * 0.6)
  ctx.lineTo(cx + faceWidth * 0.55, jacketY + faceHeight * 0.25)
  ctx.lineTo(cx + faceWidth * 0.75, faceY + faceHeight * 0.42)
  ctx.closePath()
  ctx.fill()

  // Jacket lapels
  ctx.fillStyle = '#1a252f'
  ctx.beginPath()
  ctx.moveTo(cx - neckWidth * 0.5 + idleHeadOffset * 0.3, faceY + faceHeight * 0.42)
  ctx.lineTo(cx - faceWidth * 0.35, jacketY + faceHeight * 0.2)
  ctx.lineTo(cx - neckWidth * 0.2 + idleHeadOffset * 0.3, jacketY + faceHeight * 0.35)
  ctx.closePath()
  ctx.fill()
  
  ctx.beginPath()
  ctx.moveTo(cx + neckWidth * 0.5 + idleHeadOffset * 0.3, faceY + faceHeight * 0.42)
  ctx.lineTo(cx + faceWidth * 0.35, jacketY + faceHeight * 0.2)
  ctx.lineTo(cx + neckWidth * 0.2 + idleHeadOffset * 0.3, jacketY + faceHeight * 0.35)
  ctx.closePath()
  ctx.fill()

  // Shirt collar
  ctx.fillStyle = '#e8e8e8'
  ctx.beginPath()
  ctx.moveTo(cx - neckWidth * 0.35 + idleHeadOffset * 0.3, faceY + faceHeight * 0.42)
  ctx.lineTo(cx, jacketY + faceHeight * 0.12)
  ctx.lineTo(cx + neckWidth * 0.35 + idleHeadOffset * 0.3, faceY + faceHeight * 0.42)
  ctx.closePath()
  ctx.fill()

  // Tie
  ctx.fillStyle = '#c0392b'
  ctx.beginPath()
  ctx.moveTo(cx - neckWidth * 0.08 + idleHeadOffset * 0.3, jacketY + faceHeight * 0.1)
  ctx.lineTo(cx - neckWidth * 0.04 + idleHeadOffset * 0.3, jacketY + faceHeight * 0.35)
  ctx.lineTo(cx + neckWidth * 0.04 + idleHeadOffset * 0.3, jacketY + faceHeight * 0.35)
  ctx.lineTo(cx + neckWidth * 0.08 + idleHeadOffset * 0.3, jacketY + faceHeight * 0.1)
  ctx.closePath()
  ctx.fill()

  // Tie knot
  ctx.beginPath()
  ctx.moveTo(cx - neckWidth * 0.08 + idleHeadOffset * 0.3, jacketY + faceHeight * 0.1)
  ctx.quadraticCurveTo(cx + idleHeadOffset * 0.3, jacketY + faceHeight * 0.05, cx + neckWidth * 0.08 + idleHeadOffset * 0.3, jacketY + faceHeight * 0.1)
  ctx.closePath()
  ctx.fill()

  // Jacket pocket
  ctx.fillStyle = '#34495e'
  ctx.beginPath()
  ctx.moveTo(cx + faceWidth * 0.22, jacketY + faceHeight * 0.3)
  ctx.lineTo(cx + faceWidth * 0.42, jacketY + faceHeight * 0.3)
  ctx.lineTo(cx + faceWidth * 0.4, jacketY + faceHeight * 0.5)
  ctx.lineTo(cx + faceWidth * 0.2, jacketY + faceHeight * 0.48)
  ctx.closePath()
  ctx.fill()

  // Shoulder shadow
  ctx.fillStyle = 'rgba(0, 0, 0, 0.1)'
  ctx.beginPath()
  ctx.moveTo(cx - faceWidth * 0.75, faceY + faceHeight * 0.42)
  ctx.lineTo(cx - faceWidth * 0.55, jacketY + faceHeight * 0.25)
  ctx.lineTo(cx - faceWidth * 0.65, jacketY + faceHeight * 0.15)
  ctx.closePath()
  ctx.fill()

  // Hand
  ctx.fillStyle = '#f0d8c0'
  ctx.beginPath()
  ctx.ellipse(cx - faceWidth * 0.4, jacketY + faceHeight * 0.75, faceWidth * 0.12, faceHeight * 0.08, -0.3, 0, Math.PI * 2)
  ctx.fill()

  // Sleeve
  ctx.fillStyle = '#34495e'
  ctx.beginPath()
  ctx.moveTo(cx - faceWidth * 0.55, jacketY + faceHeight * 0.25)
  ctx.lineTo(cx - faceWidth * 0.45, jacketY + faceHeight * 0.65)
  ctx.lineTo(cx - faceWidth * 0.28, jacketY + faceHeight * 0.78)
  ctx.lineTo(cx - faceWidth * 0.38, jacketY + faceHeight * 0.45)
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
})
</script>

<style scoped>
.avatar-container {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: transform 0.1s ease-out;
  
  &.speaking {
    animation: speaking-bob 0.3s ease-in-out infinite;
  }
}

@keyframes speaking-bob {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-2px); }
}

canvas {
  display: block;
  border-radius: 8px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}
</style>
