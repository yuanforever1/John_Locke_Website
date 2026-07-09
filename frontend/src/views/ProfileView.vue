<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const form = ref({ nickname: '', email: '', affiliation: '', bio: '' })
const message = ref('')
const error = ref('')
const saving = ref(false)
const avatarInput = ref(null)

const avatarUrl = computed(() => auth.profile?.avatar || '')
const initials = computed(() =>
  (auth.profile?.nickname || auth.profile?.username || 'JL').slice(0, 2).toUpperCase(),
)

onMounted(async () => {
  if (!auth.profile) await auth.fetchProfile()
  const p = auth.profile
  form.value = {
    nickname: p.nickname || '',
    email: p.email || '',
    affiliation: p.affiliation || '',
    bio: p.bio || '',
  }
})

async function save() {
  message.value = ''
  error.value = ''
  saving.value = true
  try {
    await auth.updateProfile(form.value)
    message.value = '档案已更新。'
  } catch (e) {
    error.value = '保存失败，请检查填写内容。'
  } finally {
    saving.value = false
  }
}

async function onAvatarChange(e) {
  const file = e.target.files[0]
  if (!file) return
  try {
    await auth.uploadAvatar(file)
    message.value = '头像已更新。'
  } catch (err) {
    error.value = '头像上传失败。'
  }
}
</script>

<template>
  <div class="profile container-narrow">
    <div class="section-head">
      <p class="eyebrow">Persona · 个人主页</p>
      <h1>研究者档案</h1>
    </div>

    <div v-if="message" class="alert alert-success">{{ message }}</div>
    <div v-if="error" class="alert">{{ error }}</div>

    <div class="p-card panel">
      <div class="p-identity">
        <div class="avatar" @click="avatarInput.click()">
          <img v-if="avatarUrl" :src="avatarUrl" alt="头像" />
          <span v-else>{{ initials }}</span>
          <div class="avatar-overlay">更换</div>
        </div>
        <input
          ref="avatarInput"
          type="file"
          accept="image/*"
          hidden
          @change="onAvatarChange"
        />
        <div class="p-meta">
          <h2>{{ auth.profile?.nickname || auth.profile?.username }}</h2>
          <p class="muted small">@{{ auth.profile?.username }}</p>
          <p class="muted small">
            入席于 {{ new Date(auth.profile?.date_joined).toLocaleDateString('zh-CN') }}
          </p>
        </div>
      </div>

      <div class="ornament"><span class="diamond">❧</span></div>

      <form @submit.prevent="save">
        <div class="field">
          <label>昵称</label>
          <input v-model="form.nickname" />
        </div>
        <div class="field">
          <label>邮箱</label>
          <input v-model="form.email" type="email" />
        </div>
        <div class="field">
          <label>机构 / 单位</label>
          <input v-model="form.affiliation" placeholder="如：某大学历史系" />
        </div>
        <div class="field">
          <label>个人简介</label>
          <textarea v-model="form.bio" rows="4" placeholder="研究方向、兴趣所在…"></textarea>
        </div>
        <button class="btn btn-primary" :disabled="saving">
          <span v-if="saving" class="loader"></span>
          <span v-else>保 存 档 案</span>
        </button>
      </form>
    </div>
  </div>
</template>

<style scoped>
.profile {
  padding: 3.5rem 0 5rem;
}
.section-head {
  text-align: center;
  margin-bottom: 2.5rem;
}
.section-head h1 {
  font-size: 2.4rem;
  font-family: var(--serif-cjk);
}
.p-card {
  padding: 2.5rem;
}
.p-identity {
  display: flex;
  align-items: center;
  gap: 1.6rem;
}
.avatar {
  position: relative;
  width: 96px;
  height: 96px;
  border-radius: 50%;
  overflow: hidden;
  border: 1px solid var(--gold-deep);
  background: var(--burgundy);
  color: var(--ivory);
  display: grid;
  place-items: center;
  font-family: var(--serif-latin);
  font-size: 2rem;
  cursor: pointer;
  flex-shrink: 0;
}
.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.avatar-overlay {
  position: absolute;
  inset: 0;
  background: rgba(34, 28, 20, 0.6);
  color: var(--ivory);
  display: grid;
  place-items: center;
  font-family: var(--serif-cjk);
  font-size: 0.8rem;
  letter-spacing: 0.2em;
  opacity: 0;
  transition: opacity 0.2s ease;
}
.avatar:hover .avatar-overlay {
  opacity: 1;
}
.p-meta h2 {
  margin: 0;
  font-family: var(--serif-cjk);
  font-size: 1.6rem;
}
.ornament {
  margin: 2rem 0;
}
</style>
