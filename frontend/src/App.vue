<template>
  <div class="min-h-screen bg-background text-white">
    <header class="py-6">
      <div class="container mx-auto px-4 flex justify-between items-center">
        <div>
          <h1 class="text-2xl font-bold gradient-text">STEM SPLITTER PRO</h1>
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

    <main>
      <div class="container mx-auto py-8">
        <router-view />
      </div>
    </main>

    <footer class="py-6 mt-12 border-t border-gray-800">
      <div class="container mx-auto text-center text-gray-500 text-sm">
        <p>Powered by Pulse Academy's AI stem separation technology</p>
      </div>
    </footer>
  </div>
</template>

<script>
export default {
  data() {
    return {
      audioName: '',
    };
  },
  methods: {
    browseFile() {
      this.$refs.fileInput.click();
    },
    handleFileSelect(event) {
      const file = event.target.files[0];
      if (file) {
        this.audioName = file.name;
        this.uploadFile(file);
      }
    },
    handleDrop(event) {
      const file = event.dataTransfer.files[0];
      if (file) {
        this.audioName = file.name;
        this.uploadFile(file);
      }
    },
    uploadFile(file) {
      const formData = new FormData();
      formData.append('file', file);

      fetch('http://localhost:8000/api/upload_audio/', {
        method: 'POST',
        body: formData,
        credentials: 'include',
      })
        .then(res => res.json())
        .then(data => {
          document.getElementById('afterUploading').style.display = 'block';
          document.getElementById('beforeUploading').style.display = 'none';
        });
    },
    submitSplit() {
      // Optional: show processing animation
      if (window.showProcessingAnimation) {
        window.showProcessingAnimation();
      }

      fetch('http://localhost:8000/api/split/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ file_name: this.audioName }),
        credentials: 'include',
      })
        .then(res => res.json())
        .then(data => {
          if (data.isFinished === 'exist') {
            document.getElementById('top_label').textContent = 'FOLDER WITH SONG NAME EXISTS';
          } else {
            document.getElementById('top_label').textContent = 'ERROR OCCURRED';
          }
          document.getElementById('afterUploading').style.display = 'none';
          document.getElementById('beforeUploading').style.display = 'block';
        });
    },
  }
};
</script>
