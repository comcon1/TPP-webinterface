<template>
  <div class="container">
    <h1>PDB Renumbering Service</h1>
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
    <div v-if="result" class="modal">
      <table>
        <tr>
          <td>
            <h2>Processed PDB</h2>
            <textarea rows="20" cols="80" readonly v-model="result" ref="resultTA"></textarea>
          </td>
          <td>
            <h2>Program LOG</h2>
            <textarea rows="20" cols="80" readonly v-model="reslog" ref="logTA"></textarea>
          </td>
        </tr>
        <tr>
          <td>
            <button @click="copyResult">Copy to Clipboard</button>
            <button @click="downloadResult">Download file</button>
            <div v-if="res_copied" style="color:green;">Copied!</div>
          </td>
          <td>
            <button @click="copyLog">Copy to Clipboard</button>
            <button @click="downloadLog">Download log</button>
            <div v-if="log_copied" style="color:green;">Copied!</div>
          </td>
        </tr>
      </table>
      <button @click="closeResult">Close</button>
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
    },  
    uploadFile() {
      upload_func(this, 'tpprenum');
    },
    //  ---------------------------------------
    //            Other stuff
    //  --------------------------------------- 
    copyResult() {
      const textarea = this.$refs.resultTA;
      textarea.focus();
      textarea.select();
      try {
        const successful = document.execCommand('copy');
        if (successful) {
          this.res_copied = true;
          setTimeout(() => (this.res_copied = false), 1500);
        } else {
          this.error = 'Copy failed';
        }
      } catch (err) {
        this.error = 'Copy error: ' + err;
      }
      window.getSelection().removeAllRanges();
    },
    copyLog() {
      const textarea = this.$refs.logTA;
      textarea.focus();
      textarea.select();
      try {
        const successful = document.execCommand('copy');
        if (successful) {
          this.log_copied = true;
          setTimeout(() => (this.log_copied = false), 1500);
        } else {
          this.error = 'Copy failed';
        }
      } catch (err) {
        this.error = 'Copy error: ' + err;
      }
      window.getSelection().removeAllRanges();
    },
    downloadResult() {
      const blob = new Blob([this.result], { type: "chemical/x-pdb" });
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = "processed.pdb";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(link.href);
    },
    downloadLog() {
      const blob = new Blob([this.reslog], { type: "text/plain" });
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = "program.log";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(link.href);
    },
    closeResult() {
      this.clearAll();
      this.$refs.fileInput.value = '';
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
