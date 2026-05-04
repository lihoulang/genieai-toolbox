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

.back-btn,
.topbar-placeholder {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.back-btn {
  color: var(--color-text-secondary);
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
  min-width: 64px;
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

.login-row {
  margin-top: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 13px;
}

.login-copy {
  color: var(--color-text-tertiary);
}

.login-link {
  color: var(--color-primary);
  font-weight: 600;
}
</style>
