import Vue from 'vue'
import Router from 'vue-router'

import Tpprenum from '../components/TpprenumPage.vue'
import Tppmktop from '../components/TppmktopPage.vue'
import About from '../components/AboutPage.vue'

Vue.use(Router)

export default new Router({
  mode: 'history',  // use history mode or 'hash'
  routes: [
    { path: '/tpprenum', component: Tpprenum },
    { path: '/tppmktop', component: Tppmktop },
    { path: '/about', component: About},
    { path: '*', redirect: '/about' }
  ]
})