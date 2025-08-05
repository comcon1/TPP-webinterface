<template>
  <div>
    <nav>
      <router-link to="/page1" :class="{ active: currentTab === 'page1' }">Page 1</router-link>
      <router-link to="/page2" :class="{ active: currentTab === 'page2' }">Page 2</router-link>
    </nav>

    <div class="tab-content">
      <div v-if="currentTab === 'page1'">
        <h2>Content for Page 1</h2>
        <p>This is the first tab content.</p>
      </div>

      <div v-else-if="currentTab === 'page2'">
        <h2>Content for Page 2</h2>
        <p>This is the second tab content.</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: ['tab'],
  computed: {
    // Determine current tab from prop or route path
    currentTab() {
      // if 'tab' prop is passed via route props, use that
      if(this.tab) return this.tab;
      // fallback: parse from full path
      const path = this.$route.path.replace('/', '');
      return path === 'page1' || path === 'page2' ? path : 'page1'
    }
  }
}
</script>

<style>
nav {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.active {
  font-weight: bold;
  text-decoration: underline;
}
</style>