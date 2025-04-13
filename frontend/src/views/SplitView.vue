<template>
  <div class="max-w-4xl mx-auto">
    <h2 class="text-2xl font-bold mb-6">Split Audio</h2>

    <div v-if="error" class="bg-red-900/50 border border-red-500 text-red-200 px-4 py-3 rounded-lg mb-6">
      {{ error }}
    </div>

    <!-- Step 1: Upload -->
    <div v-if="currentStep === 'upload'" class="bg-gray-800/30 backdrop-blur-md border border-purple-500/30 rounded-xl p-6 shadow-xl">
      <h3 class="text-xl font-semibold mb-4">Upload Your Audio File</h3>

      <FileUploader
        @file-selected="handleFileSelected"
        @upload-success="handleUploadSuccess"
        @upload-error="handleUploadError"
      />
    </div>

    <!-- Step 2: Split -->
    <div v-else-if="currentStep === 'split'" class="bg-gray-800/30 backdrop-blur-md border border-purple-500/30 rounded-xl p-6 shadow-xl">
      <h3 class="text-xl font-semibold mb-4">Process Audio</h3>

      <div class="mb-6 p-4 bg-gray-700/50 rounded-lg">
        <div class="flex items-center">
          <div class="bg-purple-500/20 p-3 rounded-lg mr-4">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
            </svg>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-gray-300 truncate">
              {{ uploadedFileName }}
            </p>
            <p class="text-xs text-gray-500">
              {{ formatFileSize(uploadedFileSize) }}
            </p>
          </div>
        </div>
      </div>

      <p class="text-gray-300 mb-6">
        Your file is ready to be processed. Click the button below to start splitting it into separate stems.
      </p>

      <button
        @click="startSplitting"
        class="w-full py-3 px-4 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 rounded-lg text-white font-medium transition duration-300 flex items-center justify-center"
        :disabled="isProcessing"
      >
        <svg v-if="isProcessing" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span>{{ isProcessing ? 'Processing...' : 'Split Audio' }}</span>
      </button>
    </div>

    <!-- Step 3: Processing -->
    <div v-else-if="currentStep === 'processing'" class="bg-gray-800/30 backdrop-blur-md border border-purple-500/30 rounded-xl p-6 shadow-xl">
      <h3 class="text-xl font-semibold mb-4">Processing Your Audio</h3>

      <ProcessingAnimation :progress="processingProgress" :message="processingMessage" />

      <div class="mt-6 text-center text-sm text-gray-400">
        <p>This process may take several minutes depending on the length of your audio file.</p>
        <p>You can leave this page and come back later. Your results will be waiting for you.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import FileUploader from '../components/FileUploader.vue'
import ProcessingAnimation from '../components/ProcessingAnimation.vue'
import { requestSplit, pollJobStatus } from '../utils/api'

const router = useRouter()

// State
const currentStep = ref('upload')
const error = ref('')
const uploadedFile = ref(null)
const uploadedFileName = ref('')
const uploadedFileSize = ref(0)
const uploadedObjectName = ref('')
const isProcessing = ref(false)
const jobId = ref('')
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

const processingMessage = computed(() => {
  const index = Math.floor((processingProgress.value / 100) * processingMessages.length)
  return processingMessages[Math.min(index, processingMessages.length - 1)]
})

// Handlers
function handleFileSelected(file) {
  uploadedFile.value = file
  uploadedFileName.value = file.name
  uploadedFileSize.value = file.size
}

function handleUploadSuccess(data) {
  uploadedObjectName.value = data.object_name
  currentStep.value = 'split'
}

function handleUploadError(errorMessage) {
  error.value = errorMessage || 'An error occurred during upload'
}

async function startSplitting() {
  if (!uploadedObjectName.value) {
    error.value = 'No file selected'
    return
  }

  isProcessing.value = true
  error.value = ''

  try {
    // Request the splitting process
    const response = await requestSplit(uploadedObjectName.value)

    // Store the job ID
    jobId.value = response.job_id

    // Move to processing step
    currentStep.value = 'processing'

    // Start polling for status
    stopPolling.value = pollJobStatus(jobId.value, handleStatusUpdate, 3000)
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to start processing'
    isProcessing.value = false
  }
}

function handleStatusUpdate(status) {
  // Update progress
  processingProgress.value = status.progress || 0

  // Check if processing is complete
  if (status.status === 'completed') {
    // Navigate to result page
    router.push({
      name: 'result',
      params: { jobId: jobId.value }
    })
  }
  // Check if processing failed
  else if (status.status === 'failed') {
    currentStep.value = 'split'
    isProcessing.value = false
    error.value = status.error || 'Processing failed'

    // Stop polling
    if (stopPolling.value) {
      stopPolling.value()
    }
  }
}

// Utilities
function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes'

  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// Clean up
onUnmounted(() => {
  // Stop polling when component is unmounted
  if (stopPolling.value) {
    stopPolling.value()
  }
})
</script>