<template>
  <div class="avatar-container">
    <canvas ref="canvasRef" :width="canvasWidth" :height="canvasHeight" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from "vue"

const props = withDefaults(defineProps<{
  size?: number
  isTalking?: boolean
  isListening?: boolean
}>(), {
  size: 400,
  isTalking: false,
  isListening: false,
})

const canvasWidth = computed(() => props.size * 0.8)
const canvasHeight = computed(() => props.size)

const canvasRef = ref<HTMLCanvasElement>()
let staticCanvas: HTMLCanvasElement | null = null
let animFrame = 0
let blinkTimer: number | null = null
let blinkPhase = 0
let mouthPhase = 0
let isBlinking = false
let lastInteractionTime = Date.now()
let idleFrameCount = 0

function drawStaticLayer(ctx: CanvasRenderingContext2D, cx: number, faceY: number, faceWidth: number, faceHeight: number, scale: number, breathingOffset: number) {
  drawBody(ctx, cx, faceY, faceWidth, faceHeight, scale, breathingOffset)
  drawFace(ctx, cx, faceY, faceWidth, faceHeight, scale)
  drawHair(ctx, cx, faceY, faceWidth, faceHeight, scale)
  drawEarbuds(ctx, cx, faceY, faceWidth, faceHeight, scale)
}

function easeInOutSine(t: number): number {
  return -(Math.cos(Math.PI * t) - 1) / 2
}

function easeInOutQuad(t: number): number {
  return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2
}

function draw() {
  const c = canvasRef.value
  if (!c) return
  const ctx = c.getContext("2d")
  if (!ctx) return
  const w = c.width
  const h = c.height
  const cx = w / 2
  const cy = h / 2
  const scale = w / 400

  ctx.clearRect(0, 0, w, h)

  const now = Date.now()
  const breathCycle = (now / 3500) % 1
  const breathEase = easeInOutSine(breathCycle)
  const breathingScale = 0.98 + breathEase * 0.04
  const breathingOffset = Math.sin(breathCycle * Math.PI * 2) * 1.5 * scale

  const idleHeadX = Math.sin(now / 5500) * 1.2 * scale + Math.sin(now / 8000) * 0.6 * scale
  const idleHeadY = Math.sin(now / 6500) * 0.6 * scale + Math.sin(now / 9000) * 0.3 * scale
  const eyeYOffset = Math.sin(now / 4500) * 0.4 * scale

  let headOffsetX = idleHeadX
  let headOffsetY = idleHeadY + breathingOffset

  if (props.isListening) {
    headOffsetX = idleHeadX + 6 * scale
    headOffsetY = idleHeadY - 5 * scale + breathingOffset
  }

  const faceY = cy - h * 0.05
  const faceWidth = w * 0.65
  const faceHeight = w * 0.8

  ctx.save()
  ctx.translate(cx + headOffsetX, cy + headOffsetY)
  ctx.scale(breathingScale, breathingScale)

  drawBody(ctx, 0, faceY - cy, faceWidth, faceHeight, scale, breathingOffset)
  drawFace(ctx, 0, faceY - cy, faceWidth, faceHeight, scale)
  drawHair(ctx, 0, faceY - cy, faceWidth, faceHeight, scale)
  drawEarbuds(ctx, 0, faceY - cy, faceWidth, faceHeight, scale)

  drawEyes(ctx, 0, faceY - cy, faceWidth, faceHeight, scale, eyeYOffset)
  drawGlasses(ctx, 0, faceY - cy, faceWidth, faceHeight, scale, eyeYOffset)
  drawMouth(ctx, 0, faceY - cy, faceWidth, faceHeight, scale)

  ctx.restore()

  const shadowY = cy + h * 0.3 + breathingOffset
  const shadowScale = 0.95 + breathEase * 0.1
  const shadowGrad = ctx.createRadialGradient(cx, shadowY, 0, cx, shadowY, faceWidth * 0.5 * shadowScale)
  shadowGrad.addColorStop(0, 'rgba(0, 0, 0, 0.06)')
  shadowGrad.addColorStop(0.5, 'rgba(0, 0, 0, 0.03)')
  shadowGrad.addColorStop(1, 'rgba(0, 0, 0, 0)')
  ctx.fillStyle = shadowGrad
  ctx.beginPath()
  ctx.ellipse(cx, shadowY, faceWidth * 0.45 * shadowScale, faceHeight * 0.06 * shadowScale, 0, 0, Math.PI * 2)
  ctx.fill()
}

function drawBody(ctx: CanvasRenderingContext2D, cx: number, faceY: number, faceWidth: number, faceHeight: number, scale: number, breathingOffset: number) {
  const jacketY = faceY + faceHeight * 0.42 + breathingOffset

  const jacketGrad = ctx.createLinearGradient(cx - faceWidth * 0.7, jacketY - faceHeight * 0.1, cx + faceWidth * 0.7, jacketY + faceHeight * 0.3)
  jacketGrad.addColorStop(0, '#9ca3af')
  jacketGrad.addColorStop(0.3, '#d1d5db')
  jacketGrad.addColorStop(0.5, '#bfc9c3')
  jacketGrad.addColorStop(0.7, '#d1d5db')
  jacketGrad.addColorStop(1, '#9ca3af')

  ctx.fillStyle = jacketGrad
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

  const jacketShadowGrad = ctx.createLinearGradient(cx, jacketY + faceHeight * 0.5, cx, jacketY + faceHeight * 0.85)
  jacketShadowGrad.addColorStop(0, 'rgba(0, 0, 0, 0)')
  jacketShadowGrad.addColorStop(1, 'rgba(0, 0, 0, 0.06)')
  ctx.fillStyle = jacketShadowGrad
  ctx.beginPath()
  ctx.moveTo(cx - faceWidth * 0.35, jacketY + faceHeight * 0.5)
  ctx.lineTo(cx, jacketY + faceHeight * 0.85)
  ctx.lineTo(cx + faceWidth * 0.35, jacketY + faceHeight * 0.5)
  ctx.closePath()
  ctx.fill()

  const lapelGrad = ctx.createLinearGradient(cx - faceWidth * 0.15, jacketY, cx - faceWidth * 0.05, jacketY + faceHeight * 0.2)
  lapelGrad.addColorStop(0, '#8a9099')
  lapelGrad.addColorStop(1, '#a5adb5')
  ctx.fillStyle = lapelGrad
  ctx.beginPath()
  ctx.moveTo(cx - faceWidth * 0.15, jacketY)
  ctx.lineTo(cx - faceWidth * 0.12, jacketY + faceHeight * 0.25)
  ctx.lineTo(cx - faceWidth * 0.05, jacketY + faceHeight * 0.2)
  ctx.closePath()
  ctx.fill()

  const shirtGrad = ctx.createLinearGradient(cx - faceWidth * 0.15, faceY + faceHeight * 0.42, cx, jacketY + faceHeight * 0.12)
  shirtGrad.addColorStop(0, '#fafafa')
  shirtGrad.addColorStop(0.5, '#ffffff')
  shirtGrad.addColorStop(1, '#f5f5f5')
  ctx.fillStyle = shirtGrad
  ctx.beginPath()
  ctx.moveTo(cx - faceWidth * 0.12, faceY + faceHeight * 0.42)
  ctx.lineTo(cx, jacketY + faceHeight * 0.12)
  ctx.lineTo(cx + faceWidth * 0.12, faceY + faceHeight * 0.42)
  ctx.closePath()
  ctx.fill()

  const shirtShadowGrad = ctx.createLinearGradient(cx - faceWidth * 0.08, faceY + faceHeight * 0.42, cx, jacketY + faceHeight * 0.12)
  shirtShadowGrad.addColorStop(0, 'rgba(0, 0, 0, 0.03)')
  shirtShadowGrad.addColorStop(1, 'rgba(0, 0, 0, 0)')
  ctx.fillStyle = shirtShadowGrad
  ctx.beginPath()
  ctx.moveTo(cx - faceWidth * 0.12, faceY + faceHeight * 0.42)
  ctx.lineTo(cx - faceWidth * 0.06, jacketY + faceHeight * 0.18)
  ctx.lineTo(cx, jacketY + faceHeight * 0.12)
  ctx.closePath()
  ctx.fill()

  ctx.fillStyle = '#a5adb5'
  ctx.beginPath()
  ctx.ellipse(cx - faceWidth * 0.25, jacketY + faceHeight * 0.35, faceWidth * 0.12, faceHeight * 0.08, -0.1, 0, Math.PI * 2)
  ctx.fill()

  const pocketShadowGrad = ctx.createLinearGradient(cx - faceWidth * 0.25, jacketY + faceHeight * 0.35, cx - faceWidth * 0.25, jacketY + faceHeight * 0.42)
  pocketShadowGrad.addColorStop(0, 'rgba(0, 0, 0, 0)')
  pocketShadowGrad.addColorStop(1, 'rgba(0, 0, 0, 0.06)')
  ctx.fillStyle = pocketShadowGrad
  ctx.beginPath()
  ctx.ellipse(cx - faceWidth * 0.25, jacketY + faceHeight * 0.38, faceWidth * 0.1, faceHeight * 0.05, -0.1, 0, Math.PI * 2)
  ctx.fill()
}

function drawFace(ctx: CanvasRenderingContext2D, cx: number, faceY: number, faceWidth: number, faceHeight: number, scale: number) {
  const faceGrad = ctx.createRadialGradient(
    cx - faceWidth * 0.15, faceY - faceHeight * 0.15, 10 * scale,
    cx, faceY, faceWidth * 0.6
  )
  faceGrad.addColorStop(0, '#fdf0e6')
  faceGrad.addColorStop(0.5, '#f5e6d3')
  faceGrad.addColorStop(1, '#e8d5c4')

  ctx.fillStyle = faceGrad
  ctx.beginPath()
  ctx.ellipse(cx, faceY, faceWidth * 0.5, faceHeight * 0.5, 0, 0, Math.PI * 2)
  ctx.fill()

  const leftLightGrad = ctx.createLinearGradient(cx - faceWidth * 0.5, faceY, cx, faceY)
  leftLightGrad.addColorStop(0, 'rgba(255, 220, 150, 0.15)')
  leftLightGrad.addColorStop(1, 'rgba(255, 220, 150, 0)')
  ctx.fillStyle = leftLightGrad
  ctx.beginPath()
  ctx.ellipse(cx, faceY, faceWidth * 0.5, faceHeight * 0.5, 0, 0, Math.PI * 2)
  ctx.fill()

  const rightLightGrad = ctx.createLinearGradient(cx, faceY, cx + faceWidth * 0.5, faceY)
  rightLightGrad.addColorStop(0, 'rgba(150, 200, 255, 0)')
  rightLightGrad.addColorStop(1, 'rgba(150, 200, 255, 0.12)')
  ctx.fillStyle = rightLightGrad
  ctx.beginPath()
  ctx.ellipse(cx, faceY, faceWidth * 0.5, faceHeight * 0.5, 0, 0, Math.PI * 2)
  ctx.fill()

  ctx.strokeStyle = '#4a3a2a'
  ctx.lineWidth = 2.5 * scale
  ctx.lineCap = 'round'

  const browY = faceY - faceHeight * 0.12
  const browSpacing = faceWidth * 0.22

  ctx.beginPath()
  ctx.moveTo(cx - browSpacing - faceWidth * 0.08, browY)
  ctx.quadraticCurveTo(cx - browSpacing, browY - faceHeight * 0.05, cx - browSpacing + faceWidth * 0.08, browY)
  ctx.stroke()

  ctx.beginPath()
  ctx.moveTo(cx + browSpacing - faceWidth * 0.08, browY)
  ctx.quadraticCurveTo(cx + browSpacing, browY - faceHeight * 0.05, cx + browSpacing + faceWidth * 0.08, browY)
  ctx.stroke()

  const noseY = faceY + faceHeight * 0.08
  ctx.strokeStyle = '#d4b8a0'
  ctx.lineWidth = 1.8 * scale

  ctx.beginPath()
  ctx.moveTo(cx, noseY)
  ctx.lineTo(cx - faceWidth * 0.03, noseY + faceHeight * 0.1)
  ctx.quadraticCurveTo(cx, noseY + faceHeight * 0.13, cx + faceWidth * 0.03, noseY + faceHeight * 0.1)
  ctx.stroke()

  const blushGradLeft = ctx.createRadialGradient(cx - faceWidth * 0.3, faceY + faceHeight * 0.15, 0, cx - faceWidth * 0.3, faceY + faceHeight * 0.15, faceWidth * 0.15)
  blushGradLeft.addColorStop(0, 'rgba(255, 190, 200, 0.12)')
  blushGradLeft.addColorStop(0.5, 'rgba(255, 170, 185, 0.08)')
  blushGradLeft.addColorStop(1, 'rgba(255, 150, 170, 0)')
  ctx.fillStyle = blushGradLeft
  ctx.beginPath()
  ctx.ellipse(cx - faceWidth * 0.3, faceY + faceHeight * 0.15, faceWidth * 0.15, faceHeight * 0.1, -0.05, 0, Math.PI * 2)
  ctx.fill()

  const blushGradRight = ctx.createRadialGradient(cx + faceWidth * 0.3, faceY + faceHeight * 0.15, 0, cx + faceWidth * 0.3, faceY + faceHeight * 0.15, faceWidth * 0.15)
  blushGradRight.addColorStop(0, 'rgba(255, 190, 200, 0.12)')
  blushGradRight.addColorStop(0.5, 'rgba(255, 170, 185, 0.08)')
  blushGradRight.addColorStop(1, 'rgba(255, 150, 170, 0)')
  ctx.fillStyle = blushGradRight
  ctx.beginPath()
  ctx.ellipse(cx + faceWidth * 0.3, faceY + faceHeight * 0.15, faceWidth * 0.15, faceHeight * 0.1, 0.05, 0, Math.PI * 2)
  ctx.fill()

  const chinShadowGrad = ctx.createLinearGradient(cx, faceY + faceHeight * 0.25, cx, faceY + faceHeight * 0.45)
  chinShadowGrad.addColorStop(0, 'rgba(0, 0, 0, 0)')
  chinShadowGrad.addColorStop(1, 'rgba(0, 0, 0, 0.08)')
  ctx.fillStyle = chinShadowGrad
  ctx.beginPath()
  ctx.ellipse(cx, faceY + faceHeight * 0.35, faceWidth * 0.3, faceHeight * 0.15, 0, 0, Math.PI * 2)
  ctx.fill()
}

function drawHair(ctx: CanvasRenderingContext2D, cx: number, faceY: number, faceWidth: number, faceHeight: number, scale: number) {
  const hairBaseGrad = ctx.createLinearGradient(cx - faceWidth * 0.4, faceY - faceHeight * 0.55, cx + faceWidth * 0.4, faceY - faceHeight * 0.1)
  hairBaseGrad.addColorStop(0, '#3d3d3d')
  hairBaseGrad.addColorStop(0.2, '#4a4a4a')
  hairBaseGrad.addColorStop(0.4, '#555555')
  hairBaseGrad.addColorStop(0.6, '#4a4a4a')
  hairBaseGrad.addColorStop(0.8, '#404040')
  hairBaseGrad.addColorStop(1, '#353535')

  ctx.fillStyle = hairBaseGrad
  ctx.beginPath()
  ctx.moveTo(cx - faceWidth * 0.42, faceY - faceHeight * 0.32)
  ctx.quadraticCurveTo(cx - faceWidth * 0.38, faceY - faceHeight * 0.52, cx - faceWidth * 0.05, faceY - faceHeight * 0.55)
  ctx.quadraticCurveTo(cx + faceWidth * 0.25, faceY - faceHeight * 0.55, cx + faceWidth * 0.48, faceY - faceHeight * 0.35)
  ctx.quadraticCurveTo(cx + faceWidth * 0.52, faceY - faceHeight * 0.22, cx + faceWidth * 0.48, faceY - faceHeight * 0.12)
  ctx.lineTo(cx - faceWidth * 0.42, faceY - faceHeight * 0.12)
  ctx.closePath()
  ctx.fill()

  const hairMiddleGrad = ctx.createLinearGradient(cx - faceWidth * 0.3, faceY - faceHeight * 0.52, cx + faceWidth * 0.3, faceY - faceHeight * 0.18)
  hairMiddleGrad.addColorStop(0, '#555555')
  hairMiddleGrad.addColorStop(0.3, '#666666')
  hairMiddleGrad.addColorStop(0.5, '#707070')
  hairMiddleGrad.addColorStop(0.7, '#606060')
  hairMiddleGrad.addColorStop(1, '#505050')

  ctx.fillStyle = hairMiddleGrad
  ctx.beginPath()
  ctx.moveTo(cx - faceWidth * 0.32, faceY - faceHeight * 0.28)
  ctx.quadraticCurveTo(cx - faceWidth * 0.12, faceY - faceHeight * 0.5, cx + faceWidth * 0.15, faceY - faceHeight * 0.52)
  ctx.quadraticCurveTo(cx + faceWidth * 0.38, faceY - faceHeight * 0.48, cx + faceWidth * 0.44, faceY - faceHeight * 0.28)
  ctx.lineTo(cx + faceWidth * 0.4, faceY - faceHeight * 0.18)
  ctx.lineTo(cx - faceWidth * 0.32, faceY - faceHeight * 0.18)
  ctx.closePath()
  ctx.fill()

  const hairHighlightGrad = ctx.createLinearGradient(cx - faceWidth * 0.2, faceY - faceHeight * 0.48, cx + faceWidth * 0.25, faceY - faceHeight * 0.22)
  hairHighlightGrad.addColorStop(0, '#666666')
  hairHighlightGrad.addColorStop(0.4, '#7a7a7a')
  hairHighlightGrad.addColorStop(0.6, '#858585')
  hairHighlightGrad.addColorStop(0.8, '#707070')
  hairHighlightGrad.addColorStop(1, '#606060')

  ctx.fillStyle = hairHighlightGrad
  ctx.beginPath()
  ctx.moveTo(cx - faceWidth * 0.22, faceY - faceHeight * 0.25)
  ctx.quadraticCurveTo(cx - faceWidth * 0.05, faceY - faceHeight * 0.45, cx + faceWidth * 0.18, faceY - faceHeight * 0.48)
  ctx.quadraticCurveTo(cx + faceWidth * 0.35, faceY - faceHeight * 0.44, cx + faceWidth * 0.4, faceY - faceHeight * 0.25)
  ctx.lineTo(cx + faceWidth * 0.36, faceY - faceHeight * 0.2)
  ctx.lineTo(cx - faceWidth * 0.22, faceY - faceHeight * 0.2)
  ctx.closePath()
  ctx.fill()

  const sidePartGrad = ctx.createLinearGradient(cx - faceWidth * 0.05, faceY - faceHeight * 0.52, cx - faceWidth * 0.05, faceY - faceHeight * 0.2)
  sidePartGrad.addColorStop(0, '#4a4a4a')
  sidePartGrad.addColorStop(1, '#5a5a5a')
  ctx.fillStyle = sidePartGrad
  ctx.beginPath()
  ctx.moveTo(cx - faceWidth * 0.08, faceY - faceHeight * 0.52)
  ctx.lineTo(cx - faceWidth * 0.05, faceY - faceHeight * 0.22)
  ctx.lineTo(cx, faceY - faceHeight * 0.25)
  ctx.lineTo(cx + faceWidth * 0.05, faceY - faceHeight * 0.48)
  ctx.closePath()
  ctx.fill()

  ctx.fillStyle = '#333333'
  ctx.beginPath()
  ctx.moveTo(cx - faceWidth * 0.35, faceY - faceHeight * 0.5)
  ctx.lineTo(cx - faceWidth * 0.3, faceY - faceHeight * 0.22)
  ctx.lineTo(cx - faceWidth * 0.22, faceY - faceHeight * 0.25)
  ctx.lineTo(cx - faceWidth * 0.25, faceY - faceHeight * 0.5)
  ctx.closePath()
  ctx.fill()

  const sideHairGrad = ctx.createLinearGradient(cx - faceWidth * 0.42, faceY - faceHeight * 0.15, cx - faceWidth * 0.35, faceY - faceHeight * 0.35)
  sideHairGrad.addColorStop(0, '#3a3a3a')
  sideHairGrad.addColorStop(1, '#4a4a4a')
  ctx.fillStyle = sideHairGrad
  ctx.beginPath()
  ctx.moveTo(cx - faceWidth * 0.45, faceY - faceHeight * 0.12)
  ctx.lineTo(cx - faceWidth * 0.42, faceY - faceHeight * 0.32)
  ctx.lineTo(cx - faceWidth * 0.35, faceY - faceHeight * 0.38)
  ctx.lineTo(cx - faceWidth * 0.38, faceY - faceHeight * 0.15)
  ctx.closePath()
  ctx.fill()

  const sideHairGradRight = ctx.createLinearGradient(cx + faceWidth * 0.42, faceY - faceHeight * 0.15, cx + faceWidth * 0.35, faceY - faceHeight * 0.35)
  sideHairGradRight.addColorStop(0, '#3a3a3a')
  sideHairGradRight.addColorStop(1, '#4a4a4a')
  ctx.fillStyle = sideHairGradRight
  ctx.beginPath()
  ctx.moveTo(cx + faceWidth * 0.45, faceY - faceHeight * 0.12)
  ctx.lineTo(cx + faceWidth * 0.42, faceY - faceHeight * 0.32)
  ctx.lineTo(cx + faceWidth * 0.35, faceY - faceHeight * 0.38)
  ctx.lineTo(cx + faceWidth * 0.38, faceY - faceHeight * 0.15)
  ctx.closePath()
  ctx.fill()
}

function drawEarbuds(ctx: CanvasRenderingContext2D, cx: number, faceY: number, faceWidth: number, faceHeight: number, scale: number) {
  const earXLeft = cx - faceWidth * 0.45
  const earXRight = cx + faceWidth * 0.45
  const earY = faceY + faceHeight * 0.1

  ctx.fillStyle = '#2c2c2c'
  ctx.beginPath()
  ctx.ellipse(earXLeft, earY, faceWidth * 0.08, faceWidth * 0.12, -0.15, 0, Math.PI * 2)
  ctx.fill()
  ctx.beginPath()
  ctx.ellipse(earXRight, earY, faceWidth * 0.08, faceWidth * 0.12, 0.15, 0, Math.PI * 2)
  ctx.fill()

  ctx.fillStyle = '#3a3a3a'
  ctx.beginPath()
  ctx.ellipse(earXLeft, earY, faceWidth * 0.05, faceWidth * 0.08, -0.15, 0, Math.PI * 2)
  ctx.fill()
  ctx.beginPath()
  ctx.ellipse(earXRight, earY, faceWidth * 0.05, faceWidth * 0.08, 0.15, 0, Math.PI * 2)
  ctx.fill()

  ctx.fillStyle = '#1a1a1a'
  ctx.beginPath()
  ctx.ellipse(earXLeft, earY, faceWidth * 0.03, faceWidth * 0.05, -0.15, 0, Math.PI * 2)
  ctx.fill()
  ctx.beginPath()
  ctx.ellipse(earXRight, earY, faceWidth * 0.03, faceWidth * 0.05, 0.15, 0, Math.PI * 2)
  ctx.fill()

  ctx.fillStyle = '#10ac84'
  ctx.beginPath()
  ctx.arc(earXLeft + faceWidth * 0.02, earY - faceWidth * 0.03, faceWidth * 0.015, 0, Math.PI * 2)
  ctx.fill()
  ctx.beginPath()
  ctx.arc(earXRight + faceWidth * 0.02, earY - faceWidth * 0.03, faceWidth * 0.015, 0, Math.PI * 2)
  ctx.fill()

  ctx.strokeStyle = '#5a5a5a'
  ctx.lineWidth = 0.5 * scale
  ctx.beginPath()
  ctx.moveTo(earXLeft - faceWidth * 0.05, earY - faceWidth * 0.08)
  ctx.quadraticCurveTo(earXLeft - faceWidth * 0.1, earY - faceHeight * 0.25, cx - faceWidth * 0.2, faceY - faceHeight * 0.45)
  ctx.stroke()
  ctx.beginPath()
  ctx.moveTo(earXRight + faceWidth * 0.05, earY - faceWidth * 0.08)
  ctx.quadraticCurveTo(earXRight + faceWidth * 0.1, earY - faceHeight * 0.25, cx + faceWidth * 0.2, faceY - faceHeight * 0.45)
  ctx.stroke()
}

function drawEyes(ctx: CanvasRenderingContext2D, cx: number, faceY: number, faceWidth: number, faceHeight: number, scale: number, eyeYOffset: number) {
  const eyeY = faceY - faceHeight * 0.02 + eyeYOffset
  const eyeSpacing = faceWidth * 0.22
  const eyeWidth = faceWidth * 0.12
  const eyeHeight = faceWidth * 0.06

  let blinkHeight = 1
  let cheekPuff = 0
  if (isBlinking) {
    const blinkProgress = blinkPhase / 30
    if (blinkProgress < 0.25) {
      const t = blinkProgress / 0.25
      const eased = easeInOutQuad(t)
      blinkHeight = 1 - eased * 0.98
      cheekPuff = eased * 0.3
    } else if (blinkProgress < 0.4) {
      blinkHeight = 0.02
      cheekPuff = 0.35
    } else {
      const t = (blinkProgress - 0.4) / 0.6
      const eased = easeInOutQuad(t)
      blinkHeight = 0.02 + eased * 0.98
      cheekPuff = 0.35 - eased * 0.35
    }
  }

  const eyeTopY = eyeY - eyeHeight * blinkHeight * 0.5
  const currentEyeHeight = eyeHeight * blinkHeight

  if (cheekPuff > 0) {
    const cheekY = faceY + faceHeight * 0.12
    const cheekScale = 1 + cheekPuff * 0.02

    ctx.save()
    ctx.translate(cx - eyeSpacing * 0.8, cheekY)
    ctx.scale(cheekScale, 1 - cheekPuff * 0.01)
    const leftCheekGrad = ctx.createRadialGradient(0, 0, 0, 0, 0, faceWidth * 0.12)
    leftCheekGrad.addColorStop(0, 'rgba(255, 190, 200, 0.08)')
    leftCheekGrad.addColorStop(1, 'rgba(255, 170, 185, 0)')
    ctx.fillStyle = leftCheekGrad
    ctx.beginPath()
    ctx.ellipse(0, 0, faceWidth * 0.12, faceHeight * 0.08, -0.05, 0, Math.PI * 2)
    ctx.fill()
    ctx.restore()

    ctx.save()
    ctx.translate(cx + eyeSpacing * 0.8, cheekY)
    ctx.scale(cheekScale, 1 - cheekPuff * 0.01)
    const rightCheekGrad = ctx.createRadialGradient(0, 0, 0, 0, 0, faceWidth * 0.12)
    rightCheekGrad.addColorStop(0, 'rgba(255, 190, 200, 0.08)')
    rightCheekGrad.addColorStop(1, 'rgba(255, 170, 185, 0)')
    ctx.fillStyle = rightCheekGrad
    ctx.beginPath()
    ctx.ellipse(0, 0, faceWidth * 0.12, faceHeight * 0.08, 0.05, 0, Math.PI * 2)
    ctx.fill()
    ctx.restore()
  }

  const eyeSocketGrad = ctx.createLinearGradient(cx - eyeSpacing - eyeWidth * 0.5, eyeTopY - faceHeight * 0.03, cx - eyeSpacing, eyeTopY)
  eyeSocketGrad.addColorStop(0, 'rgba(0, 0, 0, 0.08)')
  eyeSocketGrad.addColorStop(1, 'rgba(0, 0, 0, 0)')
  ctx.fillStyle = eyeSocketGrad
  ctx.beginPath()
  ctx.ellipse(cx - eyeSpacing, eyeTopY - faceHeight * 0.02, eyeWidth * 0.8, faceHeight * 0.02, 0.03, 0, Math.PI * 2)
  ctx.fill()

  eyeSocketGrad.addColorStop(0, 'rgba(0, 0, 0, 0)')
  eyeSocketGrad.addColorStop(1, 'rgba(0, 0, 0, 0.08)')
  ctx.fillStyle = eyeSocketGrad
  ctx.beginPath()
  ctx.ellipse(cx + eyeSpacing, eyeTopY - faceHeight * 0.02, eyeWidth * 0.8, faceHeight * 0.02, -0.03, 0, Math.PI * 2)
  ctx.fill()

  ctx.fillStyle = '#f5f5f5'
  ctx.beginPath()
  ctx.ellipse(cx - eyeSpacing, eyeY, eyeWidth * 0.5, currentEyeHeight * 0.5, 0.03, 0, Math.PI * 2)
  ctx.fill()
  ctx.beginPath()
  ctx.ellipse(cx + eyeSpacing, eyeY, eyeWidth * 0.5, currentEyeHeight * 0.5, -0.03, 0, Math.PI * 2)
  ctx.fill()

  if (blinkHeight > 0.1) {
    const irisXOffset = props.isListening ? 2 * scale : 1.5 * scale
    const irisYOffset = props.isListening ? -1 * scale : 0

    const irisGradLeft = ctx.createRadialGradient(
      cx - eyeSpacing + irisXOffset - eyeWidth * 0.1, eyeY + irisYOffset - eyeHeight * 0.1, 0,
      cx - eyeSpacing + irisXOffset, eyeY + irisYOffset, eyeWidth * 0.35
    )
    irisGradLeft.addColorStop(0, '#6a8fc5')
    irisGradLeft.addColorStop(0.5, '#4a6fa5')
    irisGradLeft.addColorStop(1, '#3a5a85')
    ctx.fillStyle = irisGradLeft
    ctx.beginPath()
    ctx.ellipse(cx - eyeSpacing + irisXOffset, eyeY + irisYOffset, eyeWidth * 0.35, currentEyeHeight * 0.45, 0, 0, Math.PI * 2)
    ctx.fill()

    const irisGradRight = ctx.createRadialGradient(
      cx + eyeSpacing + irisXOffset - eyeWidth * 0.1, eyeY + irisYOffset - eyeHeight * 0.1, 0,
      cx + eyeSpacing + irisXOffset, eyeY + irisYOffset, eyeWidth * 0.35
    )
    irisGradRight.addColorStop(0, '#6a8fc5')
    irisGradRight.addColorStop(0.5, '#4a6fa5')
    irisGradRight.addColorStop(1, '#3a5a85')
    ctx.fillStyle = irisGradRight
    ctx.beginPath()
    ctx.ellipse(cx + eyeSpacing + irisXOffset, eyeY + irisYOffset, eyeWidth * 0.35, currentEyeHeight * 0.45, 0, 0, Math.PI * 2)
    ctx.fill()

    ctx.fillStyle = '#2c3e50'
    ctx.beginPath()
    ctx.arc(cx - eyeSpacing + irisXOffset + 1 * scale, eyeY + irisYOffset + 0.5 * scale, eyeWidth * 0.18, 0, Math.PI * 2)
    ctx.fill()
    ctx.beginPath()
    ctx.arc(cx + eyeSpacing + irisXOffset + 1 * scale, eyeY + irisYOffset + 0.5 * scale, eyeWidth * 0.18, 0, Math.PI * 2)
    ctx.fill()

    ctx.fillStyle = '#ffffff'
    ctx.beginPath()
    ctx.arc(cx - eyeSpacing + irisXOffset - 1 * scale, eyeY + irisYOffset - 1.5 * scale, eyeWidth * 0.08, 0, Math.PI * 2)
    ctx.fill()
    ctx.beginPath()
    ctx.arc(cx + eyeSpacing + irisXOffset - 1 * scale, eyeY + irisYOffset - 1.5 * scale, eyeWidth * 0.08, 0, Math.PI * 2)
    ctx.fill()

    ctx.fillStyle = 'rgba(255, 255, 255, 0.4)'
    ctx.beginPath()
    ctx.arc(cx - eyeSpacing - eyeWidth * 0.2, eyeY - currentEyeHeight * 0.2, eyeWidth * 0.05, 0, Math.PI * 2)
    ctx.fill()
    ctx.beginPath()
    ctx.arc(cx + eyeSpacing - eyeWidth * 0.2, eyeY - currentEyeHeight * 0.2, eyeWidth * 0.05, 0, Math.PI * 2)
    ctx.fill()
  } else {
    ctx.fillStyle = '#d4c4b4'
    ctx.beginPath()
    ctx.ellipse(cx - eyeSpacing, eyeY, eyeWidth * 0.45, faceHeight * 0.015, 0.03, 0, Math.PI * 2)
    ctx.fill()
    ctx.beginPath()
    ctx.ellipse(cx + eyeSpacing, eyeY, eyeWidth * 0.45, faceHeight * 0.015, -0.03, 0, Math.PI * 2)
    ctx.fill()
  }
}

function drawGlasses(ctx: CanvasRenderingContext2D, cx: number, faceY: number, faceWidth: number, faceHeight: number, scale: number, eyeYOffset: number) {
  const eyeY = faceY - faceHeight * 0.02 + eyeYOffset
  const eyeSpacing = faceWidth * 0.22
  const eyeWidth = faceWidth * 0.12
  const eyeHeight = faceWidth * 0.06
  const glassW = eyeWidth * 0.8
  const glassH = eyeHeight * 1.1

  const frameGrad = ctx.createLinearGradient(cx - eyeSpacing - glassW, eyeY - glassH, cx - eyeSpacing + glassW, eyeY + glassH)
  frameGrad.addColorStop(0, '#8b95a5')
  frameGrad.addColorStop(0.5, '#a5adb8')
  frameGrad.addColorStop(1, '#6b7585')

  ctx.strokeStyle = frameGrad
  ctx.lineWidth = 1.2 * scale

  ctx.beginPath()
  ctx.ellipse(cx - eyeSpacing, eyeY, glassW * 0.5, glassH * 0.5, 0.02, 0, Math.PI * 2)
  ctx.stroke()
  ctx.beginPath()
  ctx.ellipse(cx + eyeSpacing, eyeY, glassW * 0.5, glassH * 0.5, -0.02, 0, Math.PI * 2)
  ctx.stroke()

  ctx.beginPath()
  ctx.moveTo(cx - eyeSpacing + glassW * 0.4, eyeY)
  ctx.lineTo(cx + eyeSpacing - glassW * 0.4, eyeY)
  ctx.stroke()

  ctx.beginPath()
  ctx.moveTo(cx - eyeSpacing - glassW * 0.5, eyeY)
  ctx.lineTo(cx - eyeSpacing - glassW * 0.8, eyeY - faceHeight * 0.04)
  ctx.stroke()
  ctx.beginPath()
  ctx.moveTo(cx + eyeSpacing + glassW * 0.5, eyeY)
  ctx.lineTo(cx + eyeSpacing + glassW * 0.8, eyeY - faceHeight * 0.04)
  ctx.stroke()

  const lensGradLeft = ctx.createLinearGradient(cx - eyeSpacing - glassW * 0.4, eyeY - glassH * 0.4, cx - eyeSpacing + glassW * 0.2, eyeY + glassH * 0.4)
  lensGradLeft.addColorStop(0, 'rgba(200, 220, 255, 0.15)')
  lensGradLeft.addColorStop(0.5, 'rgba(180, 200, 240, 0.08)')
  lensGradLeft.addColorStop(1, 'rgba(160, 180, 220, 0.05)')
  ctx.fillStyle = lensGradLeft
  ctx.beginPath()
  ctx.ellipse(cx - eyeSpacing, eyeY, glassW * 0.48, glassH * 0.48, 0.02, 0, Math.PI * 2)
  ctx.fill()

  const lensGradRight = ctx.createLinearGradient(cx + eyeSpacing - glassW * 0.4, eyeY - glassH * 0.4, cx + eyeSpacing + glassW * 0.2, eyeY + glassH * 0.4)
  lensGradRight.addColorStop(0, 'rgba(200, 220, 255, 0.15)')
  lensGradRight.addColorStop(0.5, 'rgba(180, 200, 240, 0.08)')
  lensGradRight.addColorStop(1, 'rgba(160, 180, 220, 0.05)')
  ctx.fillStyle = lensGradRight
  ctx.beginPath()
  ctx.ellipse(cx + eyeSpacing, eyeY, glassW * 0.48, glassH * 0.48, -0.02, 0, Math.PI * 2)
  ctx.fill()

  ctx.fillStyle = 'rgba(255, 255, 255, 0.3)'
  ctx.beginPath()
  ctx.ellipse(cx - eyeSpacing - glassW * 0.25, eyeY - glassH * 0.25, glassW * 0.15, glassH * 0.1, -0.3, 0, Math.PI * 2)
  ctx.fill()
  ctx.beginPath()
  ctx.ellipse(cx + eyeSpacing - glassW * 0.25, eyeY - glassH * 0.25, glassW * 0.15, glassH * 0.1, -0.3, 0, Math.PI * 2)
  ctx.fill()
}

function drawMouth(ctx: CanvasRenderingContext2D, cx: number, faceY: number, faceWidth: number, faceHeight: number, scale: number) {
  const mouthY = faceY + faceHeight * 0.25
  const mouthW = faceWidth * 0.18
  const mouthH = faceHeight * 0.06

  if (props.isTalking) {
    mouthPhase += 0.3
    const basePhase = Math.sin(mouthPhase)
    const secondaryPhase = Math.sin(mouthPhase * 1.8)
    const tertiaryPhase = Math.sin(mouthPhase * 2.5)
    
    let mouthLevel = 2
    const timeFactor = Math.sin(Date.now() / 1000) * 0.5 + 0.5
    if (timeFactor > 0.8) {
      mouthLevel = 3
    } else if (timeFactor < 0.2) {
      mouthLevel = 1
    }

    let openAmount = 0.12
    if (mouthLevel === 1) {
      openAmount = 0.08 + Math.abs(basePhase) * 0.06 + Math.abs(secondaryPhase) * 0.03
    } else if (mouthLevel === 2) {
      openAmount = 0.18 + Math.abs(basePhase) * 0.1 + Math.abs(secondaryPhase) * 0.04 + Math.abs(tertiaryPhase) * 0.03
    } else {
      openAmount = 0.32 + Math.abs(basePhase) * 0.15 + Math.abs(secondaryPhase) * 0.06 + Math.abs(tertiaryPhase) * 0.05
    }

    const currentMouthH = mouthH * openAmount
    const easedOpen = easeInOutQuad(openAmount / 0.5)

    ctx.fillStyle = '#3d2822'
    ctx.beginPath()
    ctx.ellipse(cx, mouthY + currentMouthH * 0.25, mouthW * 0.42 * (1 + easedOpen * 0.1), currentMouthH * 0.65, 0, 0, Math.PI * 2)
    ctx.fill()

    if (openAmount > 0.22) {
      ctx.fillStyle = '#f5f0e8'
      ctx.beginPath()
      ctx.ellipse(cx, mouthY - currentMouthH * 0.2, mouthW * 0.32, currentMouthH * 0.18, 0, Math.PI, 0)
      ctx.fill()

      ctx.strokeStyle = '#c4b8b0'
      ctx.lineWidth = 0.8 * scale
      ctx.lineCap = 'round'
      ctx.beginPath()
      ctx.moveTo(cx - mouthW * 0.22, mouthY - currentMouthH * 0.2)
      ctx.lineTo(cx - mouthW * 0.13, mouthY - currentMouthH * 0.2)
      ctx.moveTo(cx - mouthW * 0.04, mouthY - currentMouthH * 0.2)
      ctx.lineTo(cx + mouthW * 0.04, mouthY - currentMouthH * 0.2)
      ctx.moveTo(cx + mouthW * 0.13, mouthY - currentMouthH * 0.2)
      ctx.lineTo(cx + mouthW * 0.22, mouthY - currentMouthH * 0.2)
      ctx.stroke()

      if (openAmount > 0.32) {
        ctx.fillStyle = '#e8d8c8'
        ctx.beginPath()
        ctx.ellipse(cx, mouthY + currentMouthH * 0.15, mouthW * 0.22, currentMouthH * 0.12, 0, 0, Math.PI * 2)
        ctx.fill()

        ctx.strokeStyle = '#d4c4b4'
        ctx.lineWidth = 0.6 * scale
        ctx.beginPath()
        ctx.moveTo(cx - mouthW * 0.15, mouthY + currentMouthH * 0.15)
        ctx.lineTo(cx - mouthW * 0.08, mouthY + currentMouthH * 0.15)
        ctx.moveTo(cx - mouthW * 0.02, mouthY + currentMouthH * 0.15)
        ctx.lineTo(cx + mouthW * 0.02, mouthY + currentMouthH * 0.15)
        ctx.moveTo(cx + mouthW * 0.08, mouthY + currentMouthH * 0.15)
        ctx.lineTo(cx + mouthW * 0.15, mouthY + currentMouthH * 0.15)
        ctx.stroke()
      }
    }
  } else {
    const lipTopGrad = ctx.createLinearGradient(cx, mouthY - mouthH * 0.3, cx, mouthY)
    lipTopGrad.addColorStop(0, '#b86f7f')
    lipTopGrad.addColorStop(1, '#9b5a6b')

    ctx.fillStyle = lipTopGrad
    ctx.beginPath()
    ctx.arc(cx, mouthY - mouthH * 0.1, mouthW * 0.4, 0.15, Math.PI, false)
    ctx.fill()

    const lipBottomGrad = ctx.createLinearGradient(cx, mouthY, cx, mouthY + mouthH * 0.3)
    lipBottomGrad.addColorStop(0, '#8b4a5a')
    lipBottomGrad.addColorStop(1, '#a55a6a')

    ctx.fillStyle = lipBottomGrad
    ctx.beginPath()
    ctx.arc(cx, mouthY + mouthH * 0.1, mouthW * 0.4, Math.PI, 0.15, true)
    ctx.fill()

    ctx.strokeStyle = '#7b3a4a'
    ctx.lineWidth = 0.8 * scale
    ctx.beginPath()
    ctx.arc(cx, mouthY, mouthW * 0.38, 0.15, Math.PI - 0.15)
    ctx.stroke()

    const lipShadowGrad = ctx.createLinearGradient(cx, mouthY - mouthH * 0.15, cx, mouthY + mouthH * 0.15)
    lipShadowGrad.addColorStop(0, 'rgba(0, 0, 0, 0.08)')
    lipShadowGrad.addColorStop(0.5, 'rgba(0, 0, 0, 0)')
    lipShadowGrad.addColorStop(1, 'rgba(0, 0, 0, 0.08)')
    ctx.fillStyle = lipShadowGrad
    ctx.beginPath()
    ctx.arc(cx, mouthY, mouthW * 0.35, 0.2, Math.PI - 0.2)
    ctx.fill()
  }
}

function animate() {
  const now = Date.now()
  
  if (props.isTalking || props.isListening || isBlinking) {
    lastInteractionTime = now
    idleFrameCount = 0
  } else {
    idleFrameCount++
  }

  const isHighActivity = props.isTalking || props.isListening || isBlinking
  const frameInterval = isHighActivity ? 1 : 3
  const shouldRender = isHighActivity || idleFrameCount % frameInterval === 0

  if (shouldRender) {
    if (isBlinking) {
      blinkPhase++
      if (blinkPhase >= 30) {
        isBlinking = false
        blinkPhase = 0
        scheduleBlink()
      }
    }
    draw()
  }

  animFrame = requestAnimationFrame(animate)
}

function scheduleBlink() {
  blinkTimer = window.setTimeout(() => {
    isBlinking = true
  }, 3000 + Math.random() * 2000)
}

function triggerBlink() {
  if (!isBlinking) {
    isBlinking = true
  }
}

watch(() => props.isTalking, (newVal) => {
  if (newVal) {
    triggerBlink()
  }
})

onMounted(() => {
  animate()
  scheduleBlink()
})

onUnmounted(() => {
  cancelAnimationFrame(animFrame)
  if (blinkTimer) {
    clearTimeout(blinkTimer)
  }
})
</script>

<style scoped>
.avatar-container {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  position: relative;
  transition: transform 0.3s ease-out;
  border-radius: 8px;
}

canvas {
  display: block;
  border-radius: 8px;
  filter: saturate(0.85) contrast(0.98) brightness(1.02);
}

.avatar-container::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 8px;
  background: radial-gradient(ellipse at 30% 20%, rgba(255, 240, 220, 0.06) 0%, transparent 50%),
              radial-gradient(ellipse at 70% 80%, rgba(180, 200, 220, 0.04) 0%, transparent 50%);
  pointer-events: none;
  z-index: 1;
}
</style>