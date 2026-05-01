<template>
  <scroll-view class="legal-page" scroll-y>
    <view class="content">
      <text class="title">支持</text>
      <text class="meta">更新日期：2026-05-02</text>

      <text class="section-title">1. 联系方式</text>
      <text class="paragraph">正式上架前，请在此页面补充支持邮箱、官网或工单地址，并与 Google Play Console 中填写的支持链接保持一致。</text>

      <text class="section-title">2. 常见问题</text>
      <text class="paragraph">如果登录失效，请重新登录；如果 AI 能力不可用，请先检查网络、账号余额和后端服务状态。</text>

      <text class="section-title">3. 隐私与账号</text>
      <text class="paragraph">你可以在“我的”页面查看隐私政策、账号删除说明，并发起账号删除。</text>

      <text class="section-title">4. 上线前需补齐项</text>
      <text class="paragraph">正式上架前，请将此页面内容发布为公开 HTTPS 页面，例如 support 页面，并把相同链接填入 Play Console 的支持链接字段。</text>
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
