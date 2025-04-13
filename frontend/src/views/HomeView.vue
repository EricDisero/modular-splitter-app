<template>
  <div class="flex items-center justify-center min-h-[70vh]">
    <div class="max-w-md w-full bg-gray-800/30 backdrop-blur-md border border-purple-500/30 rounded-xl p-6 shadow-xl">
      <h2 class="text-center text-2xl font-bold mb-6 bg-gradient-to-r from-purple-400 to-blue-500 bg-clip-text text-transparent">
        STEM SPLITTER PRO
      </h2>

      <div v-if="isAuthenticated">
        <div class="text-center mb-6">
          <p class="text-gray-300">You are logged in and can start splitting audio files.</p>
        </div>
        <router-link
          to="/split"
          class="w-full block text-center py-3 px-4 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 rounded-lg text-white font-medium transition duration-300"
        >
          Start Splitting
        </router-link>
      </div>

      <div v-else>
        <div v-if="validationError" class="bg-red-900/50 border border-red-500 text-red-200 px-4 py-3 rounded-lg mb-4">
          {{ validationError }}
        </div>

        <form @submit.prevent="validateLicense" class="space-y-4">
          <div>
            <label for="license-key" class="block text-sm font-medium text-gray-300 mb-1">License Key</label>
            <input
              id="license-key"
              v-model="licenseKey"
              type="text"
              placeholder="XXXX-XXXX-XXXX-XXXX"
              class="w-full px-4 py-3 bg-gray-700/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              required
            />
          </div>

          <div>
            <button
              type="submit"
              class="w-full py-3 px-4 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 rounded-lg text-white font-medium transition duration-300 flex items-center justify-center"
              :disabled="isLoading"
            >
              <svg v-if="isLoading" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>{{ isLoading ? 'Validating...' : 'Validate License' }}</span>
            </button>
          </div>
        </form>

        <div class="mt-6 text-center text-sm text-gray-500">
          <p>Need a license? Contact our sales team to purchase one.</p>
        </div>
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