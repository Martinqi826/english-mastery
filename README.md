# 🎯 English Mastery - 英语进阶大师

> 30天从日常英语到工作/母语水平的进阶学习平台

[![Version](https://img.shields.io/badge/version-1.4.0-blue.svg)](./CHANGELOG.md)
[![Deploy](https://img.shields.io/badge/deploy-Surge.sh-orange.svg)](https://english-mastery-2026.surge.sh)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](./LICENSE)

## 🌐 在线访问

**线上地址**: [https://english-mastery-2026.surge.sh](https://english-mastery-2026.surge.sh)

---

## 📖 项目简介

English Mastery 是一个面向有一定英语基础（B1-B2水平）用户的英语进阶学习平台，帮助用户在30天内系统提升英语能力，达到工作/接近母语水平（C1-C2）。

### 目标用户
- **当前水平**: 日常交流/游戏英语（B1-B2）
- **目标水平**: 工作/接近母语水平（C1-C2）
- **学习周期**: 30天
- **使用场景**: 工作沟通、商务写作、专业表达

---

## ✨ 功能特性

### 🔐 用户系统
- 邮箱+密码注册/登录
- 密码强度检测
- 记住登录状态
- 用户菜单（头像、昵称、退出）

### 📊 学习仪表盘
- 总体进度可视化展示
- 当前水平等级显示
- 能力雷达图（词汇/听力/阅读/写作/口语）
- 连续打卡天数统计
- 学习时长统计

### ✅ 每日任务系统
- 5项每日学习任务
- 任务完成状态追踪
- 完成后按钮状态变化（颜色+文字）
- 完成3项任务即可打卡

### 👥 社区统计
- 今日参与学习人数（UV统计）
- 今日完成学习人数
- 实时完成率显示
- 数据每30秒自动更新

### 📚 学习模块
| 模块 | 功能 | 每日内容 |
|------|------|---------|
| 📖 词汇学习 | 高频商务词汇 | 30词/天 |
| 👂 听力训练 | TED/播客/商务对话 | 15分钟 |
| 📚 阅读练习 | 商务邮件/报告/文章 | 15分钟 |
| ✍️ 写作练习 | 邮件/报告/纪要 | 20分钟 |
| 🎯 每日测验 | 当日知识点检测 | 10分钟 |

### 📅 打卡日历
- 月度打卡视图
- 连续打卡记录
- 打卡成功动画

---

## 🛠️ 技术栈

- **前端框架**: HTML5 + CSS3 + Vanilla JavaScript
- **图表库**: Chart.js（雷达图）
- **数据存储**: LocalStorage（本地持久化）
- **部署平台**: Surge.sh

---

## 📁 项目结构

```
english-mastery/
├── index.html              # 主页面（仪表盘）
├── README.md               # 项目说明文档（本文件）
├── CHANGELOG.md            # 更新日志
├── Plan.md                 # 项目规划文档
├── pages/
│   ├── auth.html           # 登录/注册页面
│   ├── vocabulary.html     # 词汇学习页
│   ├── listening.html      # 听力训练页
│   ├── reading.html        # 阅读练习页
│   ├── writing.html        # 写作练习页
│   ├── test.html           # 测试评估页
│   └── calendar.html       # 打卡日历页
├── css/
│   └── styles.css          # 主样式文件
└── js/
    ├── app.js              # 主应用逻辑
    ├── auth.js             # 用户认证模块
    ├── storage.js          # 数据存储模块
    ├── progress.js         # 进度计算模块
    └── checkin.js          # 打卡系统模块
```

---

## 🚀 本地运行

### 方式一：直接打开
```bash
# 直接在浏览器中打开 index.html
open index.html
```

### 方式二：本地服务器
```bash
# 使用 Python
python3 -m http.server 8080

# 或使用 Node.js
npx serve .
```

然后访问 `http://localhost:8080`

---

## 📦 部署

### Surge.sh 部署
```bash
# 安装 Surge CLI
npm install -g surge

# 部署
cd english-mastery
surge . english-mastery-2026.surge.sh
```

---

## 📊 数据说明

所有用户数据存储在浏览器 LocalStorage 中：

| Key | 说明 |
|-----|------|
| `em_progress` | 用户学习进度 |
| `em_checkin` | 打卡记录 |
| `em_study` | 学习统计数据 |
| `em_visitor_id` | 用户唯一标识 |
| `em_visit_data` | 社区统计数据 |

---

## 📝 更新日志

查看 [CHANGELOG.md](./CHANGELOG.md) 了解完整的更新历史。

### 最近更新 (v1.4.0)
- ✨ 新增用户注册/登录模块（邮箱+密码）
- ✨ 新增用户菜单和退出登录功能
- ✨ 新增页面访问保护

---

## 🔗 相关链接

- 📋 [项目规划文档](./Plan.md)
- 📝 [更新日志](./CHANGELOG.md)
- 🌐 [在线演示](https://english-mastery-2026.surge.sh)

---

## 👤 作者

由 CodeBuddy AI 协助开发

---

## 📄 许可证

MIT License
