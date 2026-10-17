<script setup lang="ts">
import GlobalHeader from '@/components/GlobalHeader.vue'
import GlobalSlicer from '@/components/GlobalSlicer.vue'
</script>

<template>
  <div class="app-layout">
    <GlobalHeader />
    <GlobalSlicer />
    <main class="app-main">
      <div class="content-wrapper">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </main>
  </div>
</template>

<style>
/* Global resets & typography */
html,
body {
  margin: 0;
  padding: 0;
  font-family:
    -apple-system,
    BlinkMacSystemFont,
    'Segoe UI',
    Roboto,
    'Helvetica Neue',
    Arial,
    'Noto Sans',
    sans-serif,
    'Apple Color Emoji',
    'Segoe UI Emoji',
    'Segoe UI Symbol',
    'Noto Color Emoji';
  background-color: #f5f7fa;
  color: #303133;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

* {
  box-sizing: border-box;
}

#app {
  min-height: 100vh;
}
</style>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-main {
  flex: 1;
  padding: 24px 0 40px;
}

.content-wrapper {
  max-width: 1440px;
  margin: 0 auto;
  padding: 0 24px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
