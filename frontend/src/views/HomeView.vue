<script setup>
import { RouterLink } from 'vue-router'
import lockePortrait from '@/assets/images/john-locke-portrait.png'

const timeline = [
  { year: '1632', text: '生于英格兰萨默塞特郡林顿的一个清教徒家庭。' },
  { year: '1652', text: '入读牛津大学基督堂学院，研习逻辑、形而上学与古典语言。' },
  { year: '1667', text: '成为沙夫茨伯里伯爵的私人医生与顾问，投身政治生活。' },
  { year: '1675', text: '因健康与政局旅居法国，写下大量旅行日记与观察笔记。' },
  { year: '1683', text: '因政治牵连流亡荷兰，于异乡完成多部重要著作的酝酿。' },
  { year: '1689', text: '光荣革命后返英，《政府论》与《论宽容》相继问世。' },
  { year: '1690', text: '《人类理解论》出版，奠定其经验主义认识论的地位。' },
  { year: '1704', text: '于埃塞克斯郡奥茨庄园逝世，长眠于高莱恩教堂。' },
]

const works = [
  {
    title: 'An Essay Concerning Human Understanding',
    zh: '《人类理解论》',
    year: '1690',
    desc: '系统阐述心灵如白板（tabula rasa）之说，主张一切知识源于经验，为近代经验主义奠基。',
  },
  {
    title: 'Two Treatises of Government',
    zh: '《政府论》',
    year: '1689',
    desc: '论自然权利、社会契约与有限政府，深刻影响了此后的宪政思想与近代革命。',
  },
  {
    title: 'A Letter Concerning Toleration',
    zh: '《论宽容》',
    year: '1689',
    desc: '主张政教分离与信仰自由，为现代宽容与多元社会提供了思想根基。',
  },
  {
    title: 'Some Thoughts Concerning Education',
    zh: '《教育漫话》',
    year: '1693',
    desc: '强调德性、习惯与理性的养成，成为近代自由教育理念的重要源头。',
  },
]
</script>

<template>
  <div class="home">
    <!-- 首屏 -->
    <section class="hero">
      <div class="container hero-inner">
        <div class="hero-text">
          <p class="eyebrow">Philosophus · 1632 — 1704</p>
          <h1 class="hero-title">约翰 · 洛克</h1>
          <p class="hero-latin">John Locke</p>
          <p class="hero-lede">
            英格兰启蒙运动的奠基者，经验主义哲学与自由主义政治的先声。
            于其手稿的字里行间，思想的生成脉络清晰可循。
          </p>
          <div class="hero-actions">
            <RouterLink to="/library" class="btn btn-primary">披览手稿库</RouterLink>
            <RouterLink to="/workspace" class="btn">进入工作区</RouterLink>
          </div>
        </div>
        <figure class="hero-portrait">
          <div class="portrait-frame">
            <img :src="lockePortrait" alt="约翰·洛克肖像" />
          </div>
          <figcaption>约翰·洛克像 · 巴洛克风格肖像</figcaption>
        </figure>
      </div>
      <div class="hero-quote container-narrow">
        <blockquote>
          “No man's knowledge here can go beyond his experience.”
          <cite>—— An Essay Concerning Human Understanding, II</cite>
        </blockquote>
      </div>
    </section>

    <div class="ornament container-narrow">
      <span class="diamond">❦</span>
    </div>

    <!-- 生平 -->
    <section class="container life">
      <div class="section-head">
        <p class="eyebrow">生 平</p>
        <h2>思想者的一生</h2>
      </div>
      <div class="life-grid">
        <div class="life-prose">
          <p>
            约翰·洛克生于英国内战前夜的动荡年代，早年于牛津大学接受古典与经院训练，
            却对当时僵化的学院哲学颇感不满，转而钻研笛卡尔、医学与实验科学。
            与化学家玻意耳、医生西德纳姆的交往，塑造了他重实证、尚经验的治学品格。
          </p>
          <p>
            步入政界后，他辅佐沙夫茨伯里伯爵，亲历英国宪政的风云变幻。
            旅法与流亡荷兰的岁月，既是颠沛，也是沉潜——正是在这些年间，
            他将毕生思考凝练为影响深远的著述。晚年归国，声望日隆，
            终成一代宗师，其思想经由启蒙运动播散于大西洋两岸。
          </p>
        </div>
        <ol class="timeline">
          <li v-for="item in timeline" :key="item.year">
            <span class="t-year">{{ item.year }}</span>
            <span class="t-text">{{ item.text }}</span>
          </li>
        </ol>
      </div>
    </section>

    <div class="ornament container-narrow">
      <span class="diamond">❧</span>
    </div>

    <!-- 学术成就 -->
    <section class="container works">
      <div class="section-head">
        <p class="eyebrow">学 术 成 就</p>
        <h2>传世著述</h2>
      </div>
      <div class="works-grid">
        <article v-for="w in works" :key="w.title" class="work-card panel">
          <p class="work-year">{{ w.year }}</p>
          <h3 class="work-title">{{ w.title }}</h3>
          <p class="work-zh">{{ w.zh }}</p>
          <p class="work-desc muted">{{ w.desc }}</p>
        </article>
      </div>
    </section>

    <!-- 平台简介 -->
    <section class="platform">
      <div class="container-narrow platform-inner">
        <div class="ornament"><span class="diamond">✦</span></div>
        <h2>关于本平台</h2>
        <p class="muted">
          本平台面向数字人文研究，汇集洛克手稿的高清影像与权威转写，
          并借助 Agnes 智能识别，将难以辨读的十七世纪手写体转为可检索的文本。
          学者可在专属工作区中整理、上传与识别自己的手稿材料，
          让沉睡于纸页间的思想重获流传。
        </p>
        <div class="hero-actions">
          <RouterLink to="/register" class="btn btn-gold">注册以开始研究</RouterLink>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.hero {
  padding: 5rem 0 3rem;
}
.hero-inner {
  display: grid;
  grid-template-columns: 1.15fr 0.85fr;
  gap: 3.5rem;
  align-items: center;
}
.hero-text {
  text-align: left;
}
.hero-portrait {
  margin: 0;
  text-align: center;
}
.portrait-frame {
  position: relative;
  padding: 14px;
  background:
    linear-gradient(145deg, #6f5527, #a8802f 45%, #6f5527);
  box-shadow: 0 14px 40px rgba(52, 40, 22, 0.35);
}
.portrait-frame::after {
  content: '';
  position: absolute;
  inset: 8px;
  border: 1px solid rgba(251, 246, 234, 0.35);
  pointer-events: none;
}
.portrait-frame img {
  display: block;
  width: 100%;
  border: 1px solid rgba(34, 28, 20, 0.4);
  filter: sepia(0.08);
}
.hero-portrait figcaption {
  margin-top: 1rem;
  font-family: var(--serif-cjk);
  font-size: 0.78rem;
  letter-spacing: 0.24em;
  color: var(--ink-faint);
}
.hero-title {
  font-size: clamp(3rem, 8vw, 5.4rem);
  font-weight: 600;
  letter-spacing: 0.02em;
  margin: 0.4rem 0 0;
  font-family: var(--serif-cjk);
}
.hero-latin {
  font-family: var(--serif-latin);
  font-style: italic;
  font-size: 1.5rem;
  color: var(--gold-deep);
  letter-spacing: 0.1em;
  margin: 0.2rem 0 1.6rem;
}
.hero-lede {
  max-width: 560px;
  margin: 0 0 2rem;
  font-size: 1.15rem;
  color: var(--ink-soft);
}
.hero-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}
.hero-quote {
  margin-top: 3.5rem;
  text-align: center;
}
.hero-quote blockquote {
  font-family: var(--serif-latin);
  font-style: italic;
  font-size: 1.35rem;
  color: var(--ink-soft);
  border: none;
  margin: 0;
  padding: 0;
  line-height: 1.6;
}
.hero-quote cite {
  display: block;
  font-size: 0.9rem;
  color: var(--ink-faint);
  margin-top: 0.8rem;
  font-style: normal;
  letter-spacing: 0.08em;
}

.section-head {
  text-align: center;
  margin-bottom: 3rem;
}
.section-head h2 {
  font-size: 2.4rem;
  font-family: var(--serif-cjk);
}

.life-grid {
  display: grid;
  grid-template-columns: 1.1fr 1fr;
  gap: 4rem;
}
.life-prose p {
  font-size: 1.08rem;
  color: var(--ink-soft);
}
.timeline {
  list-style: none;
  margin: 0;
  padding: 0;
  border-left: 1px solid var(--line);
}
.timeline li {
  position: relative;
  padding: 0 0 1.5rem 1.8rem;
}
.timeline li::before {
  content: '';
  position: absolute;
  left: -5px;
  top: 0.55rem;
  width: 9px;
  height: 9px;
  background: var(--gold);
  transform: rotate(45deg);
}
.t-year {
  display: inline-block;
  font-family: var(--serif-latin);
  font-weight: 600;
  color: var(--burgundy);
  font-size: 1.1rem;
  margin-right: 0.8rem;
}
.t-text {
  color: var(--ink-soft);
}

.works-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.6rem;
}
.work-card {
  padding: 2rem;
  position: relative;
}
.work-year {
  font-family: var(--serif-latin);
  font-size: 0.95rem;
  letter-spacing: 0.2em;
  color: var(--gold-deep);
  margin-bottom: 0.6rem;
}
.work-title {
  font-family: var(--serif-latin);
  font-style: italic;
  font-size: 1.4rem;
  margin-bottom: 0.2rem;
}
.work-zh {
  font-family: var(--serif-cjk);
  font-size: 1.05rem;
  color: var(--ink);
  margin-bottom: 0.8rem;
}
.work-desc {
  font-size: 0.98rem;
  margin: 0;
}

.platform {
  margin-top: 5rem;
  padding: 4rem 0 1rem;
  text-align: center;
}
.platform h2 {
  font-size: 2rem;
  font-family: var(--serif-cjk);
}
.platform p {
  font-size: 1.1rem;
  margin-bottom: 2rem;
}

@media (max-width: 820px) {
  .hero-inner {
    grid-template-columns: 1fr;
    gap: 2.5rem;
    text-align: center;
  }
  .hero-text {
    text-align: center;
    order: 2;
  }
  .hero-portrait {
    order: 1;
    max-width: 340px;
    margin: 0 auto;
  }
  .hero-lede {
    margin-left: auto;
    margin-right: auto;
  }
  .hero-actions {
    justify-content: center;
  }
  .life-grid {
    grid-template-columns: 1fr;
    gap: 2.5rem;
  }
  .works-grid {
    grid-template-columns: 1fr;
  }
}
</style>
