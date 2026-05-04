<script>
export default {
  onLaunch: function () {
    const dark = uni.getStorageSync('dark_mode');
    if (dark && typeof document !== 'undefined') {
      document.documentElement.classList.add('dark');
    }
  },
  onShow: function () {},
  onHide: function () {}
}
</script>

<style>
:root {
  --safe-area-top: 0px;
  --safe-area-bottom: 0px;
  --safe-area-top: constant(safe-area-inset-top);
  --safe-area-top: env(safe-area-inset-top);
  --safe-area-bottom: constant(safe-area-inset-bottom);
  --safe-area-bottom: env(safe-area-inset-bottom);
  --color-primary: #4f46e5;
  --color-primary-strong: #4338ca;
  --color-primary-soft: #e0e7ff;
  --color-primary-gradient: linear-gradient(135deg, #4f46e5 0%, #818cf8 100%);
  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-danger: #ef4444;
  --color-page: #f8fafc;
  --color-page-alt: #f3f4f6;
  --color-surface: #ffffff;
  --color-surface-muted: #f3f4f6;
  --color-header: rgba(255, 255, 255, 0.96);
  --color-sidebar: #ffffff;
  --color-text-primary: #111827;
  --color-text-secondary: #374151;
  --color-text-tertiary: #6b7280;
  --color-text-inverse: #ffffff;
  --color-border: #d1d5db;
  --color-border-soft: #e5e7eb;
  --color-divider: #edf0f4;
  --shadow-card: 0 1px 3px rgba(0, 0, 0, 0.05), 0 1px 2px rgba(0, 0, 0, 0.1);
  --shadow-raised: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  --shadow-floating: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-pill: 9999px;
  --space-4: 4px;
  --space-8: 8px;
  --space-12: 12px;
  --space-16: 16px;
  --space-24: 24px;
  --space-32: 32px;
  --motion-fast: 100ms ease;
  --motion-base: 200ms ease;
  --motion-slow: 300ms ease;
  --code-bg: #111827;
  --font-sans: -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'PingFang SC', 'Noto Sans SC', 'Microsoft YaHei', sans-serif;
}

.dark {
  --color-page: #0f172a;
  --color-surface: #111827;
  --color-surface-muted: #1f2937;
  --color-header: rgba(17, 24, 39, 0.92);
  --color-sidebar: #111827;
  --color-text-primary: #f9fafb;
  --color-text-secondary: #d1d5db;
  --color-text-tertiary: #9ca3af;
  --color-border: #374151;
  --color-border-soft: #1f2937;
  --color-divider: #273244;
  --shadow-card: 0 8px 24px rgba(15, 23, 42, 0.28);
  --shadow-raised: 0 10px 28px rgba(15, 23, 42, 0.34);
  --shadow-floating: 0 18px 40px rgba(15, 23, 42, 0.4);
  --code-bg: #0b0f14;
}

html, body, #app { height: 100%; overflow: hidden; }
page {
  height: 100%;
  overflow: hidden;
  background: var(--color-page);
  color: var(--color-text-primary);
  font-family: var(--font-sans);
  -webkit-font-smoothing: antialiased;
}
* { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-thumb { background-color: rgba(0,0,0,0.15); border-radius: 4px; }
.dark ::-webkit-scrollbar-thumb { background-color: rgba(255,255,255,0.1); }
::selection { background-color: rgba(51,112,255,0.2); color: inherit; }
html { scroll-behavior: smooth; }
input:focus, textarea:focus { outline: none; }
input, textarea { color: var(--color-text-primary); }
img { -webkit-user-drag: none; user-select: none; }
.dark img { filter: brightness(0.95); }
.is-pressed {
  transform: scale(0.98) !important;
  opacity: 0.92 !important;
}
view, text, input, textarea, scroll-view, swiper {
  transition: background-color var(--motion-base), color var(--motion-base), border-color var(--motion-base), box-shadow var(--motion-base), opacity var(--motion-base), transform var(--motion-fast);
}
@media (prefers-reduced-motion: reduce) {
  * { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }
}
</style>
