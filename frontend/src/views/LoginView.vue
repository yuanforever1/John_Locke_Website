<script setup>
import { ref } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(username.value, password.value)
    router.push(route.query.redirect || '/library')
  } catch (e) {
    error.value =
      e.response?.data?.detail || '登入失败，请核对用户名与密码。'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth container-narrow">
    <div class="auth-card panel">
      <p class="eyebrow text-center">Bienvenue · 欢迎归来</p>
      <h1 class="auth-title">登 入</h1>
      <div class="ornament"><span class="diamond">❧</span></div>

      <div v-if="error" class="alert">{{ error }}</div>

      <form @submit.prevent="submit">
        <div class="field">
          <label>用户名</label>
          <input v-model="username" autocomplete="username" required />
        </div>
        <div class="field">
          <label>密码</label>
          <input
            v-model="password"
            type="password"
            autocomplete="current-password"
            required
          />
        </div>
        <button class="btn btn-primary full" :disabled="loading">
          <span v-if="loading" class="loader"></span>
          <span v-else>进 入</span>
        </button>
      </form>

      <p class="switch muted text-center">
        尚未拥有账户？<RouterLink to="/register">在此注册</RouterLink>
      </p>
    </div>
  </div>
</template>

<style scoped>
.auth {
  padding: 4rem 0 5rem;
}
.auth-card {
  padding: 3rem;
  max-width: 460px;
  margin: 0 auto;
}
.auth-title {
  text-align: center;
  font-size: 2.4rem;
  font-family: var(--serif-cjk);
  letter-spacing: 0.3em;
  margin: 0;
}
.full {
  width: 100%;
  margin-top: 0.5rem;
}
.switch {
  margin-top: 1.6rem;
  font-size: 0.92rem;
}
.ornament {
  margin: 1rem auto 1.8rem;
  max-width: 240px;
}
</style>
