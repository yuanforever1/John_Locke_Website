<script setup>
import { ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const form = ref({ username: '', email: '', nickname: '', password: '' })
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  loading.value = true
  try {
    await auth.register(form.value)
    router.push('/library')
  } catch (e) {
    const data = e.response?.data
    if (data && typeof data === 'object') {
      error.value = Object.values(data).flat().join(' ')
    } else {
      error.value = '注册失败，请稍后再试。'
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth container-narrow">
    <div class="auth-card panel">
      <p class="eyebrow text-center">Adhésion · 加入研究</p>
      <h1 class="auth-title">注 册</h1>
      <div class="ornament"><span class="diamond">❦</span></div>

      <div v-if="error" class="alert">{{ error }}</div>

      <form @submit.prevent="submit">
        <div class="field">
          <label>用户名</label>
          <input v-model="form.username" autocomplete="username" required />
        </div>
        <div class="field">
          <label>昵称</label>
          <input v-model="form.nickname" placeholder="将展示于个人主页" />
        </div>
        <div class="field">
          <label>邮箱 <span class="optional muted">（选填）</span></label>
          <input v-model="form.email" type="email" autocomplete="email" />
        </div>
        <div class="field">
          <label>密码</label>
          <input
            v-model="form.password"
            type="password"
            autocomplete="new-password"
            required
          />
        </div>
        <button class="btn btn-primary full" :disabled="loading">
          <span v-if="loading" class="loader"></span>
          <span v-else>创 建 账 户</span>
        </button>
      </form>

      <p class="switch muted text-center">
        已有账户？<RouterLink to="/login">前往登入</RouterLink>
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
  max-width: 480px;
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
.optional {
  font-size: 0.72rem;
  letter-spacing: 0.08em;
}
.ornament {
  margin: 1rem auto 1.8rem;
  max-width: 240px;
}
</style>
