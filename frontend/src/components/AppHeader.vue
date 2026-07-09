<script setup>
import { ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const menuOpen = ref(false)

function logout() {
  auth.logout()
  menuOpen.value = false
  router.push('/')
}
</script>

<template>
  <header class="site-header">
    <div class="container header-inner">
      <RouterLink to="/" class="brand">
        <span class="brand-mark">JL</span>
        <span class="brand-text">
          <span class="brand-title">John Locke</span>
          <span class="brand-sub">手稿转写平台</span>
        </span>
      </RouterLink>

      <button class="nav-toggle" @click="menuOpen = !menuOpen" aria-label="菜单">
        <span></span><span></span><span></span>
      </button>

      <nav class="nav" :class="{ open: menuOpen }" @click="menuOpen = false">
        <RouterLink to="/">洛克其人</RouterLink>
        <RouterLink to="/library">手稿库</RouterLink>
        <RouterLink to="/workspace">工作区</RouterLink>
        <template v-if="auth.isAuthenticated">
          <RouterLink to="/profile" class="nav-name">{{ auth.displayName }}</RouterLink>
          <a href="#" @click.prevent="logout" class="nav-logout">离席</a>
        </template>
        <template v-else>
          <RouterLink to="/login" class="btn btn-sm btn-gold">登入</RouterLink>
        </template>
      </nav>
    </div>
  </header>
</template>

<style scoped>
.site-header {
  position: sticky;
  top: 0;
  z-index: 50;
  background: rgba(244, 237, 220, 0.94);
  backdrop-filter: blur(6px);
  border-bottom: 1px solid var(--line);
}
.header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 76px;
}
.brand {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  color: var(--ink);
}
.brand-mark {
  font-family: var(--serif-latin);
  font-weight: 600;
  font-size: 1.15rem;
  width: 44px;
  height: 44px;
  display: grid;
  place-items: center;
  border: 1px solid var(--gold-deep);
  color: var(--gold-deep);
  letter-spacing: 0.05em;
}
.brand-text {
  display: flex;
  flex-direction: column;
  line-height: 1.15;
}
.brand-title {
  font-family: var(--serif-latin);
  font-size: 1.3rem;
  font-weight: 600;
  letter-spacing: 0.04em;
}
.brand-sub {
  font-family: var(--serif-cjk);
  font-size: 0.72rem;
  letter-spacing: 0.34em;
  color: var(--ink-faint);
}
.nav {
  display: flex;
  align-items: center;
  gap: 2rem;
}
.nav > a {
  font-family: var(--serif-cjk);
  font-size: 0.92rem;
  letter-spacing: 0.16em;
  color: var(--ink-soft);
  position: relative;
}
.nav > a.router-link-active:not(.btn) {
  color: var(--burgundy);
}
.nav > a:not(.btn)::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: -6px;
  width: 0;
  height: 1px;
  background: var(--gold-deep);
  transition: width 0.25s ease;
}
.nav > a:not(.btn):hover::after,
.nav > a.router-link-active:not(.btn)::after {
  width: 100%;
}
.nav-name {
  color: var(--gold-deep) !important;
}
.nav-logout {
  color: var(--ink-faint) !important;
}
.nav-toggle {
  display: none;
  flex-direction: column;
  gap: 5px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 6px;
}
.nav-toggle span {
  width: 26px;
  height: 1.5px;
  background: var(--ink);
}

@media (max-width: 820px) {
  .nav-toggle {
    display: flex;
  }
  .nav {
    position: absolute;
    top: 76px;
    left: 0;
    right: 0;
    flex-direction: column;
    gap: 1.4rem;
    padding: 2rem;
    background: var(--paper);
    border-bottom: 1px solid var(--line);
    transform: translateY(-140%);
    transition: transform 0.3s ease;
  }
  .nav.open {
    transform: translateY(0);
  }
}
</style>
