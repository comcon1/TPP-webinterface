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
        <div v-if="show_download">
          <p>Results:</p>
          <ul class="result-files">
            <li v-for="file in result_files" :key="file.name">
              <a :href="file.url" :download="file.name" v-if="file.exists">{{ file.name }}</a>
              <span v-else>{{ file.name }} (not available)</span>
            </li>
          </ul>
        </div>
        <button @click="closeResult" :disabled="!show_download && !enable_close_button">Close</button>
      </div>
    </div>
</template>

<script>
import { apiUrl, upload_func, status_update } from '@/utils/misc.js'
const metaDescription = `
TPPMKTOP service of TPPMKTOP project. It allows one to upload
PDB file and get topology files for OPLS-AA (open source) force field.
`;

export default {
  metaInfo: {
    title: 'TPPMKTOP - MD topology generator',
    meta: [
      {
        name: 'description',
        content: metaDescription.trim()
      }
    ]
  },
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
      show_download: false,
      taskIds: [],
      pollInterval: null,
      updateDirAliveInterval: null,
      result_files: []
    }
  },
  methods: {
    async pollStatus() {
      await status_update(this, true);
    },
    async updateDirAlive() {
      fetch(`${apiUrl}/status/diralive/${this.taskIds[0]}`)
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
          if (data.dir_alive == 0) {
            strs.push('Folder has been removed.');
            this.show_download = false;
            this.enable_close_button = true;
            clearInterval(this.updateDirAliveInterval);
          }
          this.processing = strs.join('\n');
      })
      .catch(err => {
          this.error = 'Failed: ' + err.message;
          this.enable_close_button = true;
          clearInterval(this.updateDirAliveInterval);
      })
      .finally(() => {
          // we still show processing status
          // even without download abilities
          this.show_processing = true;
      });
    },
    updateFilesForDownload() {
      // make base file list
      let file_list = [
        'output.itp',
        'output_ff.itp',
        'lack.itp',
        'tppmktop.log',
        'console_output.log'
      ];
      this.result_files = [];
      for (let fnm of file_list) {
        this.result_files.push({
          name: fnm,
          url: `${apiUrl}/download/${this.taskIds[0]}/${fnm}`,
          exists: false
        });
      }
      // fetch file list from server
      let req = `${apiUrl}/status/files/${this.taskIds[0]}`;
      console.log('Fetching files from: ' + req);
      fetch(req)
      .then(async response => {
          if (!response.ok) {
            throw new Error('Server error: ' + (await response.text()));
          }
          return response.json();
      })
      .then(data => {
          console.log(JSON.stringify(data.files, null, 2));
          this.result_files.forEach(file => {
            file.exists = data.files[file.name] !== undefined;
          });
      })
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
      this.show_download = false;
      this.enable_close_button = false;
      this.taskIds = [];
      this.loading = false;
    },
    onFileChange() {
      this.clearAll();
    },  
    closeResult() {
      this.clearAll();
      if (this.updateDirAliveInterval !== null) {
        clearInterval(this.updateDirAliveInterval);
      }
      this.$refs.fileInput.value = '';
    }
  },
  mounted() {
    this.pollStatus();
    this.pollInterval = setInterval(this.pollStatus, 500);
  },
  beforeDestroy() {
    clearInterval(this.pollInterval);
    clearInterval(this.updateDirAliveInterval);
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
ul.result-files {
  list-style: none;        /* Remove default bullets */
  font-size: 9pt;
  padding: 0;
  margin: 0;
  font-family: 'Courier New', Courier, monospace;  /* Monospace (tt) font */
}

ul.result-files li {
  display: inline;         /* Display items in one line */
  font-family: inherit;    /* Inherit monospace font */
}

ul.result-files li:not(:last-child)::after {
  content: " | ";          /* Add separator after each item except last */
}
</style>
