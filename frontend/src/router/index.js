import Vue from 'vue'
import Router from 'vue-router'

import Tpprenum from '../components/TpprenumPage.vue'
import Tppmktop from '../components/TppmktopPage.vue'

Vue.use(Router)

export default new Router({
  mode: 'history',  // use history mode or 'hash'
  routes: [
    { path: '/tpprenum', component: Tpprenum },
    { path: '/tppmktop', component: Tppmktop },
    { path: '*', redirect: '/tpprenum' }
  ]
})