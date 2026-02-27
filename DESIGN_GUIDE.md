# 🎨 English Mastery 视觉设计规范

> 基于 Notion 风格的极简主义设计系统

---

## 📐 设计哲学

### 核心原则

1. **极简克制** - 少即是多，去除一切不必要的装饰
2. **黑白灰为主** - 色彩仅用于功能性区分，不用于装饰
3. **大量留白** - 呼吸感，让内容成为主角
4. **功能优先** - 每个元素都有明确的功能目的
5. **一致性** - 整站保持统一的视觉语言

### Notion 风格特征

- 无渐变（或极淡渐变）
- 无强烈阴影（仅使用极淡的阴影）
- 无圆形彩色按钮
- 图标使用线条风格，单色
- 交互反馈克制、微妙

---

## 🎨 色彩系统

### 主色调（黑白灰）

```css
/* 文字色 */
--notion-black: #191919;      /* 标题、重要文字 */
--notion-dark: #37352f;       /* 正文 */
--notion-gray-dark: #787774;  /* 次要文字 */
--notion-gray: #9b9a97;       /* 辅助文字、图标 */

/* 背景色 */
--notion-bg: #ffffff;         /* 主背景 */
--notion-bg-hover: #f7f6f3;   /* 悬停背景 */
--notion-bg-secondary: #fbfbfa; /* 次级背景 */

/* 边框色 */
--notion-gray-light: #e3e2e0;   /* 边框、分割线 */
--notion-gray-lighter: #f1f1ef; /* 浅边框 */
```

### 功能色（克制使用）

```css
/* 仅在必要时使用 */
--notion-blue: #2383e2;    /* 链接、主要操作 */
--notion-green: #0f7b6c;   /* 成功、完成状态 */
--notion-red: #e03e3e;     /* 错误、危险操作 */
--notion-yellow: #dfab01;  /* 警告 */
--notion-orange: #d9730d;  /* 强调 */
```

### ⚠️ 禁止使用

- ❌ 渐变色背景（如 `linear-gradient`）
- ❌ 高饱和度的彩色
- ❌ 霓虹色、荧光色
- ❌ 多色组合装饰

---

## 🔘 按钮设计

### 主要按钮（Primary）

```css
.btn-primary {
  background: #191919;      /* 纯黑色，非渐变 */
  color: white;
  border: none;
  border-radius: 8px;       /* 中等圆角 */
  padding: 8px 16px;
  font-weight: 500;
  transition: opacity 0.12s ease;
}

.btn-primary:hover {
  opacity: 0.85;            /* 悬停仅改变透明度 */
}
```

### 次要按钮（Secondary）

```css
.btn-secondary {
  background: transparent;
  color: #37352f;
  border: 1px solid #e3e2e0;
  border-radius: 8px;
}

.btn-secondary:hover {
  background: #f7f6f3;
  border-color: #9b9a97;
}
```

### 图标按钮（Icon Button）

```css
/* Notion 风格的图标按钮 - 无背景色 */
.icon-btn {
  background: transparent;
  border: none;
  padding: 4px;
  border-radius: 4px;
  color: #9b9a97;           /* 灰色图标 */
  cursor: pointer;
  transition: all 0.12s ease;
}

.icon-btn:hover {
  background: #f7f6f3;      /* 悬停显示浅灰背景 */
  color: #37352f;           /* 图标变深 */
}
```

### ⚠️ 按钮禁止事项

- ❌ 彩色渐变背景
- ❌ 强烈的 box-shadow
- ❌ 圆形彩色按钮
- ❌ 发光效果
- ❌ 3D 效果

---

## 📝 图标设计

### 图标风格

- **类型**: 线条图标（Outline），非填充（Filled）
- **线宽**: 1.5px - 2px
- **颜色**: 单色，使用 `--notion-gray` 或 `--notion-dark`
- **尺寸**: 16px（小）、20px（中）、24px（大）

### 图标按钮示例

```html
<!-- ✅ 正确：透明背景 + 灰色线条图标 -->
<button class="icon-btn" title="播放发音">
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <path d="M11 5L6 9H2v6h4l5 4V5z"/>
    <path d="M15.54 8.46a5 5 0 010 7.07"/>
  </svg>
</button>

<!-- ❌ 错误：彩色渐变背景 -->
<button style="background: linear-gradient(135deg, #6366f1, #8b5cf6);">
  <svg fill="white">...</svg>
</button>
```

---

## 📦 卡片设计

### 标准卡片

```css
.card {
  background: #ffffff;
  border: 1px solid #e3e2e0;
  border-radius: 12px;
  box-shadow: rgba(15, 15, 15, 0.03) 0px 0px 0px 1px,
              rgba(15, 15, 15, 0.04) 0px 3px 6px;  /* 极淡阴影 */
}

.card:hover {
  box-shadow: rgba(15, 15, 15, 0.04) 0px 0px 0px 1px,
              rgba(15, 15, 15, 0.06) 0px 5px 10px;
}
```

### ⚠️ 卡片禁止事项

- ❌ 彩色边框
- ❌ 强烈阴影
- ❌ 背景渐变

---

## 📏 间距系统

```css
--spacing-xs: 4px;
--spacing-sm: 8px;
--spacing-md: 16px;
--spacing-lg: 24px;
--spacing-xl: 40px;
--spacing-2xl: 64px;
--spacing-3xl: 96px;
```

### 使用原则

- 组件内部间距：`xs` - `md`
- 组件之间间距：`lg` - `xl`
- 区块之间间距：`xl` - `2xl`

---

## 🔤 字体排版

### 字体家族

```css
--font-sans: ui-sans-serif, -apple-system, BlinkMacSystemFont, 
             "Segoe UI", Helvetica, Arial, sans-serif;
--font-mono: ui-monospace, SFMono-Regular, SF Mono, Menlo, monospace;
```

### 字体大小

```css
/* 标题 */
h1: 2.5rem (40px), font-weight: 700
h2: 1.5rem (24px), font-weight: 600
h3: 1.25rem (20px), font-weight: 600
h4: 1rem (16px), font-weight: 600

/* 正文 */
body: 1rem (16px), font-weight: 400
small: 0.875rem (14px)
caption: 0.75rem (12px)
```

### 字间距

```css
h1 { letter-spacing: -0.03em; }  /* 标题紧凑 */
body { letter-spacing: 0; }      /* 正文正常 */
```

---

## ✨ 交互动效

### 过渡时间

```css
--transition-fast: 120ms ease;    /* 微交互 */
--transition-normal: 200ms ease;  /* 标准交互 */
```

### 悬停效果

```css
/* ✅ 正确：微妙的变化 */
.element:hover {
  background: #f7f6f3;  /* 浅灰背景 */
  opacity: 0.85;        /* 轻微透明 */
}

/* ❌ 错误：夸张的效果 */
.element:hover {
  transform: scale(1.2);
  box-shadow: 0 10px 40px rgba(0,0,0,0.3);
}
```

### 动画原则

- 持续时间：100ms - 300ms
- 缓动函数：`ease` 或 `ease-out`
- 避免弹跳、旋转等夸张动画

---

## 📱 响应式设计

### 断点

```css
/* 移动端优先 */
@media (min-width: 640px) { }   /* 平板 */
@media (min-width: 1024px) { }  /* 桌面 */
@media (min-width: 1280px) { }  /* 大屏 */
```

---

## ✅ 设计检查清单

在提交任何 UI 更改前，请确认：

- [ ] 是否使用了规定的色彩系统？
- [ ] 按钮是否遵循 Notion 风格（无渐变、无强阴影）？
- [ ] 图标是否为线条风格、单色？
- [ ] 间距是否使用标准间距变量？
- [ ] 动效是否克制、微妙？
- [ ] 整体是否保持极简风格？

---

## 🔧 快速参考

### CSS 变量速查

```css
/* 常用颜色 */
color: var(--notion-dark);           /* 正文 */
color: var(--notion-gray);           /* 辅助文字 */
background: var(--notion-bg-hover);  /* 悬停背景 */
border-color: var(--notion-gray-light); /* 边框 */

/* 常用间距 */
padding: var(--spacing-md);          /* 16px */
gap: var(--spacing-sm);              /* 8px */
margin-bottom: var(--spacing-lg);    /* 24px */

/* 常用圆角 */
border-radius: var(--radius-sm);     /* 4px */
border-radius: var(--radius-md);     /* 8px */
border-radius: var(--radius-lg);     /* 12px */
```

---

*文档版本: 1.0.0*
*更新日期: 2026-02-27*
