<template>
  <main>
    <div class="container">
      <h1>STEM SPLITTER PRO</h1>

      <router-view />

      <div class="footer">
        powered by Pulse Academy's AI stem separation technology
      </div>
    </div>
  </main>
</template>

<script setup>
// Import our CSS
import './assets/css/modern_styles.css'
</script>

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
