<template>
  <view class="discover-page">
    <view class="topbar">
      <view class="menu-btn" @click="goChat">
        <view class="menu-line"></view>
        <view class="menu-line"></view>
        <view class="menu-line"></view>
      </view>
      <text class="topbar-title">发现</text>
      <view class="topbar-placeholder"></view>
    </view>

    <scroll-view class="discover-scroll" scroll-y>
      <view class="hero-card">
        <text class="hero-title">探索无限可能</text>
        <text class="hero-desc">点击灵感卡片，一键体验 AI 多模态能力</text>
      </view>

      <scroll-view class="tab-scroll" :scroll-x="true" :enable-flex="true" show-scrollbar="false" @scroll="handleTabScroll">
        <view class="tab-row">
          <view
            v-for="(tab, index) in tabs"
            :key="tab.filter"
            class="tab-pill"
            :class="{ 'tab-pill-active': activeTab === index }"
            @click="activeTab = index"
          >
            {{ tab.label }}
          </view>
        </view>
      </scroll-view>
      <view class="tab-indicator-track">
        <view class="tab-indicator-thumb" :style="indicatorStyle"></view>
      </view>

      <view class="card-list">
        <view class="idea-card" v-for="card in currentCards" :key="card.title" @click="usePrompt(card.prompt)">
          <view class="idea-icon-wrap">
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
import { onReady } from '@dcloudio/uni-app';

const activeTab = ref(0);
const tabMaxScrollLeft = ref(0);
const indicatorOffset = ref(0);
const indicatorWidth = ref(68);
const indicatorTrackWidth = ref(128);

const tabs = [
  { label: '全部', filter: 'all' },
  { label: '创意绘画', filter: 'art' },
  { label: '编程开发', filter: 'code' },
  { label: '学习办公', filter: 'study' },
  { label: '生活实用', filter: 'life' },
];

const allCards = [
  { icon: '</>', title: '代码助手', desc: 'AI 编程辅助', cat: 'code', prompt: '用 Python 写一个快速排序算法，附详细注释' },
  { icon: '◌', title: 'AI 绘画', desc: '文字生成图片', cat: 'art', prompt: '画一幅日落时分的海边灯塔，油画风格，暖色调' },
  { icon: '▤', title: '作文批改', desc: '逐段点评', cat: 'study', prompt: '请帮我批改以下作文，逐段点评并给出改进建议' },
  { icon: '✈', title: '旅行规划', desc: '定制行程', cat: 'life', prompt: '帮我规划一个 5 天 4 晚的旅行攻略，包含美食和景点' },
  { icon: '▦', title: 'Excel 公式', desc: '一句话搞定', cat: 'code', prompt: '我需要一个 Excel 公式来查找重复值并统计出现次数' },
  { icon: '∑', title: '数学解题', desc: '详细推导', cat: 'study', prompt: '请详细解答：求不定积分 ∫x²·e^x dx' },
  { icon: '⌕', title: '热点速递', desc: '联网搜索', cat: 'life', prompt: '搜索今天最重要的 5 条新闻，每条用一句话总结' },
  { icon: '⌂', title: '室内设计', desc: 'AI 效果图', cat: 'art', prompt: '画一张现代简约风格的客厅效果图，大落地窗，自然光照' },
];

const currentCards = computed(() => {
  const filter = tabs[activeTab.value].filter;
  return filter === 'all' ? allCards : allCards.filter((card) => card.cat === filter);
});

const indicatorStyle = computed(() => ({
  width: `${indicatorWidth.value}px`,
  transform: `translateX(${indicatorOffset.value}px)`,
}));

const syncIndicator = (scrollLeft = 0) => {
  const maxOffset = Math.max(indicatorTrackWidth.value - indicatorWidth.value, 0);
  if (tabMaxScrollLeft.value <= 0) {
    indicatorOffset.value = 0;
    return;
  }
  const ratio = Math.min(Math.max(scrollLeft / tabMaxScrollLeft.value, 0), 1);
  indicatorOffset.value = ratio * maxOffset;
};

const measureTabMetrics = () => {
  const query = uni.createSelectorQuery();
  query.select('.tab-scroll').boundingClientRect();
  query.select('.tab-indicator-track').boundingClientRect();
  query.selectAll('.tab-pill').boundingClientRect();
  query.exec((res) => {
    const scrollRect = res?.[0];
    const trackRect = res?.[1];
    const pillRects = res?.[2] || [];
    if (!scrollRect || pillRects.length === 0) return;

    indicatorTrackWidth.value = trackRect?.width || scrollRect.width;

    const gap = 8;
    const rightPadding = 14;
    const contentWidth =
      pillRects.reduce((sum, rect) => sum + rect.width, 0) +
      gap * Math.max(pillRects.length - 1, 0) +
      rightPadding;

    tabMaxScrollLeft.value = Math.max(contentWidth - scrollRect.width, 0);

    if (contentWidth <= scrollRect.width) {
      indicatorWidth.value = 68;
      indicatorOffset.value = 0;
      return;
    }

    const rawWidth = (scrollRect.width / contentWidth) * indicatorTrackWidth.value;
    indicatorWidth.value = Math.max(64, Math.min(rawWidth, 74));
    syncIndicator(0);
  });
};

const handleTabScroll = (event) => {
  syncIndicator(event?.detail?.scrollLeft || 0);
};

const usePrompt = (text) => {
  uni.setStorageSync('pending_prompt', text);
  uni.switchTab({ url: '/pages/index/index' });
};

const goChat = () => {
  uni.switchTab({ url: '/pages/index/index' });
};

onReady(() => {
  measureTabMetrics();
});
</script>

<style scoped>
.discover-page {
  position: fixed;
  inset: 0;
  background: #fff;
  display: flex;
  flex-direction: column;
  padding-bottom: calc(56px + var(--safe-area-bottom, 0px));
}

.topbar {
  height: calc(60px + var(--safe-area-top, 0px));
  padding: calc(8px + var(--safe-area-top, 0px)) 14px 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #eceff4;
  flex-shrink: 0;
}

.menu-btn,
.topbar-placeholder {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.menu-btn {
  flex-direction: column;
  gap: 4px;
}

.menu-line {
  width: 15px;
  height: 2px;
  border-radius: 2px;
  background: #61697b;
}

.topbar-title {
  font-size: 17px;
  font-weight: 600;
  color: #202634;
}

.discover-scroll {
  flex: 1;
  min-height: 0;
  padding: 16px 14px 24px;
  background: #fff;
}

.hero-card {
  min-height: 100px;
  padding: 24px 22px 20px;
  border-radius: 18px;
  background: linear-gradient(135deg, #6670e8 0%, #5d62c9 100%);
  box-shadow: none;
}

.hero-title {
  display: block;
  color: #fff;
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 8px;
}

.hero-desc {
  display: block;
  color: rgba(255, 255, 255, 0.86);
  font-size: 13px;
  line-height: 1.55;
}

.tab-scroll {
  margin-top: 18px;
  white-space: nowrap;
  width: 100%;
  overflow: hidden;
}

.tab-scroll ::-webkit-scrollbar {
  display: none;
  width: 0;
  height: 0;
}

.tab-row {
  display: inline-block;
  white-space: nowrap;
  padding-right: 14px;
}

.tab-pill {
  display: inline-block;
  height: 34px;
  padding: 0 18px;
  margin-right: 8px;
  border-radius: 999px;
  border: 1px solid #d8dde7;
  background: #fff;
  color: #596275;
  font-size: 13px;
  line-height: 34px;
  text-align: center;
  vertical-align: top;
}

.tab-pill:last-child {
  margin-right: 0;
}

.tab-pill-active {
  border-color: transparent;
  background: linear-gradient(135deg, #6670e8 0%, #5d62c9 100%);
  color: #fff;
  box-shadow: none;
}

.tab-indicator-track {
  width: 100%;
  height: 5px;
  border-radius: 999px;
  background: #d8dde6;
  margin: 8px 0 0;
  position: relative;
  overflow: hidden;
}

.tab-indicator-thumb {
  position: absolute;
  left: 0;
  top: 0;
  width: 48px;
  height: 100%;
  border-radius: 999px;
  background: #b8bec9;
  transition: transform 0.05s linear, width 0.2s ease;
}

.card-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 16px;
  padding-bottom: 12px;
}

.idea-card {
  display: flex;
  align-items: center;
  gap: 14px;
  min-height: 74px;
  padding: 16px 16px;
  background: #fff;
  border: 1px solid #dfe4ee;
  border-radius: 15px;
  box-shadow: none;
}

.idea-icon-wrap {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  background: #fff;
  border: 1px solid #f2f4f8;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.idea-icon {
  color: #6670e8;
  font-size: 15px;
  font-weight: 600;
}

.idea-copy {
  flex: 1;
  min-width: 0;
}

.idea-title {
  display: block;
  font-size: 15px;
  font-weight: 600;
  color: #232939;
  margin-bottom: 3px;
}

.idea-desc {
  display: block;
  font-size: 12px;
  color: #9ca4b2;
}

.idea-arrow {
  color: #aab1be;
  font-size: 20px;
  line-height: 1;
  margin-top: -1px;
}
</style>
