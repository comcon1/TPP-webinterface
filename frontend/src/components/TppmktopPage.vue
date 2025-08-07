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
import { apiUrl, upload_func, status_update } from '@/utils/misc.js'

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
      await status_update(this, true);
    },
    async updateDirAlive() {
      fetch(`${apiUrl}/status/diralive/${this.taskIds[0]}/`)
      .then(async response => {
          if (!response.ok) {
          throw new Error('Server error: ' + (await response.text()))
          }
          var x = response.json();
          // console.log(JSON.stringify(x, null, 2));
          return x;
      })
      .then(data => {
          if (data.task_id !== this.taskIds[0]) {
              throw new Error("Task ID mismatch: expected " + this.taskIds[0] + ", got " + data.task_id);
          }
          let strs = this.processing.split('\n');
          strs[1] = 'Folder will be removed in ' + data.dir_alive.toFixed(1) + ' min.';
          this.processing = strs.join('\n');
      })
      .catch(err => {
          this.error = 'Failed: ' + err.message;
      })
      .finally(() => {
          this.show_processing = true;
      });
    },
    uploadFile() {
      upload_func(this, 'tppmktop');
      this.processing += '\nFolder will be removed in 5 min.'
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
