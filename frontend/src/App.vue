<template>
  <div class="min-h-screen bg-gradient-to-b from-gray-900 to-black text-white">
    <header class="container mx-auto px-4 py-6">
      <div class="flex justify-between items-center">
        <div class="flex items-center">
          <h1 class="text-2xl font-bold bg-gradient-to-r from-purple-400 to-blue-500 bg-clip-text text-transparent">
            {{ appTitle }}
          </h1>
        </div>
        <nav>
          <ul class="flex space-x-4">
            <li>
              <router-link
                to="/"
                class="text-gray-300 hover:text-white px-3 py-2 rounded-md transition duration-150"
              >
                Home
              </router-link>
            </li>
            <li v-if="isAuthenticated">
              <router-link
                to="/split"
                class="text-gray-300 hover:text-white px-3 py-2 rounded-md transition duration-150"
              >
                Split
              </router-link>
            </li>
            <li v-if="isAuthenticated">
              <button
                @click="handleLogout"
                class="text-gray-300 hover:text-white px-3 py-2 rounded-md transition duration-150"
              >
                Logout
              </button>
            </li>
          </ul>
        </nav>
      </div>
    </header>

    <main class="container mx-auto px-4 py-8">
      <router-view />
    </main>

    <footer class="container mx-auto px-4 py-6 mt-12 border-t border-gray-800">
      <div class="text-center text-gray-500 text-sm">
        <p>Powered by Pulse Academy's AI stem separation technology</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'

const appTitle = import.meta.env.VITE_APP_TITLE || 'Stem Splitter Pro'
const router = useRouter()
const authStore = useAuthStore()

const isAuthenticated = computed(() => authStore.isAuthenticated)

async function handleLogout() {
  await authStore.logout()
  router.push('/')
}

onMounted(() => {
  // You might want to check the authentication status on page load
  // For example, by making a request to a validation endpoint
})
</script>