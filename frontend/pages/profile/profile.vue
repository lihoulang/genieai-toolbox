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
          <text class="hero-tag">{{ vipActive ? `${vipName} 已开通` : 'AI Explorer' }}</text>
        </view>
      </view>

      <view class="membership-card">
        <view class="membership-head">
          <view>
            <text class="membership-eyebrow">Member Access</text>
            <text class="membership-title">{{ vipActive ? vipName : '未开通会员' }}</text>
            <text class="membership-subtitle">{{ membershipSubtitle }}</text>
          </view>
          <view class="membership-badge" :class="vipActive ? 'membership-badge-active' : 'membership-badge-idle'">
            {{ vipActive ? 'VIP' : 'FREE' }}
          </view>
        </view>

        <view class="membership-benefits">
          <view class="membership-benefit" v-for="item in membershipBenefits" :key="item">
            {{ item }}
          </view>
        </view>

        <view class="membership-actions">
          <view class="membership-btn membership-btn-primary" hover-class="is-pressed" hover-stay-time="80" @click="handleRedeemMembership">
            {{ vipActive ? '续期会员' : '兑换会员' }}
          </view>
          <view
            class="membership-btn membership-btn-secondary"
            :class="{ 'membership-btn-disabled': !canExportHistory }"
            hover-class="is-pressed"
            hover-stay-time="80"
            @click="handleExportHistory"
          >
            导出对话
          </view>
        </view>
      </view>

      <view class="play-card">
        <view class="play-card-head">
          <view>
            <text class="play-card-eyebrow">Google Play Billing</text>
            <text class="play-card-title">开通 Google Play 会员</text>
          </view>
          <text class="play-card-state" :class="playSupported ? 'play-card-state-ready' : 'play-card-state-idle'">
            {{ playSupported ? 'READY' : 'WAITING' }}
          </text>
        </view>

        <text class="play-card-desc">{{ playStatusText }}</text>

        <view v-if="googlePlayPlans.length" class="play-plan-list">
          <view class="play-plan" v-for="plan in googlePlayPlans" :key="plan.planKey">
            <view class="play-plan-copy">
              <text class="play-plan-title">{{ plan.label }}</text>
              <text class="play-plan-subtitle">{{ plan.description }}</text>
            </view>
            <view class="play-plan-side">
              <text class="play-plan-price">{{ plan.priceText }}</text>
              <view
                class="play-plan-btn"
                :class="{ 'play-plan-btn-disabled': !playSupported || !plan.offerToken || playPurchasingPlanKey === plan.planKey }"
                hover-class="is-pressed"
                hover-stay-time="80"
                @click="handleGooglePlayPurchase(plan)"
              >
                {{ playPurchasingPlanKey === plan.planKey ? '处理中' : '开通' }}
              </view>
            </view>
          </view>
        </view>

        <view v-else class="play-empty">
          {{ playProductsLoading ? '正在加载 Google Play 商品...' : '当前还没有可展示的 Google Play 会员商品' }}
        </view>

        <view class="play-actions">
          <view class="play-action-btn" hover-class="is-pressed" hover-stay-time="80" @click="refreshGooglePlayProducts">
            刷新商品
          </view>
          <view class="play-action-btn" hover-class="is-pressed" hover-stay-time="80" @click="handleRestoreGooglePlayMembership">
            恢复购买
          </view>
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
import {
  getGooglePlayBillingStatus,
  launchGooglePlaySubscription,
  queryGooglePlayActiveSubscriptions,
  queryGooglePlaySubscriptions,
} from '../../utils/googlePlayBilling.js';
import { openExternalUrl } from '../../utils/external.js';

const userId = ref(null);
const username = ref('');
const nickname = ref('');
const balance = ref(0);
const hasSignedToday = ref(false);
const vipActive = ref(false);
const vipName = ref('普通用户');
const vipUntil = ref('');
const pinLimit = ref(3);
const canExportHistory = ref(false);
const isDark = ref(!!uni.getStorageSync('dark_mode'));
const showBalanceLogs = ref(false);
const balanceLogs = ref([]);
const playSupported = ref(false);
const playStatusText = ref('Google Play 会员购买仅支持 Android App');
const playProductsLoading = ref(false);
const playPurchasingPlanKey = ref('');
const playPackageName = ref('');
const playBackendProducts = ref([]);
const playNativeProducts = ref([]);

const displayName = computed(() => nickname.value || username.value || 'User');
const membershipSubtitle = computed(() => {
  if (!vipActive.value) return `免费版当前最多置顶 ${pinLimit.value} 个会话`;
  return `有效期至 ${vipUntil.value || '未设置'}`;
});
const membershipBenefits = computed(() => {
  if (vipActive.value) {
    return ['对话导出', `置顶上限 ${pinLimit.value} 个`, '会员身份标识'];
  }
  return [`免费版最多置顶 ${pinLimit.value} 个会话`, '会员可导出对话', '会员身份标识'];
});
const googlePlayPlans = computed(() => {
  return playBackendProducts.value.map((item) => {
    const rawKey = String(item.product_id || '');
    const [productId, basePlanId = ''] = rawKey.split(':');
    const nativeDetail = playNativeProducts.value.find((detail) => {
      if (detail.productId !== productId) return false;
      if (basePlanId && detail.basePlanId && detail.basePlanId !== basePlanId) return false;
      return true;
    });
    return {
      planKey: basePlanId ? `${productId}:${basePlanId}` : productId,
      productId,
      basePlanId,
      label: item.label || productId,
      description: nativeDetail?.description || 'Google Play 自动开通，到期随订阅同步',
      priceText: nativeDetail?.price || '待加载价格',
      offerToken: nativeDetail?.offerToken || '',
    };
  });
});

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
      vipActive.value = !!res.data.vip_active;
      vipName.value = res.data.vip_name || '普通用户';
      vipUntil.value = res.data.vip_until || '';
      pinLimit.value = Number(res.data.pin_limit || 3);
      canExportHistory.value = !!res.data.can_export_history;
    }
  } catch (e) {}
};

const fetchBalanceLogs = async () => {
  try {
    const res = await requestWithAuth({ url: `${API_BASE}/user/balance_logs/${userId.value}` });
    if (res.data.code === 200) balanceLogs.value = res.data.data;
  } catch (e) {}
};

const fetchGooglePlayProducts = async () => {
  playProductsLoading.value = true;
  try {
    const status = await getGooglePlayBillingStatus();
    playSupported.value = !!status.supported;
    playStatusText.value = status.message || (status.supported ? 'Google Play 已就绪，可直接开通会员' : 'Google Play 当前不可用');

    const resp = await requestWithAuth({ url: `${API_BASE}/billing/google-play/products` });
    if (resp.data.code !== 200) {
      playBackendProducts.value = [];
      playNativeProducts.value = [];
      playStatusText.value = '未能获取会员商品配置';
      return;
    }

    playPackageName.value = resp.data.package_name || '';
    playBackendProducts.value = Array.isArray(resp.data.products) ? resp.data.products : [];
    if (!playSupported.value || playBackendProducts.value.length === 0) {
      playNativeProducts.value = [];
      return;
    }

    const uniqueProductIds = [...new Set(playBackendProducts.value.map((item) => String(item.product_id || '').split(':')[0]).filter(Boolean))];
    playNativeProducts.value = await queryGooglePlaySubscriptions(uniqueProductIds);
    if (playNativeProducts.value.length > 0) {
      playStatusText.value = 'Google Play 商品已加载，购买后会自动开通会员';
    } else {
      playStatusText.value = 'Google Play 已连接，但暂未返回可售商品';
    }
  } catch (e) {
    playNativeProducts.value = [];
    playStatusText.value = e?.message || 'Google Play 商品加载失败';
  } finally {
    playProductsLoading.value = false;
  }
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

const handleRedeemMembership = () => {
  uni.showModal({
    title: vipActive.value ? '续期会员' : '兑换会员',
    editable: true,
    placeholderText: '输入兑换码，例如 DEMO30',
    confirmText: '确认',
    success: async (res) => {
      const code = String(res.content || '').trim();
      if (!res.confirm || !code) return;
      try {
        const resp = await requestWithAuth({
          url: `${API_BASE}/membership/redeem/${userId.value}`,
          method: 'POST',
          data: { code },
        });
        if (resp.data.code === 200) {
          uni.showToast({ title: resp.data.msg, icon: 'none' });
          fetchUserInfo();
        } else {
          uni.showToast({ title: resp.data.msg || '兑换失败', icon: 'none' });
        }
      } catch (e) {
        uni.showToast({ title: '兑换失败', icon: 'none' });
      }
    },
  });
};

const handleExportHistory = async () => {
  if (!canExportHistory.value) {
    uni.showToast({ title: '导出为会员权益', icon: 'none' });
    return;
  }
  try {
    const resp = await requestWithAuth({ url: `${API_BASE}/history/export/${userId.value}` });
    if (resp.data.code !== 200) {
      uni.showToast({ title: resp.data.msg || '导出失败', icon: 'none' });
      return;
    }
    const payload = JSON.stringify(resp.data.data, null, 2);
    uni.setClipboardData({
      data: payload,
      success: () => uni.showToast({ title: '已复制导出内容', icon: 'none' }),
      fail: () => uni.showToast({ title: '导出失败', icon: 'none' }),
    });
  } catch (e) {
    uni.showToast({ title: '导出失败', icon: 'none' });
  }
};

const refreshGooglePlayProducts = async () => {
  await fetchGooglePlayProducts();
};

const handleGooglePlayPurchase = async (plan) => {
  if (!playSupported.value) {
    uni.showToast({ title: playStatusText.value || 'Google Play 当前不可用', icon: 'none' });
    return;
  }
  if (!plan.offerToken) {
    uni.showToast({ title: '商品信息未准备好，请先刷新商品', icon: 'none' });
    return;
  }
  playPurchasingPlanKey.value = plan.planKey;
  try {
    const purchase = await launchGooglePlaySubscription({
      productId: plan.productId,
      offerToken: plan.offerToken,
    });
    const resp = await requestWithAuth({
      url: `${API_BASE}/billing/google-play/subscription/verify/${userId.value}`,
      method: 'POST',
      data: {
        purchase_token: purchase.purchaseToken,
        product_id: purchase.productId || plan.productId,
        package_name: purchase.packageName || playPackageName.value,
      },
    });
    if (resp.data.code === 200) {
      uni.showToast({ title: resp.data.msg || '会员已开通', icon: 'none' });
      await fetchUserInfo();
    } else {
      uni.showToast({ title: resp.data.msg || '校验失败', icon: 'none' });
    }
  } catch (e) {
    uni.showToast({ title: e?.message || '购买失败', icon: 'none' });
  } finally {
    playPurchasingPlanKey.value = '';
  }
};

const handleRestoreGooglePlayMembership = async () => {
  if (!playSupported.value) {
    uni.showToast({ title: playStatusText.value || 'Google Play 当前不可用', icon: 'none' });
    return;
  }
  try {
    const purchases = await queryGooglePlayActiveSubscriptions();
    if (!purchases.length) {
      uni.showToast({ title: '没有可恢复的订阅', icon: 'none' });
      return;
    }
    for (const purchase of purchases) {
      await requestWithAuth({
        url: `${API_BASE}/billing/google-play/subscription/sync/${userId.value}`,
        method: 'POST',
        data: {
          purchase_token: purchase.purchaseToken,
          package_name: purchase.packageName || playPackageName.value,
        },
      });
    }
    await fetchUserInfo();
    uni.showToast({ title: '已同步 Google Play 会员', icon: 'none' });
  } catch (e) {
    uni.showToast({ title: e?.message || '恢复购买失败', icon: 'none' });
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
  fetchGooglePlayProducts();
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

.membership-card {
  margin: -48px var(--space-16) var(--space-16);
  padding: var(--space-16);
  background:
    linear-gradient(135deg, rgba(14, 116, 144, 0.96), rgba(8, 145, 178, 0.9)),
    var(--color-surface);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-raised);
  color: var(--color-text-inverse);
}

.membership-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-16);
}

.membership-eyebrow,
.membership-title,
.membership-subtitle {
  display: block;
}

.membership-eyebrow {
  font-size: 12px;
  line-height: 16px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: rgba(236, 254, 255, 0.82);
}

.membership-title {
  margin-top: var(--space-8);
  font-size: 21px;
  line-height: 28px;
  font-weight: 700;
}

.membership-subtitle {
  margin-top: var(--space-6);
  font-size: 13px;
  line-height: 18px;
  color: rgba(236, 254, 255, 0.9);
}

.membership-badge {
  min-width: 56px;
  padding: 8px 12px;
  border-radius: 999px;
  text-align: center;
  font-size: 12px;
  line-height: 16px;
  font-weight: 700;
}

.membership-badge-active {
  background: rgba(255, 255, 255, 0.18);
  color: #ecfeff;
}

.membership-badge-idle {
  background: rgba(255, 255, 255, 0.12);
  color: rgba(236, 254, 255, 0.88);
}

.membership-benefits {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-8);
  margin-top: var(--space-16);
}

.membership-benefit {
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.14);
  font-size: 12px;
  line-height: 16px;
  color: rgba(240, 249, 255, 0.96);
}

.membership-actions {
  display: flex;
  gap: var(--space-12);
  margin-top: var(--space-16);
}

.membership-btn {
  flex: 1;
  min-height: 42px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  line-height: 20px;
  font-weight: 600;
}

.membership-btn-primary {
  background: rgba(255, 255, 255, 0.92);
  color: #0f172a;
}

.membership-btn-secondary {
  border: 1px solid rgba(236, 254, 255, 0.42);
  color: #ecfeff;
}

.membership-btn-disabled {
  opacity: 0.54;
}

.play-card {
  margin: 0 var(--space-16) var(--space-16);
  padding: var(--space-16);
  background: rgba(255, 255, 255, 0.98);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-card);
  border: 1px solid rgba(255, 255, 255, 0.86);
}

.play-card-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-16);
}

.play-card-eyebrow,
.play-card-title,
.play-card-desc {
  display: block;
}

.play-card-eyebrow {
  font-size: 12px;
  line-height: 16px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #0f766e;
}

.play-card-title {
  margin-top: var(--space-8);
  font-size: 18px;
  line-height: 24px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.play-card-state {
  padding: 8px 12px;
  border-radius: 999px;
  font-size: 12px;
  line-height: 16px;
  font-weight: 700;
}

.play-card-state-ready {
  background: rgba(16, 185, 129, 0.12);
  color: #047857;
}

.play-card-state-idle {
  background: rgba(15, 118, 110, 0.08);
  color: #0f766e;
}

.play-card-desc {
  margin-top: var(--space-12);
  font-size: 13px;
  line-height: 18px;
  color: var(--color-text-tertiary);
}

.play-plan-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-12);
  margin-top: var(--space-16);
}

.play-plan {
  padding: 14px;
  border-radius: var(--radius-md);
  background: linear-gradient(180deg, rgba(240, 253, 250, 0.96), rgba(248, 250, 252, 0.98));
  border: 1px solid rgba(15, 118, 110, 0.12);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-16);
}

.play-plan-copy,
.play-plan-side {
  display: flex;
  flex-direction: column;
}

.play-plan-copy {
  gap: var(--space-6);
  min-width: 0;
}

.play-plan-side {
  align-items: flex-end;
  gap: var(--space-8);
  flex-shrink: 0;
}

.play-plan-title {
  font-size: 15px;
  line-height: 22px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.play-plan-subtitle {
  font-size: 12px;
  line-height: 18px;
  color: var(--color-text-tertiary);
}

.play-plan-price {
  font-size: 16px;
  line-height: 22px;
  font-weight: 700;
  color: #0f766e;
}

.play-plan-btn {
  min-width: 84px;
  min-height: 36px;
  padding: 0 14px;
  border-radius: var(--radius-sm);
  background: #0f766e;
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  line-height: 18px;
  font-weight: 600;
}

.play-plan-btn-disabled {
  opacity: 0.45;
}

.play-empty {
  margin-top: var(--space-16);
  padding: 18px var(--space-12);
  border-radius: var(--radius-md);
  background: var(--color-surface-muted);
  text-align: center;
  color: var(--color-text-tertiary);
  font-size: 13px;
  line-height: 18px;
}

.play-actions {
  display: flex;
  gap: var(--space-12);
  margin-top: var(--space-16);
}

.play-action-btn {
  flex: 1;
  min-height: 40px;
  border-radius: var(--radius-sm);
  border: 1px solid rgba(15, 118, 110, 0.16);
  background: rgba(15, 118, 110, 0.06);
  color: #0f766e;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  line-height: 18px;
  font-weight: 600;
}

.balance-card {
  margin: 0 var(--space-16) var(--space-16);
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
