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
            <text class="brand-letter">G</text>
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
  background: #fff;
  display: flex;
  flex-direction: column;
}

.topbar {
  height: 60px;
  padding: 8px 14px 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #eceff4;
  flex-shrink: 0;
}

.topbar-placeholder {
  width: 36px;
  height: 36px;
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
  color: #202634;
}

.topbar-subtitle {
  display: block;
  margin-top: 2px;
  font-size: 12px;
  color: #9aa3b3;
}

.auth-scroll {
  flex: 1;
  min-height: 0;
  padding: 22px 14px 24px;
  background: #fff;
}

.brand-block {
  padding: 18px 8px 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.brand-mark {
  position: relative;
  width: 118px;
  height: 118px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.brand-orbit {
  position: absolute;
  inset: 0;
  border-radius: 34px;
  border: 1px solid rgba(102, 112, 232, 0.16);
  background: linear-gradient(135deg, rgba(102, 112, 232, 0.12), rgba(93, 98, 201, 0.04));
}

.brand-orbit-a {
  transform: rotate(12deg);
}

.brand-orbit-b {
  inset: 10px;
  border-radius: 28px;
  transform: rotate(-10deg);
  border-color: rgba(102, 112, 232, 0.22);
}

.brand-core {
  position: relative;
  z-index: 1;
  width: 72px;
  height: 72px;
  border-radius: 24px;
  background: linear-gradient(135deg, #6670e8 0%, #5d62c9 100%);
  box-shadow: 0 16px 36px rgba(102, 112, 232, 0.24);
  display: flex;
  align-items: center;
  justify-content: center;
}

.brand-letter {
  color: #fff;
  font-size: 30px;
  font-weight: 800;
  letter-spacing: 1px;
}

.brand-title {
  display: block;
  margin-top: 18px;
  font-size: 22px;
  font-weight: 700;
  color: #232939;
}

.brand-subtitle {
  display: block;
  margin-top: 8px;
  font-size: 13px;
  line-height: 1.6;
  color: #97a0af;
  text-align: center;
}

.form-card {
  margin-top: 14px;
  background: #fff;
  border: 1px solid #dfe4ee;
  border-radius: 16px;
}

.form-card {
  padding: 18px 16px 16px;
}

.card-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.card-title {
  display: block;
  font-size: 18px;
  font-weight: 700;
  color: #232939;
}

.card-subtitle {
  display: block;
  margin-top: 5px;
  font-size: 12px;
  color: #98a1b0;
}

.card-badge {
  flex-shrink: 0;
  min-width: 74px;
  height: 30px;
  padding: 0 10px;
  border-radius: 999px;
  border: 1px solid #d7dcfb;
  color: #6670e8;
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
  border: 1px solid #dfe4ee;
  border-radius: 14px;
  background: #fff;
  box-shadow: none !important;
  display: flex;
  align-items: center;
  padding: 0 14px;
  gap: 12px;
}

.input-row:focus-within {
  border-color: #dfe4ee;
  background: #fff;
}

.field-tag {
  flex-shrink: 0;
  width: 38px;
  color: #8d97a8;
  font-size: 13px;
}

.styled-input {
  flex: 1;
  height: 52px;
  font-size: 15px;
  color: #232939;
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
  -webkit-text-fill-color: #232939 !important;
  caret-color: #232939;
  transition: background-color 99999s ease-in-out 0s;
}

:deep(.styled-input .uni-input-placeholder) {
  color: #a2aabd !important;
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
  -webkit-text-fill-color: #232939 !important;
  outline: none !important;
  transition: background-color 99999s ease-in-out 0s;
}

.submit-btn {
  margin-top: 4px;
  height: 50px;
  border-radius: 14px;
  background: linear-gradient(135deg, #6670e8 0%, #5d62c9 100%);
  color: #fff;
  font-size: 15px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
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
  color: #9aa3b3;
}

.register-link {
  color: #6670e8;
  font-weight: 600;
}
</style>
