<template>
  <view class="profile-page">
    <view class="topbar">
      <view class="menu-btn" hover-class="is-pressed" hover-stay-time="80" @click="goChat">
        <view class="menu-line"></view>
        <view class="menu-line"></view>
        <view class="menu-line"></view>
      </view>
      <text class="topbar-title">我的</text>
      <view class="topbar-placeholder"></view>
    </view>

    <scroll-view class="profile-scroll" scroll-y>
      <view class="profile-hero">
        <view class="hero-avatar">{{ displayName.charAt(0) }}</view>
        <view class="hero-copy">
          <text class="hero-name">{{ displayName }}</text>
          <text class="hero-tag">AI Explorer</text>
        </view>
      </view>

      <view class="balance-card">
        <view class="balance-copy">
          <text class="balance-value">{{ balance }}</text>
          <text class="balance-label">算力余额</text>
        </view>
        <view class="balance-action">
          <view
            class="sign-pill"
            :class="hasSignedToday ? 'sign-pill-active' : 'sign-pill-pending'"
            hover-class="is-pressed"
            hover-stay-time="80"
            @click="handleSign"
          >
            {{ hasSignedToday ? '今日已签' : '去签到' }}
          </view>
          <text class="balance-action-label">每日福利</text>
        </view>
      </view>

      <view class="section-card compact-card" hover-class="row-pressed" hover-stay-time="80" @click="showBalanceLogs = !showBalanceLogs">
        <view class="single-row">
          <view class="row-left">
            <text class="row-icon accent">⌁</text>
            <text class="row-label">算力明细</text>
          </view>
          <text class="row-arrow">{{ showBalanceLogs ? '⌃' : '›' }}</text>
        </view>
      </view>

      <view class="section-card logs-card" v-if="showBalanceLogs">
        <view v-if="balanceLogs.length === 0" class="empty-text">暂无记录</view>
        <view class="log-item" v-for="(log, index) in balanceLogs" :key="index">
          <text class="log-reason">{{ log.reason }}</text>
          <text class="log-amount" :class="log.amount > 0 ? 'amount-plus' : 'amount-minus'">
            {{ log.amount > 0 ? '+' : '' }}{{ log.amount }}
          </text>
        </view>
      </view>

      <view class="settings-card">
        <view class="setting-row" hover-class="row-pressed" hover-stay-time="80" @click="goPrivacyPolicy">
          <view class="row-left">
            <text class="row-icon">⌂</text>
            <text class="row-label">隐私政策</text>
          </view>
          <text class="row-arrow">›</text>
        </view>
        <view class="setting-row" hover-class="row-pressed" hover-stay-time="80" @click="goAccountDeletion">
          <view class="row-left">
            <text class="row-icon">▤</text>
            <text class="row-label">注销说明</text>
          </view>
          <text class="row-arrow">›</text>
        </view>
        <view class="setting-row" hover-class="row-pressed" hover-stay-time="80" @click="goSupportLink">
          <view class="row-left">
            <text class="row-icon">?</text>
            <text class="row-label">支持链接</text>
          </view>
          <text class="row-arrow">›</text>
        </view>
        <view class="setting-row setting-row-switch">
          <view class="row-left">
            <text class="row-icon">◌</text>
            <text class="row-label">深色模式</text>
          </view>
          <switch class="mode-switch" :checked="isDark" color="#4F46E5" @change.stop="toggleDarkMode" />
        </view>
      </view>

      <view class="danger-card">
        <view class="action-row" hover-class="row-pressed" hover-stay-time="80" @click="handleDeleteAccount">
          <view class="row-left">
            <text class="row-icon danger-text">⊟</text>
            <text class="row-label danger-text">删除账号</text>
          </view>
        </view>
        <view class="action-row" hover-class="row-pressed" hover-stay-time="80" @click="handleLogout">
          <view class="row-left">
            <text class="row-icon danger-text">⇥</text>
            <text class="row-label danger-text">退出登录</text>
          </view>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { computed, ref } from 'vue';
import { onShow } from '@dcloudio/uni-app';
import { ACCOUNT_DELETION_URL, API_BASE, PRIVACY_POLICY_URL, SUPPORT_URL } from '../../config.js';
import { clearAuthStorage, ensureLoggedIn, redirectToLogin, requestWithAuth } from '../../utils/auth.js';
import { openExternalUrl } from '../../utils/external.js';

const userId = ref(null);
const username = ref('');
const nickname = ref('');
const balance = ref(0);
const hasSignedToday = ref(false);
const isDark = ref(!!uni.getStorageSync('dark_mode'));
const showBalanceLogs = ref(false);
const balanceLogs = ref([]);

const displayName = computed(() => nickname.value || username.value || 'User');

const applyDarkMode = (enabled) => {
  isDark.value = enabled;
  if (typeof document === 'undefined') {
    if (enabled) {
      uni.setStorageSync('dark_mode', true);
    } else {
      uni.removeStorageSync('dark_mode');
    }
    return;
  }
  if (enabled) {
    document.documentElement.classList.add('dark');
    uni.setStorageSync('dark_mode', true);
  } else {
    document.documentElement.classList.remove('dark');
    uni.removeStorageSync('dark_mode');
  }
};

const fetchUserInfo = async () => {
  if (!userId.value) return;
  try {
    const res = await requestWithAuth({ url: `${API_BASE}/user/info/${userId.value}` });
    if (res.data.code === 200) {
      username.value = res.data.username;
      balance.value = res.data.balance;
      hasSignedToday.value = res.data.has_signed_today;
      nickname.value = res.data.nickname || '';
    }
  } catch (e) {}
};

const fetchBalanceLogs = async () => {
  try {
    const res = await requestWithAuth({ url: `${API_BASE}/user/balance_logs/${userId.value}` });
    if (res.data.code === 200) balanceLogs.value = res.data.data;
  } catch (e) {}
};

const handleSign = async () => {
  if (hasSignedToday.value) {
    uni.showToast({ title: '今天已签到', icon: 'none' });
    return;
  }
  try {
    const res = await requestWithAuth({ url: `${API_BASE}/user/sign/${userId.value}`, method: 'POST' });
    if (res.data.code === 200) {
      uni.showToast({ title: res.data.msg, icon: 'none' });
      hasSignedToday.value = true;
      fetchUserInfo();
    } else {
      uni.showToast({ title: res.data.msg, icon: 'none' });
    }
  } catch (e) {
    uni.showToast({ title: '签到失败', icon: 'none' });
  }
};

const toggleDarkMode = (event) => {
  const enabled = typeof event?.detail?.value === 'boolean' ? event.detail.value : !isDark.value;
  applyDarkMode(enabled);
};

const goPrivacyPolicy = () => openExternalUrl(PRIVACY_POLICY_URL);
const goAccountDeletion = () => openExternalUrl(ACCOUNT_DELETION_URL);
const goSupportLink = () => openExternalUrl(SUPPORT_URL);

const handleDeleteAccount = () => {
  uni.showModal({
    title: '删除账号',
    content: '删除后将清空聊天记录、余额记录和登录态，且无法恢复。确认继续？',
    confirmColor: '#EF4444',
    success: async (res) => {
      if (!res.confirm) return;
      try {
        const resp = await requestWithAuth({
          url: `${API_BASE}/user/account/${userId.value}`,
          method: 'DELETE',
        });
        if (resp.data.code === 200) {
          clearAuthStorage();
          uni.showToast({ title: '账号已删除', icon: 'none' });
          setTimeout(() => uni.reLaunch({ url: '/pages/login/login' }), 500);
        } else {
          uni.showToast({ title: resp.data.msg || '删除失败', icon: 'none' });
        }
      } catch (e) {}
    },
  });
};

const handleLogout = () => {
  uni.showModal({
    title: '退出登录',
    content: '确认退出？',
    confirmColor: '#EF4444',
    success: async (res) => {
      if (!res.confirm) return;
      try {
        await requestWithAuth({ url: `${API_BASE}/logout`, method: 'POST' });
      } catch (e) {}
      clearAuthStorage();
      uni.reLaunch({ url: '/pages/login/login' });
    },
  });
};

const goChat = () => {
  uni.switchTab({ url: '/pages/index/index' });
};

onShow(() => {
  if (!ensureLoggedIn()) return;
  userId.value = uni.getStorageSync('user_id');
  if (!userId.value) {
    redirectToLogin('请先登录');
    return;
  }
  applyDarkMode(!!uni.getStorageSync('dark_mode'));
  fetchUserInfo();
  fetchBalanceLogs();
});
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  height: 100vh;
  background:
    radial-gradient(circle at top left, rgba(224, 231, 255, 0.72), transparent 22%),
    linear-gradient(180deg, #f9fbff 0%, var(--color-page) 24%, var(--color-page) 100%);
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

.profile-scroll {
  flex: 1;
  min-height: 0;
  padding-bottom: calc(var(--space-24) + var(--safe-area-bottom, 0px));
}

.profile-hero {
  display: flex;
  align-items: center;
  gap: var(--space-16);
  padding: var(--space-24) var(--space-16) 72px;
  background: var(--color-primary-gradient);
  border-radius: 0 0 var(--radius-lg) var(--radius-lg);
  box-shadow: var(--shadow-raised);
}

.hero-avatar {
  width: 64px;
  height: 64px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.2);
  color: var(--color-text-inverse);
  font-size: 24px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.hero-copy {
  min-width: 0;
}

.hero-name {
  display: block;
  color: var(--color-text-inverse);
  font-size: 17px;
  line-height: 24px;
  font-weight: 600;
}

.hero-tag {
  display: block;
  margin-top: var(--space-4);
  color: rgba(255, 255, 255, 0.9);
  font-size: 13px;
  line-height: 18px;
}

.balance-card {
  margin: -16px var(--space-16) var(--space-16);
  padding: var(--space-16);
  background: var(--color-surface);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-raised);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-16);
}

.balance-copy,
.balance-action {
  display: flex;
  flex-direction: column;
}

.balance-copy {
  align-items: flex-start;
  gap: var(--space-4);
}

.balance-action {
  align-items: flex-end;
  gap: var(--space-8);
}

.balance-value {
  font-size: 24px;
  line-height: 28px;
  color: var(--color-text-primary);
  font-weight: 700;
}

.balance-label,
.balance-action-label {
  font-size: 13px;
  line-height: 18px;
  color: var(--color-text-tertiary);
}

.sign-pill {
  min-width: 92px;
  padding: 8px 16px;
  border-radius: var(--radius-sm);
  font-size: 13px;
  line-height: 18px;
  font-weight: 600;
  text-align: center;
  transition: transform var(--motion-fast), opacity var(--motion-fast), background-color var(--motion-base), color var(--motion-base);
}

.sign-pill-active {
  background: var(--color-primary);
  color: var(--color-text-inverse);
}

.sign-pill-pending {
  background: var(--color-primary-soft);
  color: var(--color-primary);
}

.section-card,
.settings-card,
.danger-card {
  margin: 0 var(--space-16) var(--space-16);
  background: rgba(255, 255, 255, 0.98);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-card);
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.86);
}

.compact-card {
  padding: 0 var(--space-16);
}

.logs-card {
  padding: 0 var(--space-16);
}

.single-row,
.setting-row,
.action-row {
  min-height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  transition: background-color var(--motion-fast);
}

.setting-row,
.action-row,
.log-item {
  border-bottom: 1px solid var(--color-divider);
}

.setting-row:last-child,
.action-row:last-child,
.log-item:last-child {
  border-bottom: none;
}

.row-left {
  display: flex;
  align-items: center;
  gap: var(--space-12);
  min-width: 0;
}

.row-icon {
  width: 20px;
  color: var(--color-text-tertiary);
  font-size: 17px;
  text-align: center;
  flex-shrink: 0;
}

.accent {
  color: var(--color-primary);
}

.row-label {
  font-size: 15px;
  line-height: 22px;
  color: var(--color-text-secondary);
}

.row-arrow {
  color: var(--color-border);
  font-size: 16px;
}

.setting-row {
  padding: 0 var(--space-16);
}

.setting-row-switch {
  padding-right: 10px;
}

.mode-switch {
  transform: scale(0.8);
  transform-origin: right center;
}

.danger-text {
  color: var(--color-danger);
}

.row-pressed {
  background: var(--color-surface-muted);
}

.action-row {
  padding: 0 var(--space-16);
}

.log-item {
  padding: 12px 0;
}

.log-reason {
  flex: 1;
  padding-right: var(--space-16);
  font-size: 15px;
  line-height: 22px;
  color: var(--color-text-secondary);
}

.log-amount {
  font-size: 15px;
  line-height: 22px;
  font-weight: 600;
}

.amount-plus {
  color: var(--color-success);
}

.amount-minus {
  color: var(--color-danger);
}

.empty-text {
  padding: var(--space-16) 0;
  text-align: center;
  color: var(--color-text-tertiary);
  font-size: 13px;
  line-height: 18px;
}
</style>
