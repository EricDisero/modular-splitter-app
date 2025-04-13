import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

export const useAuthStore = defineStore('auth', () => {
  // State
  const licenseValidated = ref(false)
  const validationError = ref('')
  const isLoading = ref(false)

  // Computed properties
  const isAuthenticated = computed(() => licenseValidated.value)

  // Actions
  async function validateLicense(licenseKey) {
    isLoading.value = true
    validationError.value = ''

    try {
      // Create form data
      const formData = new FormData()
      formData.append('license_key', licenseKey)

      // Send validation request
      const response = await axios.post('/api/validate-license', formData, {
        withCredentials: true
      })

      // If successful, set authenticated
      if (response.data.success) {
        licenseValidated.value = true
        return true
      } else {
        validationError.value = response.data.message || 'License validation failed'
        return false
      }
    } catch (error) {
      console.error('License validation error:', error)
      validationError.value = error.response?.data?.message || 'An error occurred during validation'
      return false
    } finally {
      isLoading.value = false
    }
  }

  function clearValidation() {
    validationError.value = ''
  }

  async function logout() {
    try {
      // Send logout request
      await axios.post('/api/logout', {}, {
        withCredentials: true
      })
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      // Always clear authentication state locally
      licenseValidated.value = false
    }
  }

  return {
    // State
    licenseValidated,
    validationError,
    isLoading,

    // Computed
    isAuthenticated,

    // Actions
    validateLicense,
    clearValidation,
    logout
  }
})