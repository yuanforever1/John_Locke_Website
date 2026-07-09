<script setup>
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import client from '@/api/client'

const collections = ref([])
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const res = await client.get('/collections/')
    collections.value = res.data.results || res.data
  } catch (e) {
    error.value = '无法载入手稿库。'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="library container">
    <div class="section-head">
      <p class="eyebrow">Bibliotheca · 手稿典藏</p>
      <h1>洛克手稿库</h1>
      <p class="muted lede">
        系统收录的洛克手稿集，每一页均附有权威转写，可供比对研读。
      </p>
    </div>

    <div v-if="loading" class="text-center muted"><span class="loader"></span> 载入中…</div>
    <div v-else-if="error" class="alert">{{ error }}</div>

    <div v-else class="collection-grid">
      <RouterLink
        v-for="c in collections"
        :key="c.slug"
        :to="`/library/${c.slug}`"
        class="collection-card panel"
      >
        <div class="cc-side">
          <span class="cc-count">{{ c.page_count }}</span>
          <span class="cc-count-label">页</span>
        </div>
        <div class="cc-body">
          <p class="cc-period">{{ c.period }}</p>
          <h3 class="cc-title">{{ c.title }}</h3>
          <p class="cc-sub">{{ c.subtitle }}</p>
          <p class="cc-desc muted">{{ c.description }}</p>
          <p class="cc-lang small muted">语言 · {{ c.language }}</p>
        </div>
      </RouterLink>
    </div>
  </div>
</template>

<style scoped>
.library {
  padding: 4rem 0;
}
.section-head {
  text-align: center;
  margin-bottom: 3rem;
}
.section-head h1 {
  font-size: 2.8rem;
  font-family: var(--serif-cjk);
}
.lede {
  max-width: 560px;
  margin: 0.5rem auto 0;
}
.collection-grid {
  display: grid;
  gap: 1.6rem;
}
.collection-card {
  display: grid;
  grid-template-columns: 130px 1fr;
  color: var(--ink);
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}
.collection-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 28px var(--shadow);
}
.cc-side {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: var(--burgundy);
  color: var(--ivory);
}
.cc-count {
  font-family: var(--serif-latin);
  font-size: 2.8rem;
  line-height: 1;
}
.cc-count-label {
  font-family: var(--serif-cjk);
  letter-spacing: 0.3em;
  font-size: 0.8rem;
  margin-top: 0.3rem;
}
.cc-body {
  padding: 1.8rem 2rem;
}
.cc-period {
  font-family: var(--serif-latin);
  letter-spacing: 0.2em;
  color: var(--gold-deep);
  font-size: 0.9rem;
  margin-bottom: 0.3rem;
}
.cc-title {
  font-size: 1.6rem;
  font-family: var(--serif-cjk);
  margin-bottom: 0.15rem;
}
.cc-sub {
  font-family: var(--serif-latin);
  font-style: italic;
  color: var(--ink-soft);
  margin-bottom: 0.8rem;
}
.cc-desc {
  margin-bottom: 0.6rem;
  font-size: 0.98rem;
}
.cc-lang {
  margin: 0;
  letter-spacing: 0.1em;
}

@media (max-width: 640px) {
  .collection-card {
    grid-template-columns: 90px 1fr;
  }
  .cc-count {
    font-size: 2rem;
  }
}
</style>
