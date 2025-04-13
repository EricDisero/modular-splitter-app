import axios from 'axios'

// Create axios instance with default config
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Upload related functions
export async function uploadAudio(file, onProgress) {
  const formData = new FormData()
  formData.append('file', file)

  try {
    const response = await api.post('/api/upload-audio', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress: progressEvent => {
        if (onProgress && progressEvent.total) {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(percentCompleted)
        }
      }
    })

    return response.data
  } catch (error) {
    console.error('Upload error:', error)
    throw error
  }
}

// Split related functions
export async function requestSplit(objectName) {
  try {
    const response = await api.post('/api/split', {
      object_name: objectName
    })

    return response.data
  } catch (error) {
    console.error('Split request error:', error)
    throw error
  }
}

export async function checkSplitStatus(jobId) {
  try {
    const response = await api.get(`/api/split/${jobId}/status`)
    return response.data
  } catch (error) {
    console.error('Status check error:', error)
    throw error
  }
}

// Poll for split job status until complete or failed
export function pollJobStatus(jobId, onUpdate, interval = 5000) {
  let timerId = null

  const checkStatus = async () => {
    try {
      const status = await checkSplitStatus(jobId)
      onUpdate(status)

      // If job is completed or failed, stop polling
      if (status.status === 'completed' || status.status === 'failed') {
        clearInterval(timerId)
      }
    } catch (error) {
      console.error('Polling error:', error)
      clearInterval(timerId)
      onUpdate({ status: 'error', error: error.message })
    }
  }

  // Start polling
  timerId = setInterval(checkStatus, interval)

  // Do an immediate check
  checkStatus()

  // Return a function to stop polling
  return () => {
    if (timerId) {
      clearInterval(timerId)
    }
  }
}

export default api