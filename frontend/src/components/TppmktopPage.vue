<template>
    <div class="container">
      <h1>PDB Topology Processing Service</h1>
      <form @submit.prevent="uploadFile">
        <input type="file" ref="fileInput" @change="onFileChange" accept=".pdb" required />
        <button type="submit" :disabled="loading">Upload and Process</button>
      </form>
      <div v-if="loading">Processing...</div>
      <div v-if="error" class="error">{{ error }}</div>
      <div v-if="show_processing">
        <p>Processing status:</p>
        <textarea rows="3" cols="80" readonly v-model="processing"></textarea>
      </div>
    </div>
</template>

<script>
import { upload_func, status_update } from '@/utils/misc.js'

export default {
  data() {
    return {
      loading: false,
      error: '',
      result: '',
      processing: '',
      reslog: '',
      res_copied: false,
      log_copied: false,
      show_processing: false,
      taskIds: [],
      pollInterval: null,
    }
  },
  methods: {
    async pollStatus() {
      await status_update(this);
    },
    uploadFile() {
      upload_func(this, 'tppmktop');
    }, 
    clearAll() {
      this.error = '';
      this.result = '';
      this.reslog = '';
      this.res_copied = false;
      this.log_copied = false;
      this.processing = '';
      this.show_processing = false;
      this.taskIds = [];
      this.loading = false;
    },
    onFileChange() {
      this.clearAll();
    }  
  },
  mounted() {
    this.pollStatus();
    this.pollInterval = setInterval(this.pollStatus, 500);
  },
  beforeDestroy() {
    clearInterval(this.pollInterval);
  }
}
</script>

<style>
.container {
  max-width: 900px;
  margin: 2em auto;
  padding: 2em;
  border: 1px solid #ccc;
  border-radius: 8px;
}
.error {
  color: red;
  margin-top: 1em;
}
.modal {
  margin-top: 2em;
  padding: 1em;
  background: #f8f8f8;
  border: 1px solid #aaa;
  border-radius: 8px;
}
textarea {
  width: 100%;
  font-family: monospace;
  font-size: 6pt;
}
button {
  margin: 0.5em 0.5em 0 0;
}
</style>
