<template>
  <div class="processing-animation">
    <!-- Progress indicator -->
    <div class="relative w-full h-2 bg-gray-700 rounded-full overflow-hidden mb-8">
      <div
        class="absolute h-full bg-gradient-to-r from-purple-600 to-blue-600 rounded-full"
        :style="`width: ${progress}%`"
      ></div>
    </div>

    <!-- Particle animation canvas -->
    <div class="relative h-48 mb-6">
      <canvas ref="canvas" class="absolute inset-0 w-full h-full"></canvas>

      <!-- Text overlay -->
      <div class="absolute inset-0 flex items-center justify-center">
        <div class="text-center">
          <div class="text-xl font-bold bg-gradient-to-r from-purple-400 to-blue-500 bg-clip-text text-transparent mb-2">
            {{ progress }}%
          </div>
          <div class="text-gray-300">{{ message }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'

// Props
const props = defineProps({
  progress: {
    type: Number,
    default: 0
  },
  message: {
    type: String,
    default: 'Processing your audio...'
  }
})

// Refs
const canvas = ref(null)
let animationId = null
let particles = []

// Animation configuration
const PARTICLE_COUNT = 100
const PARTICLE_COLOR = '#8b5cf6'
const PARTICLE_FADE_RATE = 0.02
const PARTICLE_DECELERATION = 0.92

// Canvas setup
function setupCanvas() {
  const ctx = canvas.value.getContext('2d')
  const rect = canvas.value.getBoundingClientRect()

  // Set canvas size to match display size
  canvas.value.width = rect.width
  canvas.value.height = rect.height

  return ctx
}

// Create a particle
function createParticle(ctx) {
  const centerX = canvas.value.width / 2
  const centerY = canvas.value.height / 2
  const angle = Math.random() * Math.PI * 2
  const velocity = Math.random() * 2 + 1
  const size = Math.random() * 3 + 1
  const opacity = 0.6 + Math.random() * 0.4

  return {
    x: centerX,
    y: centerY,
    vx: Math.cos(angle) * velocity,
    vy: Math.sin(angle) * velocity,
    size,
    opacity,
    color: PARTICLE_COLOR
  }
}

// Animation loop
function animate() {
  if (!canvas.value) return

  const ctx = canvas.value.getContext('2d')

  // Clear canvas with semi-transparent black for trail effect
  ctx.fillStyle = 'rgba(17, 24, 39, 0.2)'
  ctx.fillRect(0, 0, canvas.value.width, canvas.value.height)

  // Add new particles to maintain the count
  while (particles.length < PARTICLE_COUNT) {
    particles.push(createParticle(ctx))
  }

  // Update and draw particles
  particles.forEach((particle, index) => {
    // Move particle
    particle.x += particle.vx
    particle.y += particle.vy

    // Apply deceleration
    particle.vx *= PARTICLE_DECELERATION
    particle.vy *= PARTICLE_DECELERATION

    // Fade out
    particle.opacity -= PARTICLE_FADE_RATE

    // Remove faded particles
    if (particle.opacity <= 0) {
      particles.splice(index, 1)
      return
    }

    // Draw particle
    ctx.beginPath()
    ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2)
    ctx.fillStyle = `${particle.color}${Math.floor(particle.opacity * 255).toString(16).padStart(2, '0')}`
    ctx.fill()
  })

  // Continue animation loop
  animationId = requestAnimationFrame(animate)
}

// Start animation
function startAnimation() {
  if (!canvas.value) return

  // Setup canvas
  setupCanvas()

  // Initialize particles
  particles = []

  // Start animation loop
  animate()
}

// Stop animation
function stopAnimation() {
  if (animationId) {
    cancelAnimationFrame(animationId)
    animationId = null
  }
}

// Handle window resize
function handleResize() {
  if (!canvas.value) return

  setupCanvas()
}

// Lifecycle hooks
onMounted(() => {
  startAnimation()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  stopAnimation()
  window.removeEventListener('resize', handleResize)
})

// Watch for progress changes to adjust animation speed
watch(() => props.progress, (newProgress) => {
  // Could adjust animation parameters based on progress if desired
})
</script>