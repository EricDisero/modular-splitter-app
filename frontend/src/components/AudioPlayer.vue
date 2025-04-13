<template>
  <div class="audio-player bg-gray-800/70 rounded-lg p-2 my-2">
    <audio
      ref="audioElement"
      :src="src"
      preload="metadata"
      @loadedmetadata="onLoadedMetadata"
      @timeupdate="onTimeUpdate"
      @ended="onEnded"
    ></audio>

    <div class="flex items-center mb-2">
      <button
        @click="togglePlay"
        class="w-8 h-8 flex items-center justify-center bg-purple-600 hover:bg-purple-500 rounded-full text-white focus:outline-none transition duration-150"
      >
        <svg v-if="!isPlaying" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd" />
        </svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
        </svg>
      </button>

      <div class="flex-1 mx-3">
        <div class="relative h-2 bg-gray-700 rounded-full">
          <div
            class="absolute left-0 top-0 h-full bg-purple-500 rounded-full"
            :style="`width: ${progress}%`"
          ></div>
          <input
            type="range"
            min="0"
            :max="duration"
            step="0.1"
            v-model="currentTime"
            @input="onSeek"
            class="absolute w-full h-full opacity-0 cursor-pointer"
          >
        </div>
      </div>

      <div class="text-xs text-gray-400 w-16 text-right tabular-nums">
        {{ formatTime(currentTime) }} / {{ formatTime(duration) }}
      </div>
    </div>

    <div class="flex items-center justify-between">
      <div class="flex items-center">
        <button
          @click="toggleMute"
          class="text-gray-400 hover:text-white"
        >
          <svg v-if="!isMuted" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
          </svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2" />
          </svg>
        </button>

        <div class="ml-2 relative h-1 w-16 bg-gray-700 rounded-full">
          <div
            class="absolute left-0 top-0 h-full bg-gray-500 rounded-full"
            :style="`width: ${volume * 100}%`"
          ></div>
          <input
            type="range"
            min="0"
            max="1"
            step="0.01"
            v-model="volume"
            @input="onVolumeChange"
            class="absolute w-full h-full opacity-0 cursor-pointer"
          >
        </div>
      </div>

      <div class="flex items-center space-x-2">
        <button
          @click="setPlaybackRate(0.5)"
          :class="playbackRate === 0.5 ? 'text-purple-400' : 'text-gray-500'"
          class="text-xs hover:text-white"
        >
          0.5x
        </button>
        <button
          @click="setPlaybackRate(1.0)"
          :class="playbackRate === 1.0 ? 'text-purple-400' : 'text-gray-500'"
          class="text-xs hover:text-white"
        >
          1.0x
        </button>
        <button
          @click="setPlaybackRate(1.5)"
          :class="playbackRate === 1.5 ? 'text-purple-400' : 'text-gray-500'"
          class="text-xs hover:text-white"
        >
          1.5x
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed, watch } from 'vue'

// Props
const props = defineProps({
  src: {
    type: String,
    required: true
  },
  stemName: {
    type: String,
    default: ''
  }
})

// Refs
const audioElement = ref(null)
const isPlaying = ref(false)
const isMuted = ref(false)
const volume = ref(0.8)
const duration = ref(0)
const currentTime = ref(0)
const playbackRate = ref(1.0)

// Computed
const progress = computed(() => {
  if (duration.value === 0) return 0
  return (currentTime.value / duration.value) * 100
})

// Event handlers
function onLoadedMetadata() {
  duration.value = audioElement.value.duration
}

function onTimeUpdate() {
  currentTime.value = audioElement.value.currentTime
}

function onEnded() {
  isPlaying.value = false
  currentTime.value = 0
}

function onSeek() {
  if (audioElement.value) {
    audioElement.value.currentTime = currentTime.value
  }
}

function onVolumeChange() {
  if (audioElement.value) {
    audioElement.value.volume = volume.value

    // Update muted state
    if (volume.value === 0) {
      isMuted.value = true
    } else {
      isMuted.value = false
    }
  }
}

// Actions
function togglePlay() {
  if (!audioElement.value) return

  if (isPlaying.value) {
    audioElement.value.pause()
  } else {
    // Pause all other audio players first
    document.querySelectorAll('audio').forEach(audio => {
      if (audio !== audioElement.value) {
        audio.pause()
      }
    })

    audioElement.value.play()
  }

  isPlaying.value = !isPlaying.value
}

function toggleMute() {
  if (!audioElement.value) return

  if (isMuted.value) {
    audioElement.value.volume = volume.value
  } else {
    audioElement.value.volume = 0
  }

  isMuted.value = !isMuted.value
}

function setPlaybackRate(rate) {
  if (!audioElement.value) return

  audioElement.value.playbackRate = rate
  playbackRate.value = rate
}

// Utilities
function formatTime(seconds) {
  if (isNaN(seconds) || seconds === Infinity) return '0:00'

  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)

  return `${mins}:${secs.toString().padStart(2, '0')}`
}

// Watchers
watch(currentTime, (newTime) => {
  if (audioElement.value && Math.abs(newTime - audioElement.value.currentTime) > 0.5) {
    audioElement.value.currentTime = newTime
  }
})

// Lifecycle hooks
onMounted(() => {
  if (audioElement.value) {
    audioElement.value.volume = volume.value
  }
})

onBeforeUnmount(() => {
  if (audioElement.value && isPlaying.value) {
    audioElement.value.pause()
  }
})
</script>