<template>
  <div>
    <div v-if="!uploading && !uploadComplete">
      <div
        class="border-2 border-dashed border-gray-600 rounded-lg p-6 text-center hover:border-purple-500 transition-colors duration-200"
        :class="{ 'border-purple-500 bg-purple-500/10': isDragging }"
        @dragover.prevent="isDragging = true"
        @dragleave.prevent="isDragging = false"
        @drop.prevent="handleFileDrop"
        @click="triggerFileInput"
      >
        <div class="text-purple-400 mb-3">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
        </div>
        <p class="text-gray-300 mb-2">Drag and drop your audio file here</p>
        <p class="text-gray-500 text-sm mb-4">or click to browse</p>
        <p class="text-gray-500 text-xs">Supports MP3, WAV, FLAC, AIF (max 500MB)</p>
      </div>

      <input
        ref="fileInput"
        type="file"
        class="hidden"
        accept=".mp3,.wav,.flac,.aif,.aiff"
        @change="handleFileChange"
      />
    </div>

    <div v-else-if="uploading">
      <div class="bg-gray-800 rounded-lg p-6">
        <div class="flex items-center justify-between mb-2">
          <div class="flex-1 truncate mr-2">
            <p class="text-gray-300 text-sm font-medium truncate">{{ file.name }}</p>
            <p class="text-gray-500 text-xs">{{ formatFileSize(file.size) }}</p>
          </div>
          <button
            @click="cancelUpload"
            class="text-gray-400 hover:text-gray-300"
            :disabled="!canCancel"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="w-full bg-gray-700 rounded-full h-2.5">
          <div class="bg-purple-600 h-2.5 rounded-full" :style="`width: ${uploadProgress}%`"></div>
        </div>

        <div class="flex justify-between mt-2 text-xs text-gray-500">
          <span>{{ uploadProgress }}%</span>
          <span>{{ formatFileSize(uploadedBytes) }} / {{ formatFileSize(file.size) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { uploadAudio } from '../utils/api'

// Props & Emits
const emit = defineEmits(['file-selected', 'upload-success', 'upload-error'])

// Refs
const fileInput = ref(null)
const isDragging = ref(false)
const file = ref(null)
const uploading = ref(false)
const uploadComplete = ref(false)
const uploadProgress = ref(0)
const uploadedBytes = ref(0)
const uploadController = ref(null)
const canCancel = ref(true)

// Methods
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
  if (!validTypes.includes(selectedFile.type)) {
    emit('upload-error', 'Invalid file type. Please upload MP3, WAV, FLAC, or AIF files only.')
    return
  }

  // Check file size (500MB limit)
  if (selectedFile.size > 500 * 1024 * 1024) {
    emit('upload-error', 'File too large. Maximum file size is 500MB.')
    return
  }

  // Set file and start upload
  file.value = selectedFile
  emit('file-selected', selectedFile)
  startUpload()
}

async function startUpload() {
  if (!file.value) return

  uploading.value = true
  uploadProgress.value = 0
  uploadedBytes.value = 0

  try {
    const result = await uploadAudio(file.value, (progress) => {
      uploadProgress.value = progress
      uploadedBytes.value = Math.floor(file.value.size * (progress / 100))
    })

    uploadComplete.value = true
    emit('upload-success', result)
  } catch (error) {
    console.error('Upload error:', error)
    emit('upload-error', error.response?.data?.detail || 'Failed to upload file')
  } finally {
    uploading.value = false
  }
}

function cancelUpload() {
  if (!canCancel.value) return

  // Cancel upload if possible
  if (uploadController.value) {
    uploadController.value.abort()
  }

  // Reset state
  file.value = null
  uploading.value = false
  uploadProgress.value = 0
  uploadedBytes.value = 0

  emit('upload-error', 'Upload cancelled')
}

// Utilities
function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes'

  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}
</script>