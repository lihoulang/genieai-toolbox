export const openExternalUrl = (url, fallbackRoute = '') => {
  if (!url) {
    if (fallbackRoute) {
      uni.navigateTo({ url: fallbackRoute });
    }
    return;
  }

  // #ifdef H5
  window.open(url, '_blank', 'noopener,noreferrer');
  // #endif

  // #ifdef APP-PLUS
  plus.runtime.openURL(url);
  // #endif

  // #ifdef MP
  uni.setClipboardData({
    data: url,
    success: () => {
      uni.showToast({ title: '链接已复制，请在浏览器打开', icon: 'none' });
    },
  });
  // #endif
};
