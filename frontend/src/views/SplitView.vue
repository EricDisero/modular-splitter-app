<template>
  <div class="max-w-4xl mx-auto">
    <h2 class="text-2xl font-bold mb-6">Split Audio</h2>

    <div v-if="error" class="error">
      {{ error }}
    </div>

    <!-- Step 1: Upload -->
    <div v-if="currentStep === 'upload'" class="card">
      <h3 class="text-xl font-semibold mb-4">Upload Your Audio File</h3>

      <div
        class="dropzone"
        :class="{ 'drag-over': isDragging }"
        @dragover.prevent="isDragging = true"
        @dragleave.prevent="isDragging = false"
        @drop.prevent="handleFileDrop"
        @click="triggerFileInput"
      >
        <div class="dropzone-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="17 8 12 3 7 8"></polyline>
            <line x1="12" y1="3" x2="12" y2="15"></line>
          </svg>
        </div>
        <div class="input-label">Drop your audio file here</div>
        <div class="text-gray-500 text-sm">or click to browse</div>
        <div class="text-gray-500 text-xs mt-2">Supports .mp3, .wav, .flac, .aif</div>
      </div>

      <input
        ref="fileInput"
        type="file"
        class="hidden"
        accept=".mp3,.wav,.flac,.aif,.aiff"
        @change="handleFileChange"
      />

      <div v-if="uploading" class="mt-4">
        <div class="flex items-center justify-between mb-2">
          <div class="flex-1 truncate mr-2">
            <p class="text-gray-300 text-sm font-medium truncate">{{ file?.name }}</p>
            <p class="text-gray-500 text-xs">{{ formatFileSize(file?.size || 0) }}</p>
          </div>
        </div>

        <div class="w-full bg-gray-700 rounded-full h-2.5">
          <div class="bg-purple-600 h-2.5 rounded-full" :style="`width: ${uploadProgress}%`"></div>
        </div>

        <div class="flex justify-between mt-2 text-xs text-gray-500">
          <span>{{ uploadProgress }}%</span>
          <span>{{ formatFileSize(uploadedBytes) }} / {{ formatFileSize(file?.size || 0) }}</span>
        </div>
      </div>
    </div>

    <!-- Step 2: Split -->
    <div v-else-if="currentStep === 'split'" class="card">
      <h3 class="text-xl font-semibold mb-4">Process Audio</h3>

      <div class="file-info">
        <div class="file-info-header">
          <div class="file-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M9 18V5l12-2v13"></path>
              <circle cx="6" cy="18" r="3"></circle>
              <circle cx="18" cy="16" r="3"></circle>
            </svg>
          </div>
          <div class="flex-1 min-w-0">
            <p class="file-name">
              {{ uploadedFileName }}
            </p>
            <p class="text-gray-500 text-xs">
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
        class="btn"
        :disabled="isProcessing"
      >
        <svg v-if="isProcessing" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"></path>
        </svg>
        <span>{{ isProcessing ? 'Processing...' : 'Split Audio' }}</span>
      </button>
    </div>

    <!-- Step 3: Processing -->
    <div v-else-if="currentStep === 'processing'" class="card">
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
import ProcessingAnimation from '../components/ProcessingAnimation.vue'
import { uploadAudio, requestSplit, pollJobStatus } from '../utils/api'

const router = useRouter()

// State
const currentStep = ref('upload')
const error = ref('')
const file = ref(null)
const fileInput = ref(null)
const isDragging = ref(false)
const uploading = ref(false)
const uploadComplete = ref(false)
const uploadProgress = ref(0)
const uploadedBytes = ref(0)
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
function triggerFileInput() {
  fileInput.value.click()
}

function handleFileChange(event) {
  if (event.target.files.length) {
    const selectedFile = event.target.files[0]
    validateAndUploadFile(selectedFile)
  }
}

function handleFileDrop(event) {
  isDragging.value = false

  if (event.dataTransfer.files.length) {
    const droppedFile = event.dataTransfer.files[0]
    validateAndUploadFile(droppedFile)
  }
}

function validateAndUploadFile(selectedFile) {
  // Check file type
  const validTypes = [
    'audio/mpeg',
    'audio/mp3',
    'audio/wav',
    'audio/flac',
    'audio/aiff',
    'audio/x-aiff'
  ]

  // Get file extension
  const extension = selectedFile.name.split('.').pop().toLowerCase()
  const validExtensions = ['mp3', 'wav', 'flac', 'aif', 'aiff']

  if (!validTypes.includes(selectedFile.type) && !validExtensions.includes(extension)) {
    error.value = 'Invalid file type. Please upload MP3, WAV, FLAC, or AIF files only.'
    return
  }

  // Check file size (500MB limit)
  if (selectedFile.size > 500 * 1024 * 1024) {
    error.value = 'File too large. Maximum file size is 500MB.'
    return
  }

  // Set file and start upload
  file.value = selectedFile
  startUpload()
}

async function startUpload() {
  if (!file.value) return

  uploading.value = true
  uploadProgress.value = 0
  uploadedBytes.value = 0
  error.value = ''

  try {
    const result = await uploadAudio(file.value, (progress) => {
      uploadProgress.value = progress
      uploadedBytes.value = Math.floor(file.value.size * (progress / 100))
    })

    uploadComplete.value = true
    uploadedFileName.value = result.filename
    uploadedFileSize.value = result.size
    uploadedObjectName.value = result.object_name
    currentStep.value = 'split'
  } catch (err) {
    console.error('Upload error:', err)
    error.value = err.response?.data?.detail || 'Failed to upload file'
  } finally {
    uploading.value = false
  }
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