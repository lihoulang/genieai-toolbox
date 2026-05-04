<template>
  <view class="auth-page">
    <view class="topbar">
      <view class="topbar-placeholder"></view>
      <view class="header-copy">
        <text class="topbar-title">登录</text>
        <text class="topbar-subtitle">Genie AI Toolbox</text>
      </view>
      <view class="topbar-placeholder"></view>
    </view>

    <scroll-view class="auth-scroll" scroll-y>
      <view class="brand-block">
        <view class="brand-mark">
          <view class="brand-orbit brand-orbit-a"></view>
          <view class="brand-orbit brand-orbit-b"></view>
          <view class="brand-core">
            <text class="brand-word">Genie</text>
          </view>
        </view>
        <text class="brand-title">Genie AI Toolbox</text>
      </view>

      <view class="form-card">
        <view class="card-head">
          <view>
          </view>
        </view>

        <view class="form-wrapper">
          <view class="input-row">
            <text class="field-tag">账号</text>
            <input class="styled-input" type="text" v-model="username" placeholder="请输入账号" />
          </view>
          <view class="input-row">
            <text class="field-tag">密码</text>
            <input class="styled-input" type="password" v-model="password" placeholder="请输入密码" @confirm="handleLogin" />
          </view>
          <view class="submit-btn" @click="handleLogin" :class="{ 'loading': isLoading }">
            {{ isLoading ? '请稍候...' : '立即登录' }}
          </view>
        </view>

        <view class="register-row">
          <text class="register-copy">还没有账号？</text>
          <text class="register-link" @click="goRegister">创建新账号</text>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref } from 'vue';
import { API_BASE } from '../../config.js';
import { clearAuthStorage } from '../../utils/auth.js';

const username = ref('');
const password = ref('');
const isLoading = ref(false);

const handleLogin = async () => {
  if (!username.value || !password.value) {
    uni.showToast({ title: '账号和密码不能为空', icon: 'none' });
    return;
  }
  isLoading.value = true;
  try {
    clearAuthStorage();
    const res = await uni.request({
      url: `${API_BASE}/login`,
      method: 'POST',
      data: { username: username.value, password: password.value }
    });
    if (res.data.code === 200) {
      uni.setStorageSync('user_id', res.data.user_id);
      uni.setStorageSync('username', username.value);
      uni.setStorageSync('access_token', res.data.access_token);
      uni.setStorageSync('token_expires_at', res.data.expires_at);
      uni.showToast({ title: '登录成功', icon: 'none' });
      setTimeout(() => { uni.switchTab({ url: '/pages/index/index' }); }, 800);
    } else {
      uni.showToast({ title: res.data.msg || '登录失败', icon: 'none' });
    }
  } catch (e) {
    uni.showToast({ title: '网络连接失败', icon: 'none' });
  } finally {
    isLoading.value = false;
  }
};

const goRegister = () => { uni.navigateTo({ url: '/pages/register/register' }); };
</script>

<style scoped>
.auth-page {
  position: fixed;
  inset: 0;
  background:
    radial-gradient(circle at top right, rgba(129, 140, 248, 0.18), transparent 26%),
    linear-gradient(180deg, #f9fbff 0%, var(--color-page) 20%, var(--color-page) 100%);
  display: flex;
  flex-direction: column;
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

.topbar-placeholder {
  width: 40px;
  height: 40px;
}

.header-copy {
  flex: 1;
  min-width: 0;
  text-align: center;
}

.topbar-title {
  display: block;
  font-size: 17px;
  font-weight: 600;
  line-height: 24px;
  color: var(--color-text-primary);
}

.topbar-subtitle {
  display: block;
  margin-top: 2px;
  font-size: 13px;
  color: var(--color-text-tertiary);
}

.auth-scroll {
  flex: 1;
  min-height: 0;
  padding: 24px var(--space-16) calc(var(--space-24) + var(--safe-area-bottom, 0px));
}

.brand-block {
  padding: 18px 8px 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.brand-mark {
  position: relative;
  width: 128px;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.brand-orbit {
  position: absolute;
  inset: 0;
  border-radius: 34px;
  border: 1px solid rgba(129, 140, 248, 0.18);
  background: linear-gradient(135deg, rgba(79, 70, 229, 0.08), rgba(129, 140, 248, 0.02));
}

.brand-orbit-a {
  transform: rotate(12deg);
}

.brand-orbit-b {
  inset: 10px;
  border-radius: 28px;
  transform: rotate(-10deg);
  border-color: rgba(129, 140, 248, 0.26);
}

.brand-core {
  position: relative;
  z-index: 1;
  width: 78px;
  height: 78px;
  border-radius: 24px;
  background: var(--color-primary-gradient);
  box-shadow: var(--shadow-raised);
  display: flex;
  align-items: center;
  justify-content: center;
}

.brand-word {
  color: #fff;
  font-size: 16px;
  font-weight: 800;
  letter-spacing: 0.2px;
}

.brand-title {
  display: block;
  margin-top: 18px;
  font-size: 20px;
  line-height: 28px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.brand-subtitle {
  display: block;
  margin-top: 8px;
  font-size: 13px;
  line-height: 1.6;
  color: var(--color-text-tertiary);
  text-align: center;
}

.form-card {
  margin-top: 14px;
  background: rgba(255, 255, 255, 0.98);
  border: 1px solid rgba(255, 255, 255, 0.86);
  border-radius: var(--radius-lg);
  padding: 18px 16px 16px;
  box-shadow: var(--shadow-card);
}

.card-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.card-title {
  display: block;
  font-size: 17px;
  line-height: 24px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.card-subtitle {
  display: block;
  margin-top: 5px;
  font-size: 13px;
  color: var(--color-text-tertiary);
}

.card-badge {
  flex-shrink: 0;
  min-width: 74px;
  height: 30px;
  padding: 0 10px;
  border-radius: 999px;
  border: 1px solid var(--color-primary-soft);
  color: var(--color-primary);
  font-size: 12px;
  line-height: 30px;
  text-align: center;
}

.form-wrapper {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 18px;
}

.input-row {
  min-height: 54px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: #fff;
  box-shadow: var(--shadow-card);
  display: flex;
  align-items: center;
  padding: 0 16px;
  gap: 12px;
}

.input-row:focus-within {
  border-color: var(--color-primary);
  background: #fafafa;
}

.field-tag {
  flex-shrink: 0;
  width: 38px;
  color: var(--color-text-tertiary);
  font-size: 13px;
}

.styled-input {
  flex: 1;
  height: 52px;
  font-size: 15px;
  color: var(--color-text-primary);
  background: transparent;
  border: none;
  outline: none;
  box-shadow: none !important;
  -webkit-appearance: none;
  appearance: none;
}

:deep(.styled-input .uni-input-wrapper) {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}

:deep(.styled-input .uni-input-input),
:deep(.styled-input .uni-input-input:focus),
:deep(.styled-input .uni-input-input:active),
:deep(.styled-input .uni-input-input:-webkit-autofill),
:deep(.styled-input .uni-input-input:-webkit-autofill:hover),
:deep(.styled-input .uni-input-input:-webkit-autofill:focus) {
  background: #fff !important;
  border: none !important;
  outline: none !important;
  box-shadow: none !important;
  -webkit-box-shadow: 0 0 0 1000px #fff inset !important;
  -webkit-text-fill-color: var(--color-text-primary) !important;
  caret-color: var(--color-text-primary);
  transition: background-color 99999s ease-in-out 0s;
}

:deep(.styled-input .uni-input-placeholder) {
  color: var(--color-text-tertiary) !important;
}

:deep(input),
:deep(input:focus),
:deep(input:active),
:deep(input:-webkit-autofill),
:deep(input:-webkit-autofill:hover),
:deep(input:-webkit-autofill:focus) {
  background: #fff !important;
  box-shadow: none !important;
  -webkit-box-shadow: 0 0 0 1000px #fff inset !important;
  -webkit-text-fill-color: var(--color-text-primary) !important;
  outline: none !important;
  transition: background-color 99999s ease-in-out 0s;
}

.submit-btn {
  margin-top: 4px;
  height: 50px;
  border-radius: var(--radius-sm);
  background: var(--color-primary);
  color: #fff;
  font-size: 15px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-raised);
}

.submit-btn:active {
  transform: scale(0.98);
}

.submit-btn.loading {
  opacity: 0.7;
  pointer-events: none;
}

.register-row {
  margin-top: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 13px;
}

.register-copy {
  color: var(--color-text-tertiary);
}

.register-link {
  color: var(--color-primary);
  font-weight: 600;
}
</style>
