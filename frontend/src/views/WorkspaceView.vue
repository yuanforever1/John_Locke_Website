<script setup>
import { ref, onMounted, computed } from 'vue'
import client from '@/api/client'

const folders = ref([])
const images = ref([])
const currentFolder = ref('root') // 'root' 或 文件夹 id
const loadingImages = ref(false)
const uploading = ref(false)
const message = ref('')
const error = ref('')

const selected = ref(new Set())
const newFolderName = ref('')
const showNewFolder = ref(false)
const fileInput = ref(null)
const busyIds = ref(new Set())
const viewer = ref(null) // 当前查看识别结果的图片

const currentFolderName = computed(() => {
  if (currentFolder.value === 'root') return '根目录'
  const f = folders.value.find((x) => x.id === currentFolder.value)
  return f ? f.name : '文件夹'
})

const anySelected = computed(() => selected.value.size > 0)

function flash(msg, isError = false) {
  if (isError) {
    error.value = msg
    message.value = ''
  } else {
    message.value = msg
    error.value = ''
  }
  setTimeout(() => {
    message.value = ''
    error.value = ''
  }, 3500)
}

async function loadFolders() {
  const res = await client.get('/folders/')
  folders.value = res.data
}

async function loadImages() {
  loadingImages.value = true
  selected.value = new Set()
  try {
    const res = await client.get('/images/', {
      params: { folder: currentFolder.value },
    })
    images.value = res.data.results || res.data
  } finally {
    loadingImages.value = false
  }
}

function selectFolder(id) {
  currentFolder.value = id
  loadImages()
}

async function createFolder() {
  if (!newFolderName.value.trim()) return
  try {
    await client.post('/folders/', { name: newFolderName.value.trim() })
    newFolderName.value = ''
    showNewFolder.value = false
    await loadFolders()
    flash('文件夹已建立。')
  } catch (e) {
    flash(e.response?.data?.name?.[0] || '创建失败，名称可能重复。', true)
  }
}

async function deleteFolder(f) {
  if (!confirm(`确定删除文件夹「${f.name}」及其中全部图片？`)) return
  await client.delete(`/folders/${f.id}/`)
  if (currentFolder.value === f.id) currentFolder.value = 'root'
  await loadFolders()
  await loadImages()
  flash('文件夹已删除。')
}

function triggerUpload() {
  fileInput.value.click()
}

async function onFilesChosen(e) {
  const files = Array.from(e.target.files)
  if (!files.length) return
  await uploadFiles(files)
  e.target.value = ''
}

async function uploadFiles(files) {
  uploading.value = true
  try {
    const form = new FormData()
    files.forEach((f) => form.append('images', f))
    if (currentFolder.value !== 'root') form.append('folder', currentFolder.value)
    await client.post('/images/', form)
    await loadImages()
    await loadFolders()
    flash(`已上传 ${files.length} 张手稿。`)
  } catch (e) {
    flash('上传失败。', true)
  } finally {
    uploading.value = false
  }
}

function onDrop(e) {
  const files = Array.from(e.dataTransfer.files).filter((f) =>
    f.type.startsWith('image/'),
  )
  if (files.length) uploadFiles(files)
}

async function deleteImage(img) {
  if (!confirm('确定删除这张图片？')) return
  await client.delete(`/images/${img.id}/`)
  await loadImages()
  await loadFolders()
  flash('图片已删除。')
}

function toggleSelect(id) {
  const s = new Set(selected.value)
  s.has(id) ? s.delete(id) : s.add(id)
  selected.value = s
}

function selectAll() {
  if (selected.value.size === images.value.length) {
    selected.value = new Set()
  } else {
    selected.value = new Set(images.value.map((i) => i.id))
  }
}

async function recognize(img) {
  const s = new Set(busyIds.value)
  s.add(img.id)
  busyIds.value = s
  try {
    const res = await client.post(`/images/${img.id}/recognize/`)
    img.recognition = res.data
    if (res.data.status === 'failed') flash(res.data.error || '识别失败。', true)
    else flash('识别完成。')
  } catch (e) {
    flash('识别请求失败。', true)
  } finally {
    const s2 = new Set(busyIds.value)
    s2.delete(img.id)
    busyIds.value = s2
  }
}

async function batchRecognize() {
  const ids = Array.from(selected.value)
  if (!ids.length) return
  busyIds.value = new Set(ids)
  try {
    const res = await client.post('/images/batch_recognize/', { ids })
    for (const item of res.data.results) {
      const img = images.value.find((i) => i.id === item.id)
      if (img) img.recognition = item.recognition
    }
    flash(`已批量识别 ${ids.length} 张。`)
  } catch (e) {
    flash('批量识别失败。', true)
  } finally {
    busyIds.value = new Set()
  }
}

function statusBadge(rec) {
  if (!rec) return { label: '未识别', cls: '' }
  const map = {
    done: { label: '已完成', cls: 'badge-done' },
    failed: { label: '失败', cls: 'badge-failed' },
    processing: { label: '识别中', cls: 'badge-processing' },
    pending: { label: '待识别', cls: '' },
  }
  return map[rec.status] || { label: rec.status_display, cls: '' }
}

onMounted(async () => {
  await loadFolders()
  await loadImages()
})
</script>

<template>
  <div class="workspace container">
    <div class="section-head">
      <p class="eyebrow">Scriptorium · 我的工作区</p>
      <h1>手稿工作台</h1>
      <p class="muted lede">
        建立文件夹以整理你的手稿影像，上传后即可交由 Agnes 智能识别为可读文本。
      </p>
    </div>

    <div v-if="message" class="alert alert-success">{{ message }}</div>
    <div v-if="error" class="alert">{{ error }}</div>

    <div class="ws-layout">
      <!-- 侧栏：文件夹 -->
      <aside class="ws-side panel">
        <div class="side-head">
          <span class="side-title">文件夹</span>
          <button class="icon-btn" @click="showNewFolder = !showNewFolder" title="新建文件夹">＋</button>
        </div>

        <div v-if="showNewFolder" class="new-folder">
          <input
            v-model="newFolderName"
            placeholder="文件夹名称"
            @keyup.enter="createFolder"
          />
          <button class="btn btn-sm btn-primary" @click="createFolder">建立</button>
        </div>

        <ul class="folder-list">
          <li
            :class="{ active: currentFolder === 'root' }"
            @click="selectFolder('root')"
          >
            <span class="f-name">根目录</span>
          </li>
          <li
            v-for="f in folders"
            :key="f.id"
            :class="{ active: currentFolder === f.id }"
            @click="selectFolder(f.id)"
          >
            <span class="f-name">{{ f.name }}</span>
            <span class="f-count">{{ f.image_count }}</span>
            <button class="f-del" @click.stop="deleteFolder(f)" title="删除">×</button>
          </li>
        </ul>
      </aside>

      <!-- 主区：图片 -->
      <section class="ws-main">
        <div class="main-toolbar">
          <div class="mt-left">
            <h3 class="mt-title">{{ currentFolderName }}</h3>
            <span class="muted small">{{ images.length }} 张</span>
          </div>
          <div class="mt-actions">
            <button v-if="images.length" class="btn btn-sm" @click="selectAll">
              {{ selected.size === images.length ? '取消全选' : '全选' }}
            </button>
            <button
              class="btn btn-sm btn-gold"
              :disabled="!anySelected"
              @click="batchRecognize"
            >
              批量识别 ({{ selected.size }})
            </button>
            <button class="btn btn-sm btn-primary" @click="triggerUpload" :disabled="uploading">
              <span v-if="uploading" class="loader"></span>
              <span v-else>上传手稿</span>
            </button>
            <input
              ref="fileInput"
              type="file"
              accept="image/*"
              multiple
              hidden
              @change="onFilesChosen"
            />
          </div>
        </div>

        <div
          class="dropzone"
          @dragover.prevent
          @drop.prevent="onDrop"
        >
          <div v-if="loadingImages" class="empty muted">
            <span class="loader"></span> 载入中…
          </div>
          <div v-else-if="!images.length" class="empty muted">
            <p>此处尚无手稿。</p>
            <p class="small">点击「上传手稿」，或将图片拖拽至此。</p>
          </div>

          <div v-else class="img-grid">
            <article
              v-for="img in images"
              :key="img.id"
              class="img-card panel"
              :class="{ selected: selected.has(img.id) }"
            >
              <div class="ic-thumb" @click="toggleSelect(img.id)">
                <img :src="img.image" :alt="img.original_name" loading="lazy" />
                <span class="ic-check" v-if="selected.has(img.id)">✓</span>
              </div>
              <div class="ic-body">
                <p class="ic-name" :title="img.original_name">{{ img.original_name }}</p>
                <span class="badge" :class="statusBadge(img.recognition).cls">
                  {{ statusBadge(img.recognition).label }}
                </span>
              </div>
              <div class="ic-actions">
                <button
                  class="btn btn-sm btn-gold"
                  :disabled="busyIds.has(img.id)"
                  @click="recognize(img)"
                >
                  <span v-if="busyIds.has(img.id)" class="loader"></span>
                  <span v-else>识别</span>
                </button>
                <button
                  v-if="img.recognition && img.recognition.status === 'done'"
                  class="btn btn-sm"
                  @click="viewer = img"
                >
                  查看
                </button>
                <button class="btn btn-sm del-btn" @click="deleteImage(img)">删除</button>
              </div>
            </article>
          </div>
        </div>
      </section>
    </div>

    <!-- 识别结果查看 -->
    <div v-if="viewer" class="modal" @click.self="viewer = null">
      <div class="modal-card panel">
        <div class="modal-head">
          <span class="dt-label">识别转写 · {{ viewer.original_name }}</span>
          <button class="icon-btn" @click="viewer = null">×</button>
        </div>
        <div class="modal-body">
          <div class="mb-image">
            <img :src="viewer.image" :alt="viewer.original_name" />
          </div>
          <div class="mb-text">
            <p>{{ viewer.recognition.text }}</p>
          </div>
        </div>
        <div class="modal-foot muted small">
          模型 · {{ viewer.recognition.model_name || 'Agnes' }}
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.workspace {
  padding: 3rem 0 4rem;
}
.section-head {
  text-align: center;
  margin-bottom: 2.5rem;
}
.section-head h1 {
  font-size: 2.6rem;
  font-family: var(--serif-cjk);
}
.lede {
  max-width: 600px;
  margin: 0.5rem auto 0;
}
.ws-layout {
  display: grid;
  grid-template-columns: 260px 1fr;
  gap: 1.6rem;
  align-items: start;
}

/* 侧栏 */
.ws-side {
  padding: 1.4rem;
  position: sticky;
  top: 100px;
}
.side-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}
.side-title {
  font-family: var(--serif-cjk);
  letter-spacing: 0.2em;
  font-size: 0.9rem;
  color: var(--sepia);
}
.icon-btn {
  background: none;
  border: 1px solid var(--line);
  width: 28px;
  height: 28px;
  cursor: pointer;
  color: var(--ink-soft);
  font-size: 1.1rem;
  line-height: 1;
}
.icon-btn:hover {
  border-color: var(--gold-deep);
  color: var(--gold-deep);
}
.new-folder {
  display: flex;
  gap: 0.4rem;
  margin-bottom: 1rem;
}
.new-folder input {
  flex: 1;
  min-width: 0;
  padding: 0.4rem 0.6rem;
  border: 1px solid var(--line);
  background: var(--paper);
  font-family: var(--serif-body);
}
.folder-list {
  list-style: none;
  margin: 0;
  padding: 0;
}
.folder-list li {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 0.7rem;
  cursor: pointer;
  border-left: 2px solid transparent;
  transition: background 0.15s ease;
}
.folder-list li:hover {
  background: var(--paper-2);
}
.folder-list li.active {
  background: var(--paper-3);
  border-left-color: var(--burgundy);
}
.f-name {
  flex: 1;
  font-family: var(--serif-cjk);
  font-size: 0.95rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.f-count {
  font-family: var(--serif-latin);
  font-size: 0.8rem;
  color: var(--ink-faint);
}
.f-del {
  background: none;
  border: none;
  color: var(--ink-faint);
  cursor: pointer;
  font-size: 1.1rem;
  opacity: 0;
}
.folder-list li:hover .f-del {
  opacity: 1;
}
.f-del:hover {
  color: var(--burgundy);
}

/* 主区 */
.main-toolbar {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.4rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--line);
  flex-wrap: wrap;
}
.mt-left {
  display: flex;
  align-items: baseline;
  gap: 0.8rem;
}
.mt-title {
  margin: 0;
  font-family: var(--serif-cjk);
  font-size: 1.5rem;
}
.mt-actions {
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
}
.dropzone {
  min-height: 300px;
}
.empty {
  text-align: center;
  padding: 5rem 1rem;
  border: 1px dashed var(--line);
}
.img-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1.3rem;
}
.img-card {
  overflow: hidden;
  transition: box-shadow 0.2s ease;
}
.img-card.selected {
  box-shadow: 0 0 0 2px var(--gold-deep);
}
.ic-thumb {
  position: relative;
  height: 200px;
  overflow: hidden;
  background: var(--paper-3);
  cursor: pointer;
  border-bottom: 1px solid var(--line-soft);
}
.ic-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: top center;
  filter: sepia(0.1);
}
.ic-check {
  position: absolute;
  top: 0.6rem;
  right: 0.6rem;
  width: 26px;
  height: 26px;
  background: var(--gold-deep);
  color: var(--ivory);
  display: grid;
  place-items: center;
  border-radius: 50%;
  font-size: 0.85rem;
}
.ic-body {
  padding: 0.8rem 0.9rem 0.4rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.ic-name {
  margin: 0;
  font-size: 0.85rem;
  color: var(--ink-soft);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.ic-actions {
  display: flex;
  gap: 0.4rem;
  padding: 0.5rem 0.9rem 0.9rem;
}
.ic-actions .btn {
  flex: 1;
  padding: 0.35rem 0.4rem;
  font-size: 0.72rem;
}
.del-btn:hover {
  background: var(--burgundy);
  border-color: var(--burgundy);
  color: var(--ivory);
}

/* 模态框 */
.modal {
  position: fixed;
  inset: 0;
  background: rgba(34, 28, 20, 0.55);
  display: grid;
  place-items: center;
  z-index: 100;
  padding: 2rem;
}
.modal-card {
  width: min(920px, 100%);
  max-height: 88vh;
  display: flex;
  flex-direction: column;
  background: var(--ivory);
}
.modal-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--line);
  background: var(--paper-2);
}
.dt-label {
  font-family: var(--serif-cjk);
  letter-spacing: 0.16em;
  font-size: 0.85rem;
  color: var(--sepia);
}
.modal-body {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  padding: 1.5rem;
  overflow-y: auto;
}
.mb-image img {
  width: 100%;
  border: 1px solid var(--line-soft);
}
.mb-text p {
  font-family: var(--serif-latin);
  font-size: 1.1rem;
  line-height: 1.85;
  white-space: pre-wrap;
  margin: 0;
  text-align: justify;
}
.modal-foot {
  padding: 0.8rem 1.5rem;
  border-top: 1px solid var(--line);
  text-align: right;
}

@media (max-width: 860px) {
  .ws-layout {
    grid-template-columns: 1fr;
  }
  .ws-side {
    position: static;
  }
  .modal-body {
    grid-template-columns: 1fr;
  }
}
</style>
