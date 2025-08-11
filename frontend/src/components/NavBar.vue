<template>
  <nav class="navbar">
    <ul>
      <li>
        <router-link to="/tpprenum">TPPrenum</router-link>
      </li>
      <li>
        <router-link to="/tppmktop">TPPmktop</router-link>
      </li>
      <li>
        <router-link to="/about">About</router-link>
      </li>
    </ul>
  </nav>
</template>

<script>
export default {
  name: 'NavBar'
}
</script>

<style scoped>
.navbar {
  display: flex;
  background-color: #333;
  padding: 1rem;
}
.navbar ul {
  list-style: none;
  display: flex;
  margin: 0;
  padding: 0;
}
.navbar li {
  margin-right: 1rem;
}
.navbar a {
  color: white;
  text-decoration: none;
}
</style>