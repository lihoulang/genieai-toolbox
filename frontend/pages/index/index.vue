<template>
  <view class="chat-page">
    <view class="topbar">
      <view class="menu-btn" hover-class="is-pressed" hover-stay-time="80" @click="openConversationMenu">
        <view class="menu-line"></view>
        <view class="menu-line"></view>
        <view class="menu-line"></view>
      </view>
      <view class="title-wrap" hover-class="is-pressed" hover-stay-time="80" @click="toggleModelMenu">
        <text class="topbar-title">AI Chat</text>
        <view class="topbar-model-row">
          <text class="topbar-subtitle">{{ currentModelLabel }}</text>
          <text class="topbar-model-caret" :class="{ 'topbar-model-caret-open': showModelMenu }">⌄</text>
        </view>
      </view>
      <view class="balance-pill">
        <text class="balance-icon">⚡</text>
        <text class="balance-value">{{ balance }}</text>
      </view>
    </view>

    <view v-if="showModelMenu" class="model-mask" @click="closeModelMenu"></view>
    <view v-if="showModelMenu" class="model-menu">
      <view
        v-for="item in modelOptions"
        :key="item.value"
        class="model-option"
        :class="{ 'model-option-active': currentModel === item.value }"
        hover-class="is-pressed"
        hover-stay-time="80"
        @click="selectModel(item.value)"
      >
        <view class="model-option-copy">
          <text class="model-option-title">{{ item.label }}</text>
          <text class="model-option-desc">{{ item.desc }}</text>
        </view>
        <text v-if="currentModel === item.value" class="model-option-check">✓</text>
      </view>
    </view>

    <view v-if="showHistoryPanel" class="history-mask" @click="closeConversationMenu"></view>
    <view v-if="showHistoryPanel" class="history-panel">
      <view class="history-panel-head">
        <view>
          <text class="history-panel-eyebrow">Genie AI Toolbox</text>
          <text class="history-panel-title">对话记录</text>
          <text class="history-panel-subtitle">从左侧抽屉快速切换历史会话</text>
        </view>
        <view class="history-panel-close" hover-class="is-pressed" hover-stay-time="80" @click="closeConversationMenu">×</view>
      </view>

      <view class="history-primary-btn" hover-class="is-pressed" hover-stay-time="80" @click="handleHistoryAction('new')">
        <text class="history-primary-icon">+</text>
        <text>发起新对话</text>
      </view>

      <view class="history-actions">
        <view class="history-action-btn" hover-class="is-pressed" hover-stay-time="80" @click="handleHistoryAction('refresh')">刷新列表</view>
        <view class="history-action-btn history-action-danger" hover-class="is-pressed" hover-stay-time="80" @click="handleHistoryAction('clear')">清空当前</view>
      </view>

      <text class="history-section-title">最近对话</text>

      <scroll-view class="history-list" scroll-y>
        <view
          v-for="item in conversations"
          :key="item.id"
          class="history-item"
          :class="{ 'history-item-active': activeConversationId === item.id }"
          hover-class="is-pressed"
          hover-stay-time="80"
          @click="selectConversation(item.id, true)"
        >
          <view class="history-item-copy">
            <text class="history-item-title">{{ item.title || '新对话' }}</text>
            <text class="history-item-time">{{ item.created_at || '刚刚' }}</text>
          </view>
          <view v-if="activeConversationId === item.id" class="history-item-badge">当前</view>
        </view>
        <view v-if="!conversations.length" class="history-empty">还没有历史对话</view>
      </scroll-view>
    </view>

    <scroll-view class="message-scroll" scroll-y :scroll-into-view="scrollAnchor" show-scrollbar="false">
      <view v-if="messages.length === 0" class="empty-state">
        <view class="empty-mark">AI</view>
        <text class="empty-title">从一个清晰的问题开始</text>
        <text class="empty-desc">可以直接输入，也可以点下面的灵感提示，快速体验对话、绘图和搜索能力。</text>
        <view class="empty-prompt-grid">
          <view
            v-for="prompt in starterPrompts"
            :key="prompt"
            class="empty-prompt-card"
            hover-class="is-pressed"
            hover-stay-time="80"
            @click="sendPreparedPrompt(prompt)"
          >
            {{ prompt }}
          </view>
        </view>
      </view>

      <view
        v-for="message in messages"
        :id="`message-${message.id}`"
        :key="message.id"
        class="message-row"
        :class="message.role === 'user' ? 'message-row-user' : 'message-row-ai'"
      >
        <view v-if="message.role === 'assistant'" class="ai-badge">AI</view>

        <view class="message-stack">
          <view
            class="message-bubble"
            :class="message.role === 'user' ? 'message-bubble-user' : 'message-bubble-ai'"
          >
            <image v-if="message.imageUrl" class="bubble-image" :src="message.imageUrl" mode="widthFix" />
            <image v-if="message.mediaType === 'image'" class="bubble-image" :src="message.mediaUrl" mode="widthFix" />
            <video v-if="message.mediaType === 'video'" class="bubble-video" :src="message.mediaUrl" controls></video>
            <text v-if="message.role === 'user' && message.text" class="bubble-text bubble-text-user">{{ message.text }}</text>
            <rich-text v-else-if="message.html" class="bubble-rich-text" :nodes="message.html"></rich-text>
            <text v-else-if="message.text" class="bubble-text">{{ message.text }}</text>
          </view>

          <view v-if="message.role === 'assistant' && !message.isLoading" class="bubble-action-row">
            <view class="bubble-action-btn" hover-class="is-pressed" hover-stay-time="80" @click.stop="copyMessage(message)">
              复制
            </view>
            <view
              class="bubble-action-btn"
              :class="{ 'bubble-action-btn-active': isMessageFavorited(message) }"
              hover-class="is-pressed"
              hover-stay-time="80"
              @click.stop="toggleFavoriteMessage(message)"
            >
              {{ isMessageFavorited(message) ? '已收藏' : '收藏' }}
            </view>
            <view class="bubble-action-btn" hover-class="is-pressed" hover-stay-time="80" @click.stop="shareMessage(message)">
              分享
            </view>
          </view>

          <view v-if="message.suggestions.length" class="bubble-suggestion-row">
            <view
              v-for="suggestion in message.suggestions"
              :key="suggestion"
              class="bubble-suggestion"
              hover-class="is-pressed"
              hover-stay-time="80"
              @click="sendPreparedPrompt(suggestion)"
            >
              {{ suggestion }}
            </view>
          </view>
        </view>
      </view>

      <view id="chat-bottom" class="chat-bottom-anchor"></view>
    </scroll-view>

    <view class="composer-shell">
      <view v-if="attachment" class="attachment-preview">
        <image class="attachment-preview-image" :src="attachment.preview" mode="aspectFill" />
        <text class="attachment-preview-name">已添加图片</text>
        <view class="attachment-remove" hover-class="is-pressed" hover-stay-time="80" @click="clearAttachment">×</view>
      </view>

      <view class="composer-row">
        <view class="composer-action" hover-class="is-pressed" hover-stay-time="80" @click="chooseAttachment">+</view>

        <view class="composer-input-wrap" :class="{ 'composer-input-focus': inputFocused }">
          <textarea
            v-model="draft"
            class="composer-input"
            auto-height
            :maxlength="-1"
            confirm-type="send"
            placeholder="输入消息..."
            placeholder-class="composer-placeholder"
            @focus="inputFocused = true"
            @blur="inputFocused = false"
            @confirm="sendMessage"
          />
        </view>

        <view
          class="send-btn"
          :class="{ 'send-btn-disabled': !canSend || isSending }"
          hover-class="is-pressed"
          hover-stay-time="80"
          @click="sendMessage"
        >
          <text v-if="isSending" class="send-btn-loading">…</text>
          <view v-else class="send-icon" aria-hidden="true">
            <view class="send-icon-plane"></view>
            <view class="send-icon-tail"></view>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { computed, nextTick, ref } from 'vue';
import { onShow } from '@dcloudio/uni-app';
import { API_BASE } from '../../config.js';
import { ensureLoggedIn, redirectToLogin, requestWithAuth } from '../../utils/auth.js';
import { renderMarkdown } from '../../utils/markdown.js';

const starterPrompts = [
  '帮我整理今天最重要的 5 条新闻，并解释为什么值得关注',
  '把这段报错信息逐行解释，并给出修复步骤',
  '规划一个 3 天 2 晚的周末旅行路线，偏轻松和美食',
  '写一份周报，语气专业但不生硬',
];

const modelOptions = [
  { value: 'doubao', label: 'Doubao', desc: '响应快，适合日常对话' },
  { value: 'gemini', label: 'Gemini', desc: '适合轻量多场景问答' },
];

const supportedModelValues = modelOptions.map((item) => item.value);
const storedModel = uni.getStorageSync('chat_model');
const FAVORITE_MESSAGES_STORAGE_KEY = 'favorite_assistant_messages';

const userId = ref(0);
const balance = ref(0);
const conversations = ref([]);
const activeConversationId = ref(0);
const messages = ref([]);
const draft = ref('');
const isSending = ref(false);
const scrollAnchor = ref('');
const inputFocused = ref(false);
const attachment = ref(null);
const showHistoryPanel = ref(false);
const showModelMenu = ref(false);
const currentModel = ref(supportedModelValues.includes(storedModel) ? storedModel : 'doubao');
const favoriteMessageMap = ref({});

const canSend = computed(() => Boolean(draft.value.trim() || attachment.value));
const currentModelLabel = computed(() => {
  const match = modelOptions.find((item) => item.value === currentModel.value);
  return match?.label || 'Doubao';
});

const normalizeStoredImage = (value = '') => {
  if (!value) return '';
  return value.startsWith('data:image') ? value : `data:image/jpeg;base64,${value}`;
};

const extractSuggestions = (content = '') => {
  const match = String(content).match(/@@@(.+?)@@@/);
  if (!match) return { text: String(content).trim(), suggestions: [] };
  const suggestions = match[1]
    .split('|')
    .map((item) => item.trim())
    .filter(Boolean)
    .slice(0, 3);
  return {
    text: String(content).replace(match[0], '').trim(),
    suggestions,
  };
};

const extractMedia = (content = '') => {
  const match = String(content).match(/\[(IMAGE|VIDEO):([^\]]+)\]/i);
  if (!match) {
    return { text: String(content), mediaType: '', mediaUrl: '' };
  }
  return {
    text: String(content).replace(match[0], '').trim(),
    mediaType: match[1].toLowerCase(),
    mediaUrl: match[2].trim(),
  };
};

const normalizeFavoriteStorage = (value) => {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return {};
  return value;
};

const createStableDigest = (value = '') => {
  let hash = 0;
  const source = String(value);
  for (let index = 0; index < source.length; index += 1) {
    hash = (hash * 31 + source.charCodeAt(index)) >>> 0;
  }
  return hash.toString(16);
};

const createFavoriteKey = ({ conversationId = 0, plainText = '', imageUrl = '', mediaType = '', mediaUrl = '' }) => {
  const source = [plainText, imageUrl, mediaType, mediaUrl].join('::');
  return `assistant::${conversationId || 'draft'}::${createStableDigest(source)}`;
};

const buildMessageActionText = (message) => {
  const parts = [];
  if (message.text) {
    parts.push(message.text);
  }
  if (message.imageUrl) {
    parts.push(`图片: ${message.imageUrl}`);
  }
  if (message.mediaType && message.mediaUrl) {
    parts.push(`${message.mediaType === 'video' ? '视频' : '图片'}: ${message.mediaUrl}`);
  }
  return parts.join('\n\n').trim();
};

const loadFavoriteMessages = () => {
  favoriteMessageMap.value = normalizeFavoriteStorage(uni.getStorageSync(FAVORITE_MESSAGES_STORAGE_KEY));
};

const persistFavoriteMessages = () => {
  uni.setStorageSync(FAVORITE_MESSAGES_STORAGE_KEY, favoriteMessageMap.value);
};

const isMessageFavorited = (message) => Boolean(message.favoriteKey && favoriteMessageMap.value[message.favoriteKey]);

const copyMessage = (message) => {
  const text = buildMessageActionText(message);
  if (!text) {
    uni.showToast({ title: '暂无可复制内容', icon: 'none' });
    return;
  }
  uni.setClipboardData({
    data: text,
    success: () => {
      uni.showToast({ title: '已复制', icon: 'none' });
    },
  });
};

const toggleFavoriteMessage = (message) => {
  if (!message.favoriteKey) return;
  const nextMap = { ...favoriteMessageMap.value };
  if (nextMap[message.favoriteKey]) {
    delete nextMap[message.favoriteKey];
    favoriteMessageMap.value = nextMap;
    persistFavoriteMessages();
    uni.showToast({ title: '已取消收藏', icon: 'none' });
    return;
  }
  nextMap[message.favoriteKey] = {
    key: message.favoriteKey,
    text: message.text || '',
    imageUrl: message.imageUrl || '',
    mediaType: message.mediaType || '',
    mediaUrl: message.mediaUrl || '',
    conversationId: activeConversationId.value || 0,
    savedAt: Date.now(),
  };
  favoriteMessageMap.value = nextMap;
  persistFavoriteMessages();
  uni.showToast({ title: '已收藏', icon: 'none' });
};

const shareMessage = async (message) => {
  const text = buildMessageActionText(message);
  if (!text) {
    uni.showToast({ title: '暂无可分享内容', icon: 'none' });
    return;
  }
  if (typeof navigator !== 'undefined' && typeof navigator.share === 'function') {
    try {
      await navigator.share({
        title: 'AI 回复',
        text,
      });
      return;
    } catch (error) {
      if (error?.name === 'AbortError') {
        return;
      }
    }
  }
  uni.setClipboardData({
    data: text,
    success: () => {
      uni.showToast({ title: '当前平台未接入系统分享，内容已复制', icon: 'none' });
    },
  });
};

const buildMessage = ({ role, content = '', image = '', key, conversationId = 0, isLoading = false }) => {
  const suggestionResult = extractSuggestions(content);
  const mediaResult = extractMedia(suggestionResult.text);
  const plainText = mediaResult.text.trim();
  const normalizedImage = normalizeStoredImage(image);
  return {
    id: key || `${role}-${Date.now()}-${Math.random().toString(16).slice(2, 8)}`,
    role: role === 'assistant' ? 'assistant' : 'user',
    text: plainText,
    html: role === 'assistant' && plainText ? renderMarkdown(plainText) : '',
    imageUrl: normalizedImage,
    mediaType: mediaResult.mediaType,
    mediaUrl: mediaResult.mediaUrl,
    suggestions: role === 'assistant' ? suggestionResult.suggestions : [],
    favoriteKey:
      role === 'assistant'
        ? createFavoriteKey({
            conversationId,
            plainText,
            imageUrl: normalizedImage,
            mediaType: mediaResult.mediaType,
            mediaUrl: mediaResult.mediaUrl,
          })
        : '',
    isLoading,
  };
};

const scrollToBottom = async () => {
  scrollAnchor.value = '';
  await nextTick();
  scrollAnchor.value = 'chat-bottom';
};

const syncBalance = async () => {
  if (!userId.value) return;
  const res = await requestWithAuth({ url: `${API_BASE}/user/info/${userId.value}` });
  if (res.data?.code === 200) {
    balance.value = Number(res.data.balance || 0);
  }
};

const syncConversations = async () => {
  if (!userId.value) return;
  const res = await requestWithAuth({ url: `${API_BASE}/conversations/${userId.value}` });
  if (res.data?.code !== 200) return;
  conversations.value = Array.isArray(res.data.data) ? res.data.data : [];
  if (!activeConversationId.value && conversations.value.length) {
    activeConversationId.value = conversations.value[0].id;
  }
};

const loadHistory = async (conversationId) => {
  if (!userId.value || !conversationId) {
    messages.value = [];
    await scrollToBottom();
    return;
  }
  const res = await requestWithAuth({
    url: `${API_BASE}/history/${userId.value}?conversation_id=${conversationId}&limit=100`,
  });
  if (res.data?.code !== 200) return;
  const rows = Array.isArray(res.data.data) ? res.data.data : [];
  messages.value = rows.map((item, index) =>
    buildMessage({
      role: item.role,
      content: item.content || '',
      image: item.image || '',
      key: `${conversationId}-${index}`,
      conversationId,
    }),
  );
  await scrollToBottom();
};

const createConversation = async () => {
  const res = await requestWithAuth({
    url: `${API_BASE}/conversation/create/${userId.value}`,
    method: 'POST',
  });
  const conversationId = Number(res.data?.conversation_id || 0);
  if (conversationId) {
    activeConversationId.value = conversationId;
    await syncConversations();
  }
  return conversationId;
};

const startNewConversation = async () => {
  activeConversationId.value = 0;
  messages.value = [];
  draft.value = '';
  attachment.value = null;
  showHistoryPanel.value = false;
  showModelMenu.value = false;
  await scrollToBottom();
};

const selectConversation = async (conversationId, shouldCloseMenu = false) => {
  if (!conversationId) return;
  if (shouldCloseMenu) {
    showHistoryPanel.value = false;
  }
  if (activeConversationId.value === conversationId) return;
  activeConversationId.value = conversationId;
  attachment.value = null;
  await loadHistory(conversationId);
};

const clearCurrentConversation = async () => {
  if (!activeConversationId.value) {
    messages.value = [];
    return;
  }
  uni.showModal({
    title: '清空对话',
    content: '确认清空当前会话的聊天记录？',
    confirmColor: '#EF4444',
    success: async (result) => {
      if (!result.confirm) return;
      try {
        await requestWithAuth({
          url: `${API_BASE}/clear/${userId.value}?conversation_id=${activeConversationId.value}`,
          method: 'DELETE',
        });
        messages.value = [];
      } catch (error) {}
    },
  });
};

const openConversationMenu = () => {
  showModelMenu.value = false;
  showHistoryPanel.value = !showHistoryPanel.value;
};

const closeConversationMenu = () => {
  showHistoryPanel.value = false;
};

const toggleModelMenu = () => {
  showHistoryPanel.value = false;
  showModelMenu.value = !showModelMenu.value;
};

const closeModelMenu = () => {
  showModelMenu.value = false;
};

const selectModel = (value) => {
  currentModel.value = value;
  uni.setStorageSync('chat_model', value);
  showModelMenu.value = false;
};

const handleHistoryAction = async (action) => {
  if (action === 'new') {
    await startNewConversation();
    return;
  }
  if (action === 'refresh') {
    await syncConversations();
    if (activeConversationId.value) {
      await loadHistory(activeConversationId.value);
    }
    return;
  }
  if (action === 'clear') {
    closeConversationMenu();
    clearCurrentConversation();
  }
};

const blobToDataUrl = (blob) =>
  new Promise((resolve, reject) => {
    if (typeof FileReader === 'undefined') {
      reject(new Error('FILE_READER_UNAVAILABLE'));
      return;
    }
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = () => reject(new Error('FILE_READ_FAILED'));
    reader.readAsDataURL(blob);
  });

const filePathToDataUrl = async (filePath) => {
  if (typeof uni.getFileSystemManager === 'function') {
    return await new Promise((resolve, reject) => {
      uni.getFileSystemManager().readFile({
        filePath,
        encoding: 'base64',
        success: (result) => resolve(`data:image/jpeg;base64,${result.data}`),
        fail: reject,
      });
    });
  }
  if (typeof fetch === 'function') {
    const response = await fetch(filePath);
    const blob = await response.blob();
    return await blobToDataUrl(blob);
  }
  throw new Error('FILE_API_UNSUPPORTED');
};

const chooseAttachment = () => {
  uni.chooseImage({
    count: 1,
    sizeType: ['compressed'],
    success: async (result) => {
      const filePath = result.tempFilePaths?.[0];
      if (!filePath) return;
      try {
        const base64 = await filePathToDataUrl(filePath);
        attachment.value = {
          preview: filePath,
          base64,
        };
      } catch (error) {
        uni.showToast({ title: '当前平台暂不支持附件上传', icon: 'none' });
      }
    },
  });
};

const clearAttachment = () => {
  attachment.value = null;
};

const ensureConversationReady = async () => {
  if (activeConversationId.value) return activeConversationId.value;
  return await createConversation();
};

const extractResponseText = (data) => {
  if (typeof data === 'string') return data;
  if (typeof ArrayBuffer !== 'undefined' && data instanceof ArrayBuffer && typeof TextDecoder !== 'undefined') {
    return new TextDecoder('utf-8').decode(data);
  }
  if (data && typeof data === 'object' && typeof data.data === 'string') {
    return data.data;
  }
  if (data && typeof data === 'object') {
    try {
      return JSON.stringify(data);
    } catch (error) {}
  }
  return String(data || '');
};

const replaceLoadingBubble = (message) => {
  const nextMessages = [...messages.value];
  const loadingIndex = nextMessages.findIndex((item) => item.id === 'assistant-loading');
  if (loadingIndex === -1) {
    nextMessages.push(message);
  } else {
    nextMessages.splice(loadingIndex, 1, message);
  }
  messages.value = nextMessages;
};

const sendPreparedPrompt = async (prompt) => {
  draft.value = prompt;
  await sendMessage();
};

const sendMessage = async () => {
  if (isSending.value || !canSend.value) return;
  const text = draft.value.trim();
  const imagePayload = attachment.value;
  draft.value = '';
  attachment.value = null;
  inputFocused.value = false;

  messages.value = [
    ...messages.value,
    buildMessage({
      role: 'user',
      content: text,
      image: imagePayload?.base64 || '',
      key: `user-${Date.now()}`,
    }),
    {
      id: 'assistant-loading',
      role: 'assistant',
      text: '正在思考...',
      html: '',
      imageUrl: '',
      mediaType: '',
      mediaUrl: '',
      suggestions: [],
      favoriteKey: '',
      isLoading: true,
    },
  ];
  await scrollToBottom();

  isSending.value = true;
  try {
    const conversationId = await ensureConversationReady();
    const res = await requestWithAuth({
      url: `${API_BASE}/chat`,
      method: 'POST',
      data: {
        user_id: userId.value,
        conversation_id: conversationId,
        message: text,
        image_base64: imagePayload?.base64 || '',
        model: currentModel.value,
      },
    });
    replaceLoadingBubble(
      buildMessage({
        role: 'assistant',
        content: extractResponseText(res.data),
        key: `assistant-${Date.now()}`,
        conversationId,
      }),
    );
    await Promise.all([syncBalance(), syncConversations()]);
  } catch (error) {
    replaceLoadingBubble(
      buildMessage({
        role: 'assistant',
        content: '当前请求未完成，请稍后重试。',
        key: `assistant-error-${Date.now()}`,
        conversationId: activeConversationId.value,
      }),
    );
  } finally {
    isSending.value = false;
    await scrollToBottom();
  }
};

const consumePendingPrompt = async () => {
  const prompt = uni.getStorageSync('pending_prompt');
  if (!prompt || isSending.value) return;
  uni.removeStorageSync('pending_prompt');
  await startNewConversation();
  await sendPreparedPrompt(String(prompt));
};

const syncPage = async () => {
  if (!ensureLoggedIn()) return;
  loadFavoriteMessages();
  const storedUserId = Number(uni.getStorageSync('user_id') || 0);
  if (!storedUserId) {
    redirectToLogin('请先登录');
    return;
  }
  userId.value = storedUserId;
  await Promise.all([syncBalance(), syncConversations()]);
  if (activeConversationId.value) {
    await loadHistory(activeConversationId.value);
  } else if (!conversations.value.length) {
    messages.value = [];
  }
  await consumePendingPrompt();
};

onShow(() => {
  syncPage();
});
</script>

<style scoped>
.chat-page {
  position: fixed;
  inset: 0;
  background:
    radial-gradient(circle at top right, rgba(129, 140, 248, 0.18), transparent 28%),
    linear-gradient(180deg, #f9fbff 0%, var(--color-page) 18%, var(--color-page) 100%);
  display: flex;
  flex-direction: column;
  padding-bottom: calc(56px + var(--safe-area-bottom, 0px));
}

.topbar {
  position: relative;
  z-index: 12;
  height: calc(72px + var(--safe-area-top, 0px));
  padding: calc(12px + var(--safe-area-top, 0px)) var(--space-16) 8px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(18px);
  border-bottom: 1px solid rgba(224, 231, 255, 0.7);
  flex-shrink: 0;
}

.menu-btn {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  background: rgba(224, 231, 255, 0.42);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-4);
}

.menu-line {
  width: 16px;
  height: 2px;
  border-radius: 999px;
  background: var(--color-text-secondary);
}

.title-wrap {
  flex: 1;
  min-width: 0;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  padding: 4px 0;
}

.topbar-title {
  display: block;
  color: var(--color-text-primary);
  font-size: 17px;
  line-height: 24px;
  font-weight: 600;
}

.topbar-subtitle {
  color: var(--color-text-tertiary);
  font-size: 13px;
  line-height: 18px;
}

.topbar-model-row {
  display: flex;
  align-items: center;
  gap: 4px;
}

.topbar-model-caret {
  color: var(--color-text-tertiary);
  font-size: 12px;
  line-height: 1;
  transform: translateY(1px);
}

.topbar-model-caret-open {
  transform: rotate(180deg) translateY(-1px);
}

.model-mask {
  position: absolute;
  inset: 0;
  z-index: 18;
  background: transparent;
}

.model-menu {
  position: absolute;
  top: calc(62px + var(--safe-area-top, 0px));
  left: 50%;
  z-index: 19;
  width: min(72vw, 248px);
  padding: 8px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.98);
  box-shadow: var(--shadow-floating);
  border: 1px solid rgba(224, 231, 255, 0.92);
  transform: translateX(-50%);
  animation: dropdown-slide-in 180ms ease both;
}

.model-option {
  padding: 12px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.model-option + .model-option {
  margin-top: 2px;
}

.model-option-active {
  background: rgba(224, 231, 255, 0.52);
}

.model-option-copy {
  flex: 1;
  min-width: 0;
}

.model-option-title {
  display: block;
  color: var(--color-text-primary);
  font-size: 15px;
  line-height: 22px;
  font-weight: 600;
}

.model-option-desc {
  display: block;
  margin-top: 2px;
  color: var(--color-text-tertiary);
  font-size: 12px;
  line-height: 16px;
}

.model-option-check {
  color: var(--color-primary);
  font-size: 14px;
  line-height: 1;
  font-weight: 700;
  flex-shrink: 0;
}

.history-mask {
  position: absolute;
  inset: 0;
  z-index: 20;
  background: rgba(15, 23, 42, 0.22);
  backdrop-filter: blur(2px);
}

.history-panel {
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 21;
  width: min(82vw, 320px);
  padding: calc(var(--safe-area-top, 0px) + 18px) var(--space-16) calc(18px + var(--safe-area-bottom, 0px));
  border-radius: 0 24px 24px 0;
  background: rgba(255, 255, 255, 0.98);
  box-shadow: var(--shadow-floating);
  border-right: 1px solid rgba(224, 231, 255, 0.86);
  display: flex;
  flex-direction: column;
  gap: var(--space-16);
  animation: sidebar-slide-in 220ms ease both;
}

.history-panel-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-12);
}

.history-panel-eyebrow {
  display: block;
  color: var(--color-primary);
  font-size: 11px;
  line-height: 16px;
  font-weight: 700;
  letter-spacing: 0.6px;
  text-transform: uppercase;
}

.history-panel-title {
  display: block;
  margin-top: 4px;
  color: var(--color-text-primary);
  font-size: 20px;
  line-height: 28px;
  font-weight: 700;
}

.history-panel-subtitle {
  display: block;
  margin-top: 6px;
  color: var(--color-text-tertiary);
  font-size: 13px;
  line-height: 18px;
}

.history-panel-close {
  width: 32px;
  height: 32px;
  border-radius: 999px;
  background: var(--color-surface-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-secondary);
  font-size: 18px;
  line-height: 1;
  flex-shrink: 0;
}

.history-primary-btn {
  height: 44px;
  padding: 0 16px;
  border-radius: 14px;
  background: var(--color-primary);
  box-shadow: var(--shadow-card);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: var(--color-text-inverse);
  font-size: 15px;
  line-height: 22px;
  font-weight: 600;
}

.history-primary-icon {
  font-size: 18px;
  line-height: 1;
  font-weight: 500;
}

.history-actions {
  display: flex;
  gap: var(--space-8);
}

.history-action-btn {
  flex: 1;
  height: 36px;
  padding: 0 14px;
  border-radius: var(--radius-pill);
  background: var(--color-surface-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-secondary);
  font-size: 13px;
  line-height: 18px;
}

.history-action-danger {
  color: var(--color-danger);
  background: rgba(239, 68, 68, 0.08);
}

.history-section-title {
  color: var(--color-text-tertiary);
  font-size: 12px;
  line-height: 16px;
  font-weight: 600;
}

.history-list {
  flex: 1;
  min-height: 0;
}

.history-item {
  padding: 14px 12px;
  border-bottom: 1px solid rgba(237, 240, 244, 0.78);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-12);
}

.history-item:last-child {
  border-bottom: none;
}

.history-item + .history-item {
  margin-top: 6px;
}

.history-item-active {
  background: rgba(224, 231, 255, 0.56);
}

.history-item-copy {
  flex: 1;
  min-width: 0;
}

.history-item-title {
  display: block;
  color: var(--color-text-primary);
  font-size: 15px;
  line-height: 22px;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.history-item-time {
  display: block;
  margin-top: 2px;
  color: var(--color-text-tertiary);
  font-size: 13px;
  line-height: 18px;
}

.history-item-badge {
  padding: 6px 10px;
  border-radius: var(--radius-pill);
  background: var(--color-primary-soft);
  color: var(--color-primary);
  font-size: 12px;
  line-height: 16px;
  flex-shrink: 0;
}

.history-item-active .history-item-title {
  color: var(--color-primary);
}

.history-empty {
  padding: var(--space-24) 0;
  text-align: center;
  color: var(--color-text-tertiary);
  font-size: 13px;
  line-height: 18px;
}

@keyframes sidebar-slide-in {
  from {
    opacity: 0;
    transform: translateX(-18px);
  }

  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes dropdown-slide-in {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(-8px);
  }

  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

.balance-pill {
  min-width: 72px;
  padding: 8px 12px;
  border-radius: var(--radius-pill);
  background: var(--color-primary-soft);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.balance-icon,
.balance-value {
  color: var(--color-primary);
  font-size: 15px;
  line-height: 22px;
  font-weight: 600;
}

.message-scroll {
  flex: 1;
  min-height: 0;
  padding: 0 var(--space-16);
}

.empty-state {
  padding: var(--space-32) 0 var(--space-24);
}

.empty-mark {
  width: 56px;
  height: 56px;
  border-radius: 20px;
  background: var(--color-primary-gradient);
  box-shadow: var(--shadow-raised);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-inverse);
  font-size: 20px;
  line-height: 28px;
  font-weight: 700;
}

.empty-title {
  display: block;
  margin-top: var(--space-16);
  color: var(--color-text-primary);
  font-size: 20px;
  line-height: 28px;
  font-weight: 700;
}

.empty-desc {
  display: block;
  margin-top: var(--space-8);
  color: var(--color-text-tertiary);
  font-size: 13px;
  line-height: 18px;
}

.empty-prompt-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--space-12);
  margin-top: var(--space-24);
}

.empty-prompt-card {
  min-height: 92px;
  padding: 14px;
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid rgba(224, 231, 255, 0.92);
  box-shadow: var(--shadow-card);
  color: var(--color-text-secondary);
  font-size: 13px;
  line-height: 18px;
}

.message-row {
  display: flex;
  align-items: flex-start;
  gap: var(--space-12);
  margin-bottom: var(--space-16);
}

.message-row-ai {
  justify-content: flex-start;
}

.message-row-user {
  justify-content: flex-end;
}

.ai-badge {
  width: 32px;
  height: 32px;
  border-radius: 999px;
  background: var(--color-primary);
  box-shadow: var(--shadow-card);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-inverse);
  font-size: 13px;
  line-height: 18px;
  font-weight: 600;
  flex-shrink: 0;
}

.message-stack {
  max-width: 75%;
  display: flex;
  flex-direction: column;
  gap: var(--space-8);
}

.message-row-user .message-stack {
  align-items: flex-end;
}

.message-bubble {
  overflow: hidden;
  padding: 12px 16px;
  box-shadow: var(--shadow-card);
}

.message-bubble-ai {
  border-radius: 12px 4px 12px 12px;
  background: var(--color-surface-muted);
}

.message-bubble-user {
  border-radius: 12px 12px 4px 12px;
  background: var(--color-primary);
}

.bubble-text {
  color: var(--color-text-secondary);
  font-size: 15px;
  line-height: 22px;
  white-space: pre-wrap;
  word-break: break-word;
}

.bubble-text-user {
  color: var(--color-text-inverse);
}

.bubble-rich-text {
  color: var(--color-text-secondary);
  font-size: 15px;
  line-height: 22px;
  word-break: break-word;
}

.bubble-image,
.bubble-video {
  width: 100%;
  margin-bottom: 10px;
  border-radius: 10px;
  overflow: hidden;
  background: rgba(17, 24, 39, 0.04);
}

.bubble-image:last-child,
.bubble-video:last-child {
  margin-bottom: 0;
}

.bubble-video {
  min-height: 180px;
}

.bubble-suggestion-row {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-8);
}

.bubble-action-row {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-8);
  padding-left: 2px;
}

.bubble-action-btn {
  min-width: 54px;
  height: 30px;
  padding: 0 12px;
  border-radius: var(--radius-pill);
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid rgba(224, 231, 255, 0.96);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-tertiary);
  font-size: 12px;
  line-height: 16px;
}

.bubble-action-btn-active {
  background: rgba(79, 70, 229, 0.1);
  border-color: rgba(129, 140, 248, 0.38);
  color: var(--color-primary);
}

.bubble-suggestion {
  padding: 8px 12px;
  border-radius: var(--radius-pill);
  background: rgba(224, 231, 255, 0.72);
  color: var(--color-primary);
  font-size: 13px;
  line-height: 18px;
}

.chat-bottom-anchor {
  height: 8px;
}

.composer-shell {
  padding: 8px var(--space-16) var(--space-16);
  background: rgba(255, 255, 255, 0.92);
  border-top: 1px solid rgba(224, 231, 255, 0.72);
  backdrop-filter: blur(18px);
  flex-shrink: 0;
}

.attachment-preview {
  margin-bottom: var(--space-12);
  padding: 10px 12px;
  border-radius: var(--radius-md);
  background: rgba(243, 244, 246, 0.92);
  display: flex;
  align-items: center;
  gap: 10px;
}

.attachment-preview-image {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  flex-shrink: 0;
}

.attachment-preview-name {
  flex: 1;
  min-width: 0;
  color: var(--color-text-secondary);
  font-size: 13px;
  line-height: 18px;
}

.attachment-remove {
  width: 28px;
  height: 28px;
  border-radius: 999px;
  background: rgba(209, 213, 219, 0.64);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-secondary);
  font-size: 18px;
  line-height: 1;
}

.composer-row {
  display: flex;
  align-items: flex-end;
  gap: var(--space-8);
}

.composer-action {
  width: 24px;
  height: 24px;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-tertiary);
  font-size: 24px;
  line-height: 1;
}

.composer-input-wrap {
  flex: 1;
  min-height: 48px;
  max-height: 132px;
  padding: 10px 14px;
  border-radius: var(--radius-md);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-card);
}

.composer-input-focus {
  border-color: var(--color-primary);
  background: #fafafa;
}

.composer-input {
  width: 100%;
  max-height: 110px;
  color: var(--color-text-primary);
  font-size: 15px;
  line-height: 22px;
  background: transparent;
}

.composer-placeholder {
  color: var(--color-text-tertiary);
  font-size: 15px;
}

.send-btn {
  min-width: 48px;
  height: 44px;
  padding: 0 16px;
  border-radius: var(--radius-sm);
  background: var(--color-primary);
  box-shadow: var(--shadow-card);
  display: flex;
  align-items: center;
  justify-content: center;
}

.send-btn-disabled {
  background: var(--color-border);
  opacity: 0.82;
}

.send-btn-loading {
  color: var(--color-text-inverse);
  font-size: 16px;
  line-height: 1;
  font-weight: 600;
}

.send-icon {
  position: relative;
  width: 18px;
  height: 18px;
}

.send-icon-plane {
  position: absolute;
  right: 0;
  top: 1px;
  width: 0;
  height: 0;
  border-top: 8px solid transparent;
  border-bottom: 8px solid transparent;
  border-left: 14px solid rgba(255, 255, 255, 0.98);
}

.send-icon-tail {
  position: absolute;
  left: 2px;
  top: 8px;
  width: 9px;
  height: 2px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.88);
  transform: rotate(-24deg);
  transform-origin: left center;
}

:deep(.bubble-rich-text p) {
  margin: 0;
}

:deep(.bubble-rich-text p + p),
:deep(.bubble-rich-text ul),
:deep(.bubble-rich-text ol),
:deep(.bubble-rich-text blockquote),
:deep(.bubble-rich-text div),
:deep(.bubble-rich-text table) {
  margin-top: 10px;
}

@media screen and (max-width: 375px) {
  .empty-prompt-grid {
    grid-template-columns: minmax(0, 1fr);
  }

  .message-stack {
    max-width: 82%;
  }
}
</style>
