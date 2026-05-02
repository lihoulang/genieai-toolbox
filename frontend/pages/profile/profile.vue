<template>
  <view class="profile-page">
    <view class="topbar">
      <view class="menu-btn" @click="goChat">
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
        <view class="balance-column">
          <text class="balance-value">{{ balance }}</text>
          <text class="balance-label">算力余额</text>
        </view>
        <view class="balance-divider"></view>
        <view class="balance-column" @click="handleSign">
          <view class="sign-pill" :class="{ 'sign-pill-disabled': hasSignedToday }">
            {{ hasSignedToday ? '今日已签' : '签到领取' }}
          </view>
          <text class="balance-label">每日福利</text>
        </view>
      </view>

      <view class="section-card compact-card" @click="showBalanceLogs = !showBalanceLogs">
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

      <view class="section-card settings-card">
        <text class="settings-title">设置</text>
        <view class="setting-row" @click="goPrivacyPolicy">
          <view class="row-left">
            <text class="row-icon">⌂</text>
            <text class="row-label">隐私政策</text>
          </view>
          <text class="row-arrow">›</text>
        </view>
        <view class="setting-row" @click="goAccountDeletion">
          <view class="row-left">
            <text class="row-icon">▤</text>
            <text class="row-label">注销说明</text>
          </view>
          <text class="row-arrow">›</text>
        </view>
        <view class="setting-row" @click="goSupportLink">
          <view class="row-left">
            <text class="row-icon">?</text>
            <text class="row-label">支持链接</text>
          </view>
          <text class="row-arrow">›</text>
        </view>
        <view class="setting-row" @click="toggleDarkMode">
          <view class="row-left">
            <text class="row-icon">◌</text>
            <text class="row-label">深色模式</text>
          </view>
          <text class="row-state">{{ isDark ? '开' : '关' }}</text>
        </view>
      </view>

      <view class="action-card danger-card" @click="handleDeleteAccount">
        <view class="row-left">
          <text class="row-icon danger-text">⊟</text>
          <text class="row-label danger-text">删除账号</text>
        </view>
      </view>

      <view class="action-card" @click="handleLogout">
        <view class="row-left">
          <text class="row-icon">⇥</text>
          <text class="row-label">退出登录</text>
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

const toggleDarkMode = () => {
  isDark.value = !isDark.value;
  if (typeof document === 'undefined') {
    if (isDark.value) {
      uni.setStorageSync('dark_mode', true);
    } else {
      uni.removeStorageSync('dark_mode');
    }
    return;
  }
  if (isDark.value) {
    document.documentElement.classList.add('dark');
    uni.setStorageSync('dark_mode', true);
  } else {
    document.documentElement.classList.remove('dark');
    uni.removeStorageSync('dark_mode');
  }
};

const goPrivacyPolicy = () => openExternalUrl(PRIVACY_POLICY_URL, '/pages/legal/privacy');
const goAccountDeletion = () => openExternalUrl(ACCOUNT_DELETION_URL, '/pages/legal/account-delete');
const goSupportLink = () => openExternalUrl(SUPPORT_URL, '/pages/legal/support');

const handleDeleteAccount = () => {
  uni.showModal({
    title: '删除账号',
    content: '删除后将清空聊天记录、余额记录和登录态，且无法恢复。确认继续？',
    confirmColor: '#fa6a67',
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
  fetchUserInfo();
  fetchBalanceLogs();
});
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  background: var(--bg-page);
}

.topbar {
  height: 60px;
  padding: 8px 14px 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid var(--border-color);
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
  font-size: 18px;
  font-weight: 600;
  color: #1f2430;
}

.profile-scroll {
  height: calc(100vh - 110px);
  padding-bottom: 20px;
}

.profile-hero {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 24px 18px 60px;
  background: linear-gradient(135deg, #6670e8 0%, #5d62c9 100%);
}

.hero-avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.18);
  color: #fff;
  font-size: 28px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hero-copy {
  min-width: 0;
}

.hero-name {
  display: block;
  color: #fff;
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 6px;
}

.hero-tag {
  display: block;
  color: rgba(255, 255, 255, 0.82);
  font-size: 13px;
}

.balance-card {
  margin: -28px 18px 18px;
  background: #fff;
  border-radius: 18px;
  border: 1px solid #dfe4ee;
  box-shadow: none;
  display: flex;
  align-items: center;
  padding: 18px 12px;
}

.balance-column {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.balance-value {
  font-size: 20px;
  line-height: 1;
  color: #222939;
  font-weight: 700;
}

.balance-label {
  font-size: 13px;
  color: #9aa3b3;
}

.balance-divider {
  width: 1px;
  height: 34px;
  background: #eceff4;
}

.sign-pill {
  min-width: 96px;
  height: 34px;
  padding: 0 16px;
  border-radius: 999px;
  border: 1px solid #d8dde7;
  background: #fff;
  color: #5f6779;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sign-pill-disabled {
  color: #5f6779;
}

.section-card,
.action-card {
  margin: 14px 18px 0;
  background: #fff;
  border: 1px solid #dfe4ee;
  border-radius: 16px;
  box-shadow: none;
}

.compact-card {
  padding: 0 16px;
}

.logs-card {
  padding: 8px 16px;
}

.settings-card {
  overflow: hidden;
}

.settings-title {
  display: block;
  padding: 16px;
  font-size: 16px;
  font-weight: 600;
  color: #232939;
  border-bottom: 1px solid #eceff4;
}

.single-row,
.setting-row,
.action-card {
  min-height: 52px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.setting-row {
  padding: 0 16px;
  border-bottom: 1px solid #eceff4;
}

.setting-row:last-child {
  border-bottom: none;
}

.action-card {
  padding: 0 16px;
}

.row-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.row-icon {
  width: 20px;
  text-align: center;
  color: #9aa3b3;
  font-size: 17px;
  font-weight: 500;
}

.accent {
  color: #6670e8;
}

.row-label {
  font-size: 15px;
  color: #232939;
}

.row-arrow,
.row-state {
  font-size: 16px;
  color: #a3acbb;
}

.danger-card {
  margin-top: 16px;
}

.danger-text {
  color: #fa6a67;
}

.log-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid #eceff4;
}

.log-item:last-child {
  border-bottom: none;
}

.log-reason {
  flex: 1;
  font-size: 14px;
  color: #232939;
  padding-right: 14px;
}

.log-amount {
  font-size: 14px;
  font-weight: 600;
}

.amount-plus {
  color: #27c93f;
}

.amount-minus {
  color: #fa6a67;
}

.empty-text {
  text-align: center;
  color: #9aa3b3;
  font-size: 13px;
  padding: 12px 0;
}
</style>
