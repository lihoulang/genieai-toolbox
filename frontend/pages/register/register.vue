<template>
  <view class="auth-page">
    <view class="topbar">
      <view class="back-btn" @click="goLogin">‹</view>
      <view class="header-copy">
        <text class="topbar-title">注册</text>
        <text class="topbar-subtitle">创建 Genie AI Toolbox 账号</text>
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
            <text class="card-title">填写注册信息</text>
            <text class="card-subtitle">用户名至少 2 个字符，密码至少 6 位</text>
          </view>
        </view>

        <view class="form-wrapper">
          <view class="input-row">
            <text class="field-tag">账号</text>
            <input class="styled-input" type="text" v-model="username" placeholder="设置用户名" />
          </view>
          <view class="input-row">
            <text class="field-tag">密码</text>
            <input class="styled-input" type="password" v-model="password" placeholder="设置密码（至少6位）" />
          </view>
          <view class="input-row">
            <text class="field-tag">确认</text>
            <input class="styled-input" type="password" v-model="confirmPassword" placeholder="再次确认密码" />
          </view>
          <view class="input-row">
            <text class="field-tag">邀请</text>
            <input class="styled-input" type="text" v-model="inviteCode" placeholder="邀请码（选填）" maxlength="6" />
          </view>
          <view class="submit-btn" @click="handleRegister" :class="{ 'loading': isLoading }">
            {{ isLoading ? '注册中...' : '立即注册' }}
          </view>
        </view>

        <view class="login-row">
          <text class="login-copy">已有账号？</text>
          <text class="login-link" @click="goLogin">返回登录</text>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref } from 'vue';
import { API_BASE } from '../../config.js';

const username = ref('');
const password = ref('');
const confirmPassword = ref('');
const inviteCode = ref('');
const isLoading = ref(false);

const goLogin = () => {
  if (getCurrentPages().length > 1) {
    uni.navigateBack();
    return;
  }
  uni.reLaunch({ url: '/pages/login/login' });
};

const handleRegister = async () => {
  if (!username.value.trim() || username.value.trim().length < 2) {
    uni.showToast({ title: '用户名至少2个字符', icon: 'none' }); return;
  }
  if (password.value.length < 6) {
    uni.showToast({ title: '密码至少6位', icon: 'none' }); return;
  }
  if (password.value !== confirmPassword.value) {
    uni.showToast({ title: '两次密码不一致', icon: 'none' }); return;
  }
  isLoading.value = true;
  try {
    const res = await uni.request({
      url: `${API_BASE}/register`,
      method: 'POST',
      data: { username: username.value.trim(), password: password.value, invite_code: inviteCode.value.trim() }
    });
    if (res.data.code === 200) {
      uni.showToast({ title: '注册成功！', icon: 'success' });
      setTimeout(() => { goLogin(); }, 1500);
    } else {
      uni.showToast({ title: res.data.msg || '注册失败', icon: 'none' });
    }
  } catch (e) {
    uni.showToast({ title: '网络连接失败', icon: 'none' });
  } finally {
    isLoading.value = false;
  }
};
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

.back-btn,
.topbar-placeholder {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.back-btn {
  color: #61697b;
  font-size: 24px;
  line-height: 1;
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
  width: 124px;
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
  width: 78px;
  height: 78px;
  border-radius: 24px;
  background: linear-gradient(135deg, #6670e8 0%, #5d62c9 100%);
  box-shadow: 0 16px 36px rgba(102, 112, 232, 0.24);
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
  min-width: 64px;
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

.login-row {
  margin-top: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 13px;
}

.login-copy {
  color: #9aa3b3;
}

.login-link {
  color: #6670e8;
  font-weight: 600;
}
</style>
