# English Mastery 免费部署指南

本指南帮助您使用完全免费的方案将项目部署到外网，用于产品验证。

## 📊 部署架构

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│   Vercel        │      │    Railway       │      │   PostgreSQL    │
│   (前端托管)    │─────▶│    (后端 API)    │─────▶│   (Railway DB)  │
│   免费          │      │    $5/月免费额度  │      │   免费          │
└─────────────────┘      └──────────────────┘      └─────────────────┘
```

## 🚀 第一步：部署后端到 Railway

### 1.1 注册 Railway 账号

1. 访问 [railway.app](https://railway.app)
2. 使用 GitHub 账号登录（推荐）或邮箱注册
3. 新账号会获得 $5/月的免费额度

### 1.2 创建项目

1. 点击 **"New Project"**
2. 选择 **"Deploy from GitHub repo"**
3. 授权 Railway 访问您的 GitHub
4. 选择 `english-mastery` 仓库

### 1.3 配置后端服务

由于我们的仓库有前后端代码，需要指定后端目录：

1. 在项目设置中，点击 **"Settings"**
2. 在 **"Root Directory"** 中填写：`backend`
3. Railway 会自动检测 Python 项目并安装依赖

### 1.4 添加 PostgreSQL 数据库

1. 在项目面板中，点击 **"+ New"**
2. 选择 **"Database"** → **"Add PostgreSQL"**
3. Railway 会自动创建数据库并设置 `DATABASE_URL` 环境变量

### 1.5 配置环境变量

在后端服务的 **"Variables"** 中添加：

```bash
# 必需配置
JWT_SECRET_KEY=your-super-secret-key-change-this-to-random-string
DATABASE_URL_ENV=${{Postgres.DATABASE_URL}}

# 可选配置
DEBUG=false
CORS_ORIGINS=https://your-vercel-app.vercel.app,http://localhost:3000
```

> ⚠️ **重要**：`JWT_SECRET_KEY` 请使用随机字符串，可以在终端运行：
> ```bash
> python3 -c "import secrets; print(secrets.token_urlsafe(32))"
> ```

### 1.6 部署

1. 点击 **"Deploy"** 或等待自动部署
2. 部署成功后，点击 **"Generate Domain"** 获取公网域名
3. 记录下域名，格式类似：`your-app-name.railway.app`

### 1.7 验证后端

访问 `https://your-app-name.railway.app/docs` 应该能看到 API 文档页面。

---

## 🎨 第二步：部署前端到 Vercel

### 2.1 注册 Vercel 账号

1. 访问 [vercel.com](https://vercel.com)
2. 使用 GitHub 账号登录

### 2.2 导入项目

1. 点击 **"Add New..."** → **"Project"**
2. 选择 `english-mastery` 仓库
3. **重要**：不需要修改 Root Directory，Vercel 会托管整个前端

### 2.3 配置构建

在 **"Configure Project"** 页面：

- **Framework Preset**: `Other`
- **Build Command**: 留空（纯静态网站）
- **Output Directory**: `.`（当前目录）
- **Install Command**: 留空

### 2.4 配置环境变量（重要！）

在 **"Environment Variables"** 中添加：

```
API_BASE_URL = https://your-app-name.railway.app/api/v1
```

> 将 `your-app-name` 替换为上一步 Railway 生成的域名。

### 2.5 部署

1. 点击 **"Deploy"**
2. 等待部署完成（通常 1-2 分钟）
3. 获得前端域名，格式类似：`english-mastery.vercel.app`

### 2.6 更新 Railway CORS 配置

回到 Railway，更新 `CORS_ORIGINS` 环境变量：

```bash
CORS_ORIGINS=https://english-mastery.vercel.app,http://localhost:3000
```

---

## ✅ 第三步：验证部署

### 3.1 测试 API

```bash
# 健康检查
curl https://your-app-name.railway.app/health

# 应该返回：
# {"status":"healthy","version":"1.0.0"}
```

### 3.2 测试前端

1. 访问 `https://english-mastery.vercel.app`
2. 尝试注册一个新账号
3. 登录并测试各功能模块

---

## 🔧 常见问题

### Q1: Railway 报错 "No start command found"

确保 `backend/` 目录下有以下文件之一：
- `Procfile`（已创建）
- `railway.json`（已创建）

### Q2: 数据库连接失败

1. 确认 PostgreSQL 插件已添加
2. 检查 `DATABASE_URL_ENV` 是否正确引用了 `${{Postgres.DATABASE_URL}}`

### Q3: 前端无法调用 API (CORS 错误)

1. 检查 Railway 的 `CORS_ORIGINS` 是否包含 Vercel 域名
2. 确保前端 `API_BASE_URL` 配置正确

### Q4: 超出免费额度

Railway 会在接近额度时发邮件提醒。如果超出：
- 服务不会立即停止
- 可以添加信用卡升级，或等下月额度刷新

---

## 📈 扩展建议

当产品验证成功，用户增长后：

1. **升级 Railway** - 添加付费计划获得更多资源
2. **添加 Redis** - Railway 支持一键添加 Redis
3. **配置自定义域名** - 两个平台都支持绑定自己的域名
4. **添加 CDN** - 可以使用 Cloudflare 免费 CDN

---

## 🔗 有用链接

- [Railway 文档](https://docs.railway.app)
- [Vercel 文档](https://vercel.com/docs)
- [FastAPI 文档](https://fastapi.tiangolo.com)

---

## 💰 费用预估

| 服务 | 费用 | 说明 |
|------|------|------|
| Railway 后端 | $0-5/月 | $5 免费额度内 |
| Railway PostgreSQL | $0 | 含在免费额度 |
| Vercel 前端 | $0 | 永久免费（个人使用） |
| **总计** | **$0** | 免费验证产品！ |
