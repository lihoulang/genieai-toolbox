<template>
  <scroll-view class="legal-page" scroll-y>
    <view class="content">
      <text class="title">账号删除说明</text>
      <text class="meta">更新日期：2026-05-01</text>

      <text class="section-title">1. 删除入口</text>
      <text class="paragraph">你可以在“我的”页面点击“删除账号”发起注销。为避免误操作，系统会再次要求你确认。</text>

      <text class="section-title">2. 删除范围</text>
      <text class="paragraph">删除账号后，系统会清理你的账号信息、聊天记录、余额日志、AI 举报记录和登录会话。</text>

      <text class="section-title">3. 删除结果</text>
      <text class="paragraph">账号删除后无法恢复，请在操作前确认不再需要保留历史记录和剩余权益。</text>

      <text class="section-title">4. 生效时间</text>
      <text class="paragraph">当前版本采用即时删除策略。若后续接入支付、风控或合规留存机制，应在此页面同步更新延迟删除或部分字段保留规则。</text>

      <text class="section-title">5. 上线前需补齐项</text>
      <text class="paragraph">正式上架前，请将同版本账号删除说明部署为公开 HTTPS 页面，并在 Google Play Console 中填写一致的支持链接或删除说明链接。</text>
    </view>
  </scroll-view>
</template>

<script setup>
</script>

<style scoped>
.legal-page { min-height: 100vh; background-color: var(--bg-page); }
.content { padding: 20px 16px 40px; }
.title { display: block; font-size: 24px; font-weight: 700; color: var(--text-primary); margin-bottom: 8px; }
.meta { display: block; font-size: 12px; color: var(--text-tertiary); margin-bottom: 20px; }
.section-title { display: block; font-size: 16px; font-weight: 600; color: var(--text-primary); margin: 18px 0 8px; }
.paragraph { display: block; font-size: 14px; line-height: 1.7; color: var(--text-secondary); }
</style>
