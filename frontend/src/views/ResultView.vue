<template>
  <div class="max-w-4xl mx-auto">
    <h2 class="text-2xl font-bold mb-6">Splitting Results</h2>

    <div v-if="error" class="error">
      {{ error }}
    </div>

    <div v-if="isLoading" class="card flex justify-center">
      <div class="text-center">
        <svg class="animate-spin h-10 w-10 text-purple-400 mx-auto mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <p class="text-gray-300">Loading your results...</p>
      </div>
    </div>

    <div v-else-if="jobStatus === 'completed'" class="card">
      <div class="mb-6">
        <h3 class="text-xl font-semibold mb-2">Splitting Complete!</h3>
        <p class="text-gray-300">Your audio has been successfully split into the following stems:</p>
      </div>

      <!-- Stem cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div v-for="stem in stems" :key="stem.stem_name" class="bg-gray-700/50 rounded-lg p-4">
          <div class="flex items-center mb-3">
            <div class="bg-purple-500/20 p-2 rounded-lg mr-3">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
              </svg>
            </div>
            <div>
              <h4 class="font-medium text-white capitalize">{{ formatStemName(stem.stem_name) }}</h4>
              <p class="text-xs text-gray-400">{{ stem.filename }}</p>
            </div>
          </div>

          <!-- Audio player for previewing stems -->
          <AudioPlayer v-if="stem.download_url"
                       :src="stem.download_url"
                       :stem-name="stem.stem_name" />

          <a
            v-if="stem.download_url"
            :href="stem.download_url"
            download
            class="mt-2 w-full block text-center py-2 px-3 bg-gray-600 hover:bg-gray-500 rounded-lg text-white text-sm font-medium transition duration-150"
          >
            Download {{ formatStemName(stem.stem_name) }}
          </a>
        </div>
      </div>

      <!-- Download All button -->
      <div v-if="zipDownloadUrl" class="mt-6">
        <a
          :href="zipDownloadUrl"
          download
          class="btn"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          Download All Stems (ZIP)
        </a>
      </div>

      <div class="mt-6 text-center">
        <router-link
          to="/split"
          class="btn-secondary"
        >
          Split Another Track
        </router-link>
      </div>
    </div>

    <div v-else-if="jobStatus === 'processing'" class="card">
      <h3 class="text-xl font-semibold mb-4">Processing Your Audio</h3>

      <ProcessingAnimation :progress="processingProgress" :message="processingMessage" />

      <div class="mt-6 text-center text-sm text-gray-400">
        <p>Your audio is still being processed. This may take several minutes depending on the length of your audio file.</p>
      </div>
    </div>

    <div v-else-if="jobStatus === 'failed'" class="card">
      <div class="text-center">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-red-500 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <h3 class="text-xl font-semibold mb-2">Processing Failed</h3>
        <p class="text-gray-300 mb-6">Unfortunately, there was an error processing your audio file.</p>
        <div class="bg-red-900/30 border border-red-500/30 text-red-200 px-4 py-3 rounded-lg mb-6 text-left">
          <p class="text-sm">{{ jobError || 'An unknown error occurred' }}</p>
        </div>
        <router-link
          to="/split"
          class="btn-secondary"
        >
          Try Again
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AudioPlayer from '../components/AudioPlayer.vue'
import ProcessingAnimation from '../components/ProcessingAnimation.vue'
import { checkSplitStatus, pollJobStatus } from '../utils/api'

const route = useRoute()
const router = useRouter()

// State
const isLoading = ref(true)
const error = ref('')
const jobData = ref(null)
const processingProgress = ref(0)
const stopPolling = ref(null)

// Processing messages for animation
const processingMessages = [
  "Calibrating quantum entanglement parameters.",
  "Analyzing frequency spectrum bands...",
  "Isolating vocals using neural networks...",
  "Separating drum patterns from mix...",
  "Extracting bass frequencies...",
  "Applying stem separation algorithms...",
  "Preparing final audio components..."
]

// Computed properties
const jobId = computed(() => route.params.jobId)
const jobStatus = computed(() => jobData.value?.status)
const jobError = computed(() => jobData.value?.error)
const stems = computed(() => jobData.value?.stems || [])
const processingMessage = computed(() => {
  const index = Math.floor((processingProgress.value / 100) * processingMessages.length)
  return processingMessages[Math.min(index, processingMessages.length - 1)]
})
const zipDownloadUrl = computed(() => {
  const zipStem = stems.value.find(stem => stem.stem_name === 'zip')
  return zipStem?.download_url
})

// Methods
async function loadJobStatus() {
  isLoading.value = true
  error.value = ''

  try {
    // Get initial job status
    const status = await checkSplitStatus(jobId.value)
    jobData.value = status
    processingProgress.value = status.progress || 0

    // If the job is still processing, start polling
    if (status.status === 'processing' || status.status === 'queued') {
      stopPolling.value = pollJobStatus(jobId.value, handleStatusUpdate, 3000)
    }
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to load job status'
  } finally {
    isLoading.value = false
  }
}

function handleStatusUpdate(status) {
  jobData.value = status
  processingProgress.value = status.progress || 0
}

function formatStemName(name) {
  if (!name) return ''

  if (name === 'ee') return 'Everything Else'

  return name.charAt(0).toUpperCase() + name.slice(1)
}

// Lifecycle hooks
onMounted(() => {
  loadJobStatus()
})

onUnmounted(() => {
  // Stop polling when component is unmounted
  if (stopPolling.value) {
    stopPolling.value()
  }
})
</script>