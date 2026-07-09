<script setup></script>

<template>
  <footer class="site-footer">
    <div class="container footer-inner">
      <div class="ornament">
        <span class="diamond">❧</span>
      </div>
      <p class="footer-title">John Locke Manuscript Atelier</p>
      <p class="footer-note muted small">
        面向数字人文研究的洛克手稿转写与识别平台 · 数据集为洛克法国旅行日记（1675–1679）
      </p>
      <p class="footer-copy muted small">
        © {{ new Date().getFullYear() }} 洛克手稿转写平台 · 仅用于学术研究与教学
      </p>
    </div>
  </footer>
</template>

<style scoped>
.site-footer {
  margin-top: 5rem;
  padding: 2.5rem 0 3.5rem;
  border-top: 1px solid var(--line);
  background: var(--paper-2);
  text-align: center;
}
.footer-title {
  font-family: var(--serif-latin);
  font-size: 1.25rem;
  letter-spacing: 0.08em;
  margin-bottom: 0.4rem;
}
.footer-note {
  margin-bottom: 0.3rem;
}
.footer-copy {
  margin: 0;
  letter-spacing: 0.06em;
}
.ornament {
  margin: 0 auto 1.4rem;
  max-width: 320px;
}
</style>
