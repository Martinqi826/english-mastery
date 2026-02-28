# 🤖 AI 协作指南 (AI Collaboration Guide)

> 本文档专为 AI 助手设计（CodeBuddy、Claude、GPT、Copilot 等）
> 目的是让 AI 在新会话中快速恢复上下文，高效协作

---

## 🎯 项目概要

**English Mastery** 是一个英语进阶学习平台，帮助用户从 B1-B2 水平提升到 C1-C2。

### 技术栈速查
```
前端: HTML5 + CSS3 + Vanilla JS (Vercel)
后端: FastAPI + PostgreSQL (Railway)
风格: Notion 极简主义
AI:   Claude API (内容生成)
```

### 在线地址
```
前端: https://english-mastery-app.vercel.app
后端: https://english-mastery-production.up.railway.app
API:  https://english-mastery-production.up.railway.app/docs
```

---

## ⚡ 快速上下文恢复

新会话开始时，请执行以下步骤：

### Step 1: 读取核心文档
```
1. AI_GUIDE.md (本文件) - 了解协作规范
2. CHANGELOG.md - 了解最近更新
3. .codebuddy/rules/ - 加载自动规则
```

### Step 2: 了解项目状态
```
当前版本: 2.x
主要功能: 用户认证、学习模块、打卡系统、用户素材
数据库:   PostgreSQL (Railway) - 有真实用户数据！
```

### Step 3: 检查待办事项
```bash
# 查看 Plan.md 了解待实现功能
# 查看 GitHub Issues 了解问题
```

---

## 🚨 必须遵守的规则

### 1. 数据安全 - 最高优先级

```
⛔ 绝对禁止:
- drop_all() / create_all() 操作生产数据库
- 直接删除或重建表
- 修改已有字段的类型

✅ 必须执行:
- 使用 Alembic 进行数据库迁移
- 新字段必须有默认值或允许 NULL
- 变更前考虑数据兼容性
```

**为什么**: 项目已有注册用户，数据丢失是不可接受的！

### 2. 设计风格 - Notion 极简

```
⛔ 禁止使用:
- linear-gradient 渐变背景
- 彩色 emoji 作为导航图标
- 强烈的 box-shadow
- 3D 效果和发光效果

✅ 必须遵循:
- 黑白灰配色系统
- 导航图标使用符号: ◉ ◆ ◇
- 参考 DESIGN_GUIDE.md
```

### 3. 代码规范

```python
# 后端 Python
- 使用 async/await
- 完整的类型注解
- 中文错误提示
```

```javascript
// 前端 JavaScript
- ES6+ 语法
- 避免大型框架
- 文件保持独立
```

---

## 📁 项目结构速查

```
english-mastery/
├── 📄 文档
│   ├── README.md          # 项目入口
│   ├── CONTRIBUTING.md    # 贡献指南
│   ├── ARCHITECTURE.md    # 架构决策
│   ├── AI_GUIDE.md        # AI 指南 (本文件)
│   ├── DESIGN_GUIDE.md    # 设计规范
│   └── CHANGELOG.md       # 更新日志
│
├── 📁 .codebuddy/rules/   # AI 自动规则
│
├── 📁 前端
│   ├── index.html         # 仪表盘首页
│   ├── pages/*.html       # 各功能页面
│   ├── css/styles.css     # 全局样式
│   └── js/*.js            # JavaScript 模块
│
└── 📁 backend/            # 后端
    ├── app/
    │   ├── main.py        # FastAPI 入口
    │   ├── config.py      # 配置管理
    │   ├── database.py    # 数据库连接
    │   ├── models/        # 数据模型
    │   ├── schemas/       # Pydantic 模式
    │   ├── api/v1/        # API 路由
    │   └── services/      # 业务服务
    ├── alembic/           # 数据库迁移
    └── requirements.txt   # Python 依赖
```

---

## 🔧 常见操作指南

### 添加新的数据库表

```python
# 1. 创建模型 backend/app/models/new_model.py
from sqlalchemy import Column, Integer, String
from app.database import Base

class NewModel(Base):
    __tablename__ = "new_models"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))

# 2. 在 models/__init__.py 导出
from .new_model import NewModel

# 3. 创建迁移
# cd backend && alembic revision -m "add new_models table"

# 4. 编辑迁移文件，添加 upgrade/downgrade

# 5. 提交代码，Railway 自动执行迁移
```

### 添加新的 API 端点

```python
# backend/app/api/v1/new_endpoint.py
from fastapi import APIRouter, Depends
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/")
async def get_items(user = Depends(get_current_user)):
    return {"items": []}

# 在 api/v1/__init__.py 注册路由
```

### 添加新页面

```html
<!-- pages/new_page.html -->
<!-- 1. 复制现有页面结构 -->
<!-- 2. 保持导航栏一致 (使用 ◉◆◇ 符号) -->
<!-- 3. 遵循 DESIGN_GUIDE.md 样式规范 -->
```

---

## 🎨 设计速查

### 颜色系统
```css
--notion-black: #191919;     /* 标题、主按钮 */
--notion-dark: #37352f;      /* 正文 */
--notion-gray: #9b9a97;      /* 图标、辅助 */
--notion-bg-hover: #f7f6f3;  /* 悬停背景 */
--notion-blue: #2383e2;      /* 链接、激活 */
--notion-green: #0f7b6c;     /* 成功 */
--notion-red: #e03e3e;       /* 错误 */
```

### 导航图标
```
◉ - 仪表盘（首页）
◆ - 当前激活页面
◇ - 其他页面
```

---

## 📝 提交代码规范

```bash
# 格式
<type>: <description>

# 类型
feat:     新功能
fix:      修复 bug
docs:     文档更新
style:    样式调整
refactor: 重构
```

---

## 🔍 调试技巧

### 检查后端日志
```bash
# Railway Dashboard → Logs
```

### 检查前端
```bash
# 浏览器开发者工具 → Console/Network
```

### 测试 API
```bash
curl https://english-mastery-production.up.railway.app/health
```

---

## ⚠️ 常见陷阱

### 1. 导航栏图标不一致
每个页面的导航栏必须使用相同的符号图标，不要使用 emoji。

### 2. 数据库迁移忘记提交
迁移文件必须提交到 Git，Railway 才能执行。

### 3. 忘记更新 models/__init__.py
新模型必须在 `__init__.py` 导出才能被 Alembic 检测到。

### 4. API 响应格式不一致
统一使用：
```json
{
  "code": 0,
  "message": "成功",
  "data": {}
}
```

---

## 🔄 项目历史里程碑

| 版本 | 日期 | 主要功能 |
|------|------|----------|
| v1.0 | 2026-02 | 基础功能、本地存储 |
| v2.0 | 2026-02 | 用户系统、云端同步 |
| v2.1 | 2026-02 | 用户素材、AI 生成 |

---

## 🧠 给 AI 的特别提示

### 开始新任务前
1. 确认理解用户需求
2. 检查是否有相关规范
3. 考虑是否影响现有功能

### 修改代码时
1. 先理解现有代码
2. 最小化改动范围
3. 保持代码风格一致

### 完成任务后
1. 自检代码质量
2. 更新相关文档
3. 告知用户变更内容

### 遇到不确定时
1. 询问用户确认
2. 提供多个方案
3. 说明各方案利弊

---

## 📚 扩展阅读

- `ARCHITECTURE.md` - 了解为什么这样设计
- `DESIGN_GUIDE.md` - 完整的设计规范
- `PROJECT.md` - 详细的技术实现

---

*最后更新: 2026-02-28*
