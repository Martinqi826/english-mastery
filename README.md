# 🎯 English Mastery - 英语进阶大师

> 30天从日常英语到工作/母语水平的进阶学习平台

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](./CHANGELOG.md)
[![Frontend](https://img.shields.io/badge/frontend-Vercel-black.svg)](https://english-mastery-app.vercel.app)
[![Backend](https://img.shields.io/badge/backend-Railway-purple.svg)](https://english-mastery-production.up.railway.app)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](./LICENSE)

## 🌐 在线访问

| 环境 | 地址 |
|------|------|
| **前端应用** | https://english-mastery-app.vercel.app |
| **后端 API** | https://english-mastery-production.up.railway.app |
| **API 文档** | https://english-mastery-production.up.railway.app/docs |

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
- JWT Token 双令牌认证（Access Token + Refresh Token）
- 密码强度检测
- 记住登录状态
- 学习进度云端同步

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

### 💎 会员体系（规划中）
- 免费版：基础功能
- 月度会员：全部功能 + 高级内容
- 年度会员：全部功能 + 专属服务

---

## 🛠️ 技术栈

### 前端
- **框架**: HTML5 + CSS3 + Vanilla JavaScript
- **图表库**: Chart.js（雷达图）
- **部署平台**: Vercel

### 后端
- **框架**: FastAPI (Python 3.11)
- **数据库**: PostgreSQL
- **认证**: JWT (python-jose)
- **ORM**: SQLAlchemy 2.0 (异步)
- **部署平台**: Railway

---

## 📁 项目结构

```
english-mastery/
├── index.html              # 主页面（仪表盘）
├── README.md               # 项目说明文档（本文件）
├── CHANGELOG.md            # 更新日志
├── PROJECT.md              # 项目详细说明
├── vercel.json             # Vercel 部署配置
├── pages/
│   ├── auth.html           # 登录/注册页面
│   ├── vocabulary.html     # 词汇学习页
│   ├── listening.html      # 听力训练页
│   ├── reading.html        # 阅读练习页
│   ├── writing.html        # 写作练习页
│   ├── test.html           # 测试评估页
│   ├── calendar.html       # 打卡日历页
│   └── membership.html     # 会员中心页
├── css/
│   └── styles.css          # 主样式文件
├── js/
│   ├── app.js              # 主应用逻辑
│   ├── api.js              # API 调用层
│   ├── auth.js             # 用户认证模块
│   ├── storage.js          # 数据存储模块
│   ├── progress.js         # 进度计算模块
│   └── checkin.js          # 打卡系统模块
└── backend/                # 后端 API 服务
    ├── app/
    │   ├── main.py         # FastAPI 入口
    │   ├── config.py       # 配置管理
    │   ├── database.py     # 数据库连接
    │   ├── models/         # 数据模型
    │   ├── api/            # API 路由
    │   ├── services/       # 业务逻辑
    │   └── utils/          # 工具函数
    ├── requirements.txt    # Python 依赖
    ├── Procfile            # Railway 启动配置
    └── runtime.txt         # Python 版本
```

---

## 🚀 本地开发

### 前端运行
```bash
# 使用 Python
python3 -m http.server 8080

# 或使用 Node.js
npx serve .
```
然后访问 `http://localhost:8080`

### 后端运行
```bash
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 启动服务
uvicorn app.main:app --reload --port 8000
```
API 文档：`http://localhost:8000/docs`

---

## 📦 部署

### 前端部署（Vercel）
1. Fork 或 Clone 本仓库到 GitHub
2. 在 [Vercel](https://vercel.com) 导入项目
3. 配置环境变量 `API_BASE_URL`
4. 自动部署

### 后端部署（Railway）
1. 在 [Railway](https://railway.app) 创建项目
2. 连接 GitHub 仓库
3. 设置 Root Directory 为 `backend`
4. 添加 PostgreSQL 数据库
5. 配置环境变量
6. 自动部署

---

## 📊 API 接口

### 认证接口
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/auth/register` | 用户注册 |
| POST | `/api/v1/auth/login` | 用户登录 |
| POST | `/api/v1/auth/refresh` | 刷新 Token |
| GET | `/api/v1/auth/me` | 获取当前用户 |

### 学习进度接口
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/progress` | 获取学习进度 |
| POST | `/api/v1/progress/sync` | 同步进度数据 |
| POST | `/api/v1/checkin` | 每日打卡 |

### 健康检查
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 服务健康状态 |

---

## 📝 更新日志

查看 [CHANGELOG.md](./CHANGELOG.md) 了解完整的更新历史。

### 最新更新 (v2.0.0)
- 🚀 新增 FastAPI 后端服务
- 🔐 新增 JWT 双令牌认证系统
- 💾 新增学习进度云端同步
- ☁️ 部署到 Railway + Vercel

---

## 🔗 相关链接

- 📋 [项目详细说明](./PROJECT.md)
- 📝 [更新日志](./CHANGELOG.md)
- 🌐 [在线应用](https://english-mastery-app.vercel.app)
- 📚 [API 文档](https://english-mastery-production.up.railway.app/docs)

---

## 👤 作者

由 CodeBuddy AI 协助开发

---

## 📄 许可证

MIT License
