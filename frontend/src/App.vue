<script setup>
import AppNavbar from './components/AppNavbar.vue'
import OfflineBar from './components/OfflineBar.vue'
import AppFooter from './components/AppFooter.vue'
import AssistantDrawer from './components/AssistantDrawer.vue'
</script>

<template>
  <AppNavbar />
  <OfflineBar />
  <main>
    <RouterView />
  </main>
  <AppFooter />
  <AssistantDrawer />
</template>
