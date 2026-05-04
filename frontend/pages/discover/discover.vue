<template>
  <view class="discover-page">
    <view class="topbar">
      <view class="menu-btn" hover-class="is-pressed" hover-stay-time="80" @click="goChat">
        <view class="menu-line"></view>
        <view class="menu-line"></view>
        <view class="menu-line"></view>
      </view>
      <text class="topbar-title">发现</text>
      <view class="topbar-placeholder"></view>
    </view>

    <scroll-view class="discover-scroll" scroll-y>
      <view class="hero-card">
        <view class="hero-copy">
          <text class="hero-title">探索无限可能</text>
          <text class="hero-desc">点击灵感卡片，一键体验 AI 多模态能力</text>
        </view>
        <view class="hero-ornament" aria-hidden="true">
          <view class="hero-orb hero-orb-large"></view>
          <view class="hero-orb hero-orb-small"></view>
          <view class="hero-line hero-line-top"></view>
          <view class="hero-line hero-line-bottom"></view>
        </view>
      </view>

      <scroll-view class="tab-scroll" :scroll-x="true" :enable-flex="true" show-scrollbar="false">
        <view class="tab-row">
          <view
            v-for="(tab, index) in tabs"
            :key="tab.filter"
            class="tab-pill"
            :class="{ 'tab-pill-active': activeTab === index }"
            hover-class="is-pressed"
            hover-stay-time="80"
            @click="activeTab = index"
          >
            {{ tab.label }}
          </view>
        </view>
      </scroll-view>

      <view class="card-list">
        <view
          class="idea-card"
          :class="{ 'idea-card-featured': index < 2 }"
          v-for="(card, index) in currentCards"
          :key="card.title"
          hover-class="is-pressed"
          hover-stay-time="80"
          @click="usePrompt(card.prompt)"
        >
          <view class="idea-icon-wrap" :class="{ 'idea-icon-wrap-featured': index < 2 }">
            <text class="idea-icon">{{ card.icon }}</text>
          </view>
          <view class="idea-copy">
            <text class="idea-title">{{ card.title }}</text>
            <text class="idea-desc">{{ card.desc }}</text>
          </view>
          <text class="idea-arrow">›</text>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { computed, ref } from 'vue';

const activeTab = ref(0);

const tabs = [
  { label: '全部', filter: 'all' },
  { label: '创意绘画', filter: 'art' },
  { label: '编程开发', filter: 'code' },
  { label: '学习办公', filter: 'study' },
  { label: '生活实用', filter: 'life' },
];

const allCards = [
  { icon: '</>', title: '代码助手', desc: 'AI 编程辅助', cat: 'code', prompt: '用 Python 写一个快速排序算法，附详细注释' },
  { icon: '✦', title: 'AI 绘画', desc: '文字生成图片', cat: 'art', prompt: '画一幅日落时分的海边灯塔，油画风格，暖色调' },
  { icon: '▤', title: '作文批改', desc: '逐段点评', cat: 'study', prompt: '请帮我批改以下作文，逐段点评并给出改进建议' },
  { icon: '✈', title: '旅行规划', desc: '定制行程', cat: 'life', prompt: '帮我规划一个 5 天 4 晚的旅行攻略，包含美食和景点' },
  { icon: '∑', title: 'Excel 公式', desc: '一句话搞定', cat: 'code', prompt: '我需要一个 Excel 公式来查找重复值并统计出现次数' },
  { icon: '√', title: '数学解题', desc: '详细推导', cat: 'study', prompt: '请详细解答：求不定积分 ∫x²·e^x dx' },
  { icon: '⌕', title: '热点速递', desc: '联网搜索', cat: 'life', prompt: '搜索今天最重要的 5 条新闻，每条用一句话总结' },
  { icon: '⌂', title: '室内设计', desc: 'AI 效果图', cat: 'art', prompt: '画一张现代简约风格的客厅效果图，大落地窗，自然光照' },
];

const currentCards = computed(() => {
  const filter = tabs[activeTab.value].filter;
  return filter === 'all' ? allCards : allCards.filter((card) => card.cat === filter);
});

const usePrompt = (text) => {
  uni.setStorageSync('pending_prompt', text);
  uni.switchTab({ url: '/pages/index/index' });
};

const goChat = () => {
  uni.switchTab({ url: '/pages/index/index' });
};
</script>

<style scoped>
.discover-page {
  position: fixed;
  inset: 0;
  background:
    radial-gradient(circle at top left, rgba(224, 231, 255, 0.72), transparent 24%),
    linear-gradient(180deg, #f9fbff 0%, var(--color-page) 22%, var(--color-page) 100%);
  display: flex;
  flex-direction: column;
  padding-bottom: calc(56px + var(--safe-area-bottom, 0px));
}

.topbar {
  height: calc(72px + var(--safe-area-top, 0px));
  padding: calc(12px + var(--safe-area-top, 0px)) var(--space-16) 8px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(255, 255, 255, 0.92);
  border-bottom: 1px solid rgba(224, 231, 255, 0.7);
  backdrop-filter: blur(18px);
  flex-shrink: 0;
}

.menu-btn,
.topbar-placeholder {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
}

.menu-btn {
  background: rgba(224, 231, 255, 0.42);
  flex-direction: column;
  gap: var(--space-4);
  transition: transform var(--motion-fast), opacity var(--motion-fast), background-color var(--motion-base);
}

.menu-btn:active {
  background: rgba(224, 231, 255, 0.82);
}

.menu-line {
  width: 16px;
  height: 2px;
  border-radius: 999px;
  background: var(--color-text-secondary);
}

.topbar-title {
  font-size: 17px;
  line-height: 24px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.discover-scroll {
  flex: 1;
  min-height: 0;
  padding: var(--space-16) var(--space-16) calc(var(--space-24) + var(--safe-area-bottom, 0px));
}

.hero-card {
  position: relative;
  overflow: hidden;
  min-height: 144px;
  padding: var(--space-24);
  border-radius: var(--radius-lg);
  background: var(--color-primary-gradient);
  box-shadow: var(--shadow-raised);
  border: 1px solid rgba(255, 255, 255, 0.18);
}

.hero-copy {
  position: relative;
  z-index: 1;
  max-width: 70%;
}

.hero-title {
  display: block;
  color: var(--color-text-inverse);
  font-size: 20px;
  line-height: 28px;
  font-weight: 700;
}

.hero-desc {
  display: block;
  margin-top: var(--space-8);
  color: rgba(255, 255, 255, 0.9);
  font-size: 13px;
  line-height: 18px;
}

.hero-ornament {
  position: absolute;
  right: -8px;
  top: 10px;
  width: 120px;
  height: 120px;
  opacity: 0.9;
}

.hero-orb {
  position: absolute;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.24);
}

.hero-orb-large {
  right: 18px;
  top: 4px;
  width: 80px;
  height: 80px;
}

.hero-orb-small {
  right: 56px;
  top: 42px;
  width: 36px;
  height: 36px;
  background: rgba(255, 255, 255, 0.12);
}

.hero-line {
  position: absolute;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.18);
}

.hero-line-top {
  right: 8px;
  top: 34px;
  width: 76px;
  height: 1px;
  transform: rotate(-25deg);
}

.hero-line-bottom {
  right: 18px;
  top: 70px;
  width: 90px;
  height: 1px;
  transform: rotate(18deg);
}

.tab-scroll {
  margin: var(--space-16) -16px 0;
  white-space: nowrap;
}

.tab-scroll ::-webkit-scrollbar {
  display: none;
  width: 0;
  height: 0;
}

.tab-row {
  display: inline-flex;
  gap: var(--space-8);
  padding: 0 var(--space-16);
}

.tab-pill {
  min-width: 72px;
  height: 40px;
  padding: 0 var(--space-16);
  border-radius: var(--radius-pill);
  background: rgba(243, 244, 246, 0.96);
  color: var(--color-text-secondary);
  font-size: 15px;
  line-height: 40px;
  text-align: center;
  border: 1px solid transparent;
  transition: transform var(--motion-fast), opacity var(--motion-fast), background-color var(--motion-base), color var(--motion-base), box-shadow var(--motion-base), border-color var(--motion-base);
}

.tab-pill-active {
  background: var(--color-primary);
  color: var(--color-text-inverse);
  box-shadow: var(--shadow-card);
}

.card-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-16);
  margin-top: var(--space-16);
  padding-bottom: var(--space-8);
}

.idea-card {
  display: flex;
  align-items: center;
  gap: var(--space-12);
  min-height: 88px;
  padding: var(--space-16);
  background: rgba(255, 255, 255, 0.98);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-card);
  border: 1px solid rgba(255, 255, 255, 0.86);
  transition: transform var(--motion-fast), opacity var(--motion-fast), box-shadow var(--motion-base), background-color var(--motion-base);
}

.idea-card-featured {
  border: 1px solid var(--color-primary-soft);
  box-shadow: var(--shadow-raised);
}

.idea-icon-wrap {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  background: rgba(79, 70, 229, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.idea-icon-wrap-featured {
  background: linear-gradient(135deg, rgba(79, 70, 229, 0.16) 0%, rgba(129, 140, 248, 0.28) 100%);
}

.idea-icon {
  color: var(--color-primary);
  font-size: 20px;
  font-weight: 700;
}

.idea-copy {
  flex: 1;
  min-width: 0;
}

.idea-title {
  display: block;
  font-size: 17px;
  line-height: 24px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.idea-desc {
  display: block;
  margin-top: var(--space-4);
  font-size: 13px;
  line-height: 18px;
  color: var(--color-text-tertiary);
}

.idea-arrow {
  color: var(--color-border);
  font-size: 18px;
  line-height: 1;
  transition: color var(--motion-base);
}

.idea-card:active {
  box-shadow: var(--shadow-raised);
}

.idea-card:active .idea-arrow,
.idea-card-featured .idea-arrow {
  color: var(--color-primary);
}
</style>
