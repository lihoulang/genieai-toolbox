import * as GooglePlayBilling from '../uni_modules/genie-google-play-billing';

const getPlatformInfo = () => {
  try {
    const info = uni.getSystemInfoSync();
    return {
      platform: info.platform || '',
      isApp: typeof plus !== 'undefined',
      isAndroidApp: typeof plus !== 'undefined' && info.platform === 'android',
    };
  } catch (error) {
    return {
      platform: '',
      isApp: typeof plus !== 'undefined',
      isAndroidApp: false,
    };
  }
};

export const getGooglePlayBillingStatus = async () => {
  const platformInfo = getPlatformInfo();
  if (!platformInfo.isApp) {
    return {
      ...platformInfo,
      supported: false,
      message: 'Google Play 会员购买仅支持 Android App',
    };
  }
  if (!platformInfo.isAndroidApp) {
    return {
      ...platformInfo,
      supported: false,
      message: '当前设备不是 Android，无法使用 Google Play 购买',
    };
  }
  try {
    const result = await GooglePlayBilling.isBillingSupported();
    return {
      ...platformInfo,
      supported: !!result?.supported,
      message: result?.message || '',
    };
  } catch (error) {
    return {
      ...platformInfo,
      supported: false,
      message: error?.message || 'Google Play Billing 插件不可用',
    };
  }
};

export const queryGooglePlaySubscriptions = async (productIds = []) => {
  if (!Array.isArray(productIds) || productIds.length === 0) return [];
  const result = await GooglePlayBilling.querySubscriptionProducts(productIds);
  return Array.isArray(result) ? result : [];
};

export const launchGooglePlaySubscription = async ({ productId, offerToken = '' }) => {
  return GooglePlayBilling.purchaseSubscription({ productId, offerToken });
};

export const queryGooglePlayActiveSubscriptions = async () => {
  const result = await GooglePlayBilling.queryActiveSubscriptions();
  return Array.isArray(result) ? result : [];
};
