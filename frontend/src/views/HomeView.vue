<template>
  <div class="step active" id="step-license">
    <form @submit.prevent="validateLicense">
      <div class="input-group">
        <label class="input-label">Enter your license key to begin</label>
        <input
          type="text"
          v-model="licenseKey"
          class="input-field"
          placeholder="XXXX-XXXX-XXXX-XXXX">
      </div>

      <button type="submit" class="btn" :disabled="isLoading">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"></path>
        </svg>
        {{ isLoading ? 'Validating...' : 'Validate License' }}
      </button>
    </form>

    <div v-if="validationError" class="error">
      {{ validationError }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const licenseKey = ref('')
const isLoading = ref(false)
const validationError = ref('')

async function validateLicense() {
  if (!licenseKey.value) {
    validationError.value = 'License key cannot be empty!'
    return
  }

  isLoading.value = true
  validationError.value = ''

  try {
    const success = await authStore.validateLicense(licenseKey.value)
    if (success) {
      router.push('/split')
    } else {
      validationError.value = 'Invalid license key. Please try again.'
    }
  } catch (error) {
    validationError.value = error.message || 'Validation failed. Please try again.'
  } finally {
    isLoading.value = false
  }
}
</script>