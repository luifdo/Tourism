<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import BrandLogo from './BrandLogo.vue'
import InstallButton from './InstallButton.vue'

const { t, locale } = useI18n()
const menu = ref(false)

function setLang(l) {
  locale.value = l
  document.documentElement.lang = l
  try { localStorage.setItem('lang', l) } catch { /* sin almacenamiento */ }
}
const links = [['catalog', '#catalogo'], ['map', '#mapa'], ['routes', '#rutas'], ['ethics', '#compromiso']].map(([k, hash]) => [k, { name: 'home', hash }])
</script>

<template>
  <!-- Cinta superior (se desplaza con la página) -->
  <div class="flex items-center justify-between gap-4 bg-cream px-[clamp(16px,3vw,32px)] font-mono text-[11px] text-ink-control" style="height: var(--ticker-h)">
    <p class="flex min-w-0 items-center gap-2.5 truncate">
      <i class="size-1.5 shrink-0 rounded-full bg-teal" />
      <b class="shrink-0 font-semibold uppercase tracking-wider text-navy-darkest">{{ t('ticker.badge') }}</b>
      <span class="hidden truncate text-muted sm:inline">· {{ t('ticker.text') }}</span>
    </p>
    <div class="flex shrink-0 items-center gap-4">
      <span class="hidden items-center gap-1.5 text-teal md:flex">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M5 12a7 7 0 0114 0M8.5 12a3.5 3.5 0 017 0" /><circle cx="12" cy="12" r="1" /></svg>
        {{ t('ticker.live') }}
      </span>
      <div role="group" aria-label="Idioma / Language">
        <button type="button" :aria-pressed="locale === 'es'" :class="locale === 'es' ? 'font-bold text-navy' : 'text-muted'" @click="setLang('es')">ES</button>
        <span class="mx-1 text-muted">|</span>
        <button type="button" :aria-pressed="locale === 'en'" :class="locale === 'en' ? 'font-bold text-navy' : 'text-muted'" @click="setLang('en')">EN</button>
      </div>
    </div>
  </div>

  <!-- Barra principal fija -->
  <header class="sticky top-0 z-50 bg-cream/90 px-[clamp(16px,3vw,32px)] backdrop-blur-xl" style="height: var(--nav-h)">
    <nav class="mx-auto flex h-full max-w-[1400px] items-center justify-between gap-4" aria-label="Principal">
      <RouterLink :to="{ name: 'home' }" class="shrink-0" aria-label="Samaland adventure"><BrandLogo /></RouterLink>

      <div class="hidden items-center rounded-full border border-sand/30 bg-white px-3 py-1.5 shadow-card xl:flex">
        <RouterLink v-for="[k, to] in links" :key="k" :to="to" class="max-w-[150px] rounded-full px-4 py-1.5 text-center text-[13px] font-medium leading-tight text-ink-control transition-colors hover:bg-cream hover:text-navy">{{ t(`nav.${k}`) }}</RouterLink>
      </div>

      <div class="flex items-center gap-3">
        <InstallButton />
        <RouterLink :to="{ name: 'my-bookings' }" class="flex items-center gap-1.5 text-[13px] font-medium text-navy transition-colors hover:text-teal">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 3h12v18l-3-2-3 2-3-2-3 2z" /><path d="M9 8h6M9 12h6" /></svg>
          <span class="hidden sm:inline">{{ t('nav.reservations') }}</span>
        </RouterLink>
        <button type="button" class="xl:hidden" :aria-label="t('nav.menu')" :aria-expanded="menu" @click="menu = !menu">
          <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16" /></svg>
        </button>
      </div>
    </nav>

    <div v-if="menu" class="absolute inset-x-0 top-full flex flex-col gap-1 border-b border-sand/30 bg-cream p-4 shadow-elevated xl:hidden">
      <RouterLink v-for="[k, to] in links" :key="k" :to="to" class="rounded-lg px-3 py-3 font-medium text-ink-control hover:bg-white" @click="menu = false">{{ t(`nav.${k}`) }}</RouterLink>
      <RouterLink :to="{ name: 'my-bookings' }" class="rounded-lg px-3 py-3 font-medium text-navy hover:bg-white" @click="menu = false">{{ t('nav.reservations') }}</RouterLink>
    </div>
  </header>
</template>
