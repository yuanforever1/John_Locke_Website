<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import client from '@/api/client'

const route = useRoute()
const collection = ref(null)
const pages = ref([])
const loading = ref(true)
const search = ref('')
const page = ref(1)
const totalCount = ref(0)
const pageSize = 24

async function loadCollection() {
  const res = await client.get(`/collections/${route.params.slug}/`)
  collection.value = res.data
}

async function loadPages() {
  loading.value = true
  const res = await client.get(`/collections/${route.params.slug}/pages/`, {
    params: { page: page.value, search: search.value || undefined },
  })
  pages.value = res.data.results
  totalCount.value = res.data.count
  loading.value = false
}

let searchTimer
function onSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    page.value = 1
    loadPages()
  }, 350)
}

function changePage(delta) {
  const next = page.value + delta
  if (next < 1 || (next - 1) * pageSize >= totalCount.value) return
  page.value = next
  loadPages()
}

onMounted(async () => {
  await loadCollection()
  await loadPages()
})

watch(() => route.params.slug, async () => {
  page.value = 1
  await loadCollection()
  await loadPages()
})
</script>

<template>
  <div class="collection container">
    <RouterLink to="/library" class="back small">‹ 返回手稿库</RouterLink>

    <header v-if="collection" class="col-head">
      <p class="eyebrow">{{ collection.period }} · {{ collection.page_count }} 页</p>
      <h1>{{ collection.title }}</h1>
      <p class="col-sub">{{ collection.subtitle }}</p>
      <p class="muted col-desc">{{ collection.description }}</p>
    </header>

    <div class="toolbar">
      <input
        v-model="search"
        @input="onSearch"
        class="search-input"
        placeholder="在转写文本中检索关键词…"
      />
      <span class="muted small">共 {{ totalCount }} 页</span>
    </div>

    <div v-if="loading" class="text-center muted"><span class="loader"></span> 载入中…</div>

    <div v-else class="page-grid">
      <RouterLink
        v-for="p in pages"
        :key="p.id"
        :to="`/page/${p.id}`"
        class="page-card panel"
      >
        <div class="pc-thumb">
          <img :src="p.image" :alt="p.image_name" loading="lazy" />
        </div>
        <div class="pc-body">
          <p class="pc-num">第 {{ p.page_number }} 页</p>
          <p class="pc-excerpt">{{ p.excerpt }}</p>
        </div>
      </RouterLink>
    </div>

    <div v-if="!loading && totalCount > pageSize" class="pager">
      <button class="btn btn-sm" @click="changePage(-1)" :disabled="page === 1">
        ‹ 上一页
      </button>
      <span class="muted small">第 {{ page }} 页</span>
      <button
        class="btn btn-sm"
        @click="changePage(1)"
        :disabled="page * pageSize >= totalCount"
      >
        下一页 ›
      </button>
    </div>
  </div>
</template>

<style scoped>
.collection {
  padding: 2.5rem 0 4rem;
}
.back {
  display: inline-block;
  margin-bottom: 1.5rem;
  color: var(--ink-faint);
  letter-spacing: 0.1em;
}
.col-head {
  text-align: center;
  margin-bottom: 2.5rem;
}
.col-head h1 {
  font-size: 2.6rem;
  font-family: var(--serif-cjk);
}
.col-sub {
  font-family: var(--serif-latin);
  font-style: italic;
  font-size: 1.2rem;
  color: var(--gold-deep);
}
.col-desc {
  max-width: 640px;
  margin: 0.6rem auto 0;
}
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--line);
}
.search-input {
  flex: 1;
  max-width: 420px;
  padding: 0.6rem 0.9rem;
  font-family: var(--serif-body);
  font-size: 1rem;
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: 1px;
}
.search-input:focus {
  outline: none;
  border-color: var(--gold);
}
.page-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
  gap: 1.5rem;
}
.page-card {
  color: var(--ink);
  transition: transform 0.22s ease, box-shadow 0.22s ease;
  overflow: hidden;
}
.page-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 26px var(--shadow);
}
.pc-thumb {
  height: 240px;
  overflow: hidden;
  background: var(--paper-3);
  border-bottom: 1px solid var(--line-soft);
}
.pc-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: top center;
  filter: sepia(0.12);
}
.pc-body {
  padding: 1rem 1.1rem 1.2rem;
}
.pc-num {
  font-family: var(--serif-latin);
  letter-spacing: 0.14em;
  color: var(--gold-deep);
  font-size: 0.85rem;
  margin-bottom: 0.4rem;
}
.pc-excerpt {
  font-size: 0.9rem;
  color: var(--ink-soft);
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.pager {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1.5rem;
  margin-top: 3rem;
}
</style>
