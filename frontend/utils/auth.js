export const getAccessToken = () => uni.getStorageSync('access_token') || '';

export const getAuthHeaders = (extra = {}) => {
  const token = getAccessToken();
  return token ? { ...extra, Authorization: `Bearer ${token}` } : { ...extra };
};

export const clearAuthStorage = () => {
  uni.removeStorageSync('access_token');
  uni.removeStorageSync('token_expires_at');
  uni.removeStorageSync('user_id');
  uni.removeStorageSync('username');
};

export const redirectToLogin = (toastTitle = '登录已失效，请重新登录') => {
  clearAuthStorage();
  uni.showToast({ title: toastTitle, icon: 'none' });
  setTimeout(() => {
    uni.reLaunch({ url: '/pages/login/login' });
  }, 250);
};

export const ensureLoggedIn = () => {
  const token = getAccessToken();
  const userId = uni.getStorageSync('user_id');
  if (!token || !userId) {
    redirectToLogin('请先登录');
    return false;
  }
  return true;
};

export const requestWithAuth = async (options) => {
  const res = await uni.request({
    ...options,
    header: getAuthHeaders(options.header || {}),
  });

  const unauthorized =
    res.statusCode === 401 ||
    res.data?.detail === '未登录或登录已失效' ||
    res.data?.detail === '登录态失效，请重新登录' ||
    res.data?.detail === '登录已过期，请重新登录';
  if (unauthorized) {
    redirectToLogin();
    throw new Error('AUTH_EXPIRED');
  }
  return res;
};
