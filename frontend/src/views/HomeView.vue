<template>
  <div class="flex items-center justify-center min-h-[70vh]">
    <div class="max-w-md w-full card">
      <h2 class="text-center text-2xl font-bold gradient-text mb-6">
        STEM SPLITTER PRO
      </h2>

      <div v-if="isAuthenticated">
        <div class="text-center mb-6">
          <p class="text-gray-300">You are logged in and can start splitting audio files.</p>
        </div>
        <router-link
          to="/split"
          class="btn"
        >
          Start Splitting
        </router-link>
      </div>

      <div v-else>
        <div v-if="validationError" class="error">
          {{ validationError }}
        </div>

        <form @submit.prevent="validateLicense" class="space-y-4">
          <div class="input-group">
            <label for="license-key" class="input-label">Enter your license key to begin</label>
            <input
              id="license-key"
              v-model="licenseKey"
              type="text"
              placeholder="XXXX-XXXX-XXXX-XXXX"
              class="input-field"
              required
            />
          </div>

          <button
            type="submit"
            class="btn"
            :disabled="isLoading"
          >
            <svg v-if="isLoading" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"></path>
            </svg>
            <span>{{ isLoading ? 'Validating...' : 'Validate License' }}</span>
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const licenseKey = ref('')

const isAuthenticated = computed(() => authStore.isAuthenticated)
const validationError = computed(() => authStore.validationError)
const isLoading = computed(() => authStore.isLoading)

async function validateLicense() {
  if (!licenseKey.value) return

  const success = await authStore.validateLicense(licenseKey.value)

  if (success) {
    // If validation was successful, redirect to the split page
    router.push('/split')
  }
}

onMounted(() => {
  // Clear any previous validation errors
  authStore.clearValidation()

  // If already authenticated, redirect to split page
  if (isAuthenticated.value) {
    router.push('/split')
  }
})
</script>