# 📋 English Mastery - 项目说明文档

> 完整的项目架构、技术实现和部署说明

---

## 🎯 项目概述

### 产品定位
English Mastery 是一款面向职场人士的英语进阶学习平台，帮助用户在 30 天内从日常英语水平（B1-B2）提升到工作/母语水平（C1-C2）。

### 核心价值
- **结构化学习路径**: 30 天系统课程设计
- **多维度能力提升**: 词汇、听力、阅读、写作、口语全面覆盖
- **游戏化激励机制**: 打卡系统、进度追踪、成就系统
- **云端数据同步**: 多设备无缝切换

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                        用户浏览器                            │
│                   (HTML/CSS/JavaScript)                      │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTPS
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                      Vercel (前端)                           │
│              english-mastery-app.vercel.app                  │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ 登录注册  │  │ 学习仪表盘│  │ 学习模块  │  │ 打卡日历  │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
└─────────────────────────┬───────────────────────────────────┘
                          │ API 调用
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                     Railway (后端)                           │
│          english-mastery-production.up.railway.app           │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                   FastAPI 应用                         │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  │   │
│  │  │ 认证 API │  │ 用户 API │  │ 进度 API │  │ 打卡 API │  │   │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘  │   │
│  └──────────────────────────────────────────────────────┘   │
│                          │                                   │
│                          ▼                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                 PostgreSQL 数据库                      │   │
│  │  ┌───────┐  ┌───────────┐  ┌────────┐  ┌─────────┐   │   │
│  │  │ Users │  │ Memberships│  │ Orders │  │ Progress│   │   │
│  │  └───────┘  └───────────┘  └────────┘  └─────────┘   │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 技术栈详情

### 前端技术
| 技术 | 版本 | 用途 |
|------|------|------|
| HTML5 | - | 页面结构 |
| CSS3 | - | 样式布局 |
| JavaScript | ES6+ | 交互逻辑 |
| Chart.js | 4.x | 雷达图可视化 |
| LocalStorage | - | 本地缓存 |

### 后端技术
| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.11 | 运行环境 |
| FastAPI | 0.109.0 | Web 框架 |
| SQLAlchemy | 2.0.25 | ORM |
| asyncpg | 0.29.0 | PostgreSQL 异步驱动 |
| python-jose | 3.3.0 | JWT 处理 |
| passlib | 1.7.4 | 密码加密 |
| Pydantic | 2.5.3 | 数据验证 |

### 部署平台
| 平台 | 用途 | 费用 |
|------|------|------|
| Vercel | 前端托管 | 免费 |
| Railway | 后端 + 数据库 | $5/月免费额度 |
| GitHub | 代码托管 | 免费 |

---

## 📊 数据库设计

### 用户表 (users)
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    nickname VARCHAR(100),
    password_hash VARCHAR(255) NOT NULL,
    avatar_url VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 会员表 (memberships)
```sql
CREATE TABLE memberships (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    plan_type VARCHAR(50),  -- free, monthly, yearly
    status VARCHAR(50),     -- active, expired, cancelled
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 学习进度表 (progress)
```sql
CREATE TABLE progress (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    day INT NOT NULL,
    tasks_completed JSONB,
    study_time INT,  -- 分钟
    checkin_date DATE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🔐 认证流程

### JWT 双令牌机制

```
用户登录
    │
    ▼
┌─────────────────┐
│ 验证邮箱+密码    │
└────────┬────────┘
         │ 成功
         ▼
┌─────────────────────────────────────┐
│ 生成 Token 对                        │
│ • Access Token (15分钟有效)          │
│ • Refresh Token (7天有效)            │
└────────┬────────────────────────────┘
         │
         ▼
    返回给前端
         │
         ▼
┌─────────────────────────────────────┐
│ 前端存储 Token                       │
│ • Access Token → localStorage       │
│ • Refresh Token → localStorage      │
└─────────────────────────────────────┘
         │
         ▼
    API 请求时
         │
         ▼
┌─────────────────────────────────────┐
│ Authorization: Bearer <access_token>│
└────────┬────────────────────────────┘
         │
         ▼
    Access Token 过期?
         │
    ┌────┴────┐
    │ 是      │ 否
    ▼         ▼
使用 Refresh   正常访问
Token 换取     API
新 Access Token
```

---

## 🌐 API 接口文档

### 基础信息
- **Base URL**: `https://english-mastery-production.up.railway.app`
- **API 前缀**: `/api/v1`
- **认证方式**: Bearer Token

### 认证接口

#### 用户注册
```http
POST /api/v1/auth/register
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "nickname": "学习者"
}
```

#### 用户登录
```http
POST /api/v1/auth/login
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "SecurePass123!"
}
```

**响应**:
```json
{
    "code": 0,
    "message": "登录成功",
    "data": {
        "access_token": "eyJhbGciOiJIUzI1NiIs...",
        "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
        "token_type": "bearer",
        "user": {
            "id": "uuid",
            "email": "user@example.com",
            "nickname": "学习者"
        }
    }
}
```

### 学习进度接口

#### 获取进度
```http
GET /api/v1/progress
Authorization: Bearer <access_token>
```

#### 同步进度
```http
POST /api/v1/progress/sync
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "day": 1,
    "tasks_completed": ["vocabulary", "listening"],
    "study_time": 45
}
```

---

## 📦 环境变量

### 后端环境变量 (Railway)
```env
# 数据库
DATABASE_URL=postgresql://...

# JWT 配置
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=https://english-mastery-app.vercel.app

# 应用配置
DEBUG=false
```

### 前端环境变量 (Vercel)
```env
API_BASE_URL=https://english-mastery-production.up.railway.app/api/v1
```

---

## 🚀 部署流程

### 1. 代码推送到 GitHub
```bash
git add .
git commit -m "your changes"
git push origin main
```

### 2. 自动部署触发
- **Railway**: 检测到 `backend/` 目录变化 → 自动重新部署后端
- **Vercel**: 检测到前端文件变化 → 自动重新部署前端

### 3. 部署验证
- 后端: 访问 `/health` 检查服务状态
- 前端: 访问首页检查页面加载

---

## 💰 成本估算

### 产品验证阶段（当前）
| 项目 | 费用 |
|------|------|
| Vercel 前端托管 | $0 |
| Railway 后端 ($5 额度) | $0 |
| GitHub 代码托管 | $0 |
| **总计** | **$0/月** |

### 小规模运营阶段
| 项目 | 费用 |
|------|------|
| Vercel Pro | ~$20/月 |
| Railway Starter | ~$5-20/月 |
| **总计** | **$25-40/月** |

---

## 📈 后续规划

### Phase 1: 产品验证（当前）
- [x] 基础功能完成
- [x] 云端部署上线
- [ ] 邀请种子用户测试
- [ ] 收集用户反馈

### Phase 2: 功能完善
- [ ] 完善学习内容
- [ ] 添加更多练习题
- [ ] 优化用户体验
- [ ] 接入支付系统

### Phase 3: 规模化
- [ ] 迁移到更稳定的云服务
- [ ] 添加管理后台
- [ ] 数据分析系统
- [ ] 营销推广

---

## 🔗 相关资源

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Railway 文档](https://docs.railway.app/)
- [Vercel 文档](https://vercel.com/docs)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)

---

*文档更新时间: 2026-02-27*
