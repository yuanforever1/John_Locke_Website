<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import client from '@/api/client'

const route = useRoute()
const pageData = ref(null)
const loading = ref(true)
const error = ref('')
const zoom = ref(false)

async function load() {
  loading.value = true
  error.value = ''
  try {
    const res = await client.get(`/pages/${route.params.id}/`)
    pageData.value = res.data
  } catch (e) {
    error.value = '无法载入该手稿页。'
  } finally {
    loading.value = false
  }
}

onMounted(load)
watch(() => route.params.id, load)
</script>

<template>
  <div class="detail container">
    <div v-if="loading" class="text-center muted"><span class="loader"></span> 载入中…</div>
    <div v-else-if="error" class="alert">{{ error }}</div>

    <template v-else-if="pageData">
      <RouterLink :to="`/library/${pageData.collection.slug}`" class="back small">
        ‹ 返回《{{ pageData.collection.title }}》
      </RouterLink>

      <header class="d-head">
        <p class="eyebrow">{{ pageData.collection.title }} · {{ pageData.collection.period }}</p>
        <h1>第 {{ pageData.page_number }} 页</h1>
        <p class="muted small">{{ pageData.image_name }}</p>
      </header>

      <div class="d-grid">
        <figure class="d-image panel">
          <img
            :src="pageData.image"
            :alt="pageData.image_name"
            :class="{ zoomed: zoom }"
            @click="zoom = !zoom"
          />
          <figcaption class="muted small">{{ zoom ? '点击缩小' : '点击放大查看细节' }}</figcaption>
        </figure>

        <section class="d-text panel">
          <div class="dt-head">
            <span class="dt-label">官方转写 · Ground Truth</span>
          </div>
          <div class="dt-body">
            <p>{{ pageData.transcription }}</p>
          </div>
        </section>
      </div>
    </template>
  </div>
</template>

<style scoped>
.detail {
  padding: 2.5rem 0 4rem;
}
.back {
  display: inline-block;
  margin-bottom: 1.5rem;
  color: var(--ink-faint);
  letter-spacing: 0.1em;
}
.d-head {
  text-align: center;
  margin-bottom: 2.5rem;
}
.d-head h1 {
  font-size: 2.4rem;
  font-family: var(--serif-cjk);
}
.d-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  align-items: start;
}
.d-image {
  margin: 0;
  padding: 1rem;
  text-align: center;
}
.d-image img {
  width: 100%;
  cursor: zoom-in;
  transition: transform 0.3s ease;
}
.d-image img.zoomed {
  transform: scale(1.6);
  cursor: zoom-out;
}
.d-image figcaption {
  margin-top: 0.7rem;
  letter-spacing: 0.08em;
}
.d-text {
  position: sticky;
  top: 100px;
}
.dt-head {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--line);
  background: var(--paper-2);
}
.dt-label {
  font-family: var(--serif-cjk);
  letter-spacing: 0.2em;
  font-size: 0.82rem;
  color: var(--sepia);
}
.dt-body {
  padding: 1.8rem;
  max-height: 60vh;
  overflow-y: auto;
}
.dt-body p {
  font-family: var(--serif-latin);
  font-size: 1.12rem;
  line-height: 1.9;
  color: var(--ink);
  white-space: pre-wrap;
  margin: 0;
  text-align: justify;
}

@media (max-width: 860px) {
  .d-grid {
    grid-template-columns: 1fr;
  }
  .d-text {
    position: static;
  }
}
</style>
