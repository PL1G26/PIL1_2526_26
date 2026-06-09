<script setup>
import { onMounted } from 'vue'
import { store } from './store'

onMounted(() => {
  store.initAuth()
})
</script>

<template>
  <router-view />
</template>
