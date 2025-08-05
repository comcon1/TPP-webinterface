<template>
    <div class="container"></div>
</template>

<script>
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
    // Define methods here
  },
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
