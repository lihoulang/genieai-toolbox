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
  --bg-page: #f7f8fb;
  --bg-chat: #ffffff;
  --bg-card: #ffffff;
  --bg-input: #f6f8fb;
  --bg-bubble-ai: #ffffff;
  --bg-bubble-user: linear-gradient(135deg, #6670e8 0%, #5d62c9 100%);
  --bg-sidebar: #ffffff;
  --bg-header: rgba(255,255,255,0.98);
  --text-primary: #232939;
  --text-secondary: #687385;
  --text-tertiary: #9aa3b3;
  --text-inverse: #ffffff;
  --border-color: #e6e9ef;
  --border-light: #eef1f5;
  --shadow-card: 0 8px 20px rgba(32,43,67,0.05);
  --shadow-msg: 0 6px 16px rgba(32,43,67,0.04);
  --code-bg: #1e1e1e;
  --primary-color: #6670e8;
}

.dark {
  --bg-page: #0b0f14;
  --bg-chat: #0d1117;
  --bg-card: #151b23;
  --bg-input: #1a2232;
  --bg-bubble-ai: #151b23;
  --bg-bubble-user: linear-gradient(135deg, #1a4fad, #2563eb);
  --bg-sidebar: #151b23;
  --bg-header: rgba(21,27,35,0.95);
  --text-primary: #e5e7eb;
  --text-secondary: #9ca3af;
  --text-tertiary: #6b7280;
  --text-inverse: #ffffff;
  --border-color: #1e2733;
  --border-light: #2d3748;
  --shadow-card: 0 1px 3px rgba(0,0,0,0.3), 0 4px 12px rgba(0,0,0,0.2);
  --shadow-msg: 0 2px 6px rgba(0,0,0,0.3);
  --code-bg: #0b0f14;
}

html, body, #app { height: 100%; overflow: hidden; }
page { height: 100%; overflow: hidden; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif; -webkit-font-smoothing: antialiased; }
* { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-thumb { background-color: rgba(0,0,0,0.15); border-radius: 4px; }
.dark ::-webkit-scrollbar-thumb { background-color: rgba(255,255,255,0.1); }
::selection { background-color: rgba(51,112,255,0.2); color: inherit; }
html { scroll-behavior: smooth; }
input:focus, textarea:focus { outline: none; }
img { -webkit-user-drag: none; user-select: none; }
.dark img { filter: brightness(0.95); }
@media (prefers-reduced-motion: reduce) {
  * { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }
}
</style>
