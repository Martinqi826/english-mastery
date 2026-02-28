# 开发指南

本目录包含各类开发和使用指南。

## 快速开始

### 本地开发

```bash
# 前端
python3 -m http.server 8080

# 后端
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 部署

参考 [DEPLOY_FREE.md](../../DEPLOY_FREE.md)

## 指南列表

| 指南 | 说明 |
|------|------|
| [CONTRIBUTING.md](../../CONTRIBUTING.md) | 贡献指南 |
| [DESIGN_GUIDE.md](../../DESIGN_GUIDE.md) | 设计规范 |
| [DEPLOY_FREE.md](../../DEPLOY_FREE.md) | 免费部署 |

## 常见问题

### Q: 如何添加新的数据库表？

使用 Alembic 迁移，参考 [AI_GUIDE.md](../../AI_GUIDE.md)

### Q: 如何添加新页面？

1. 复制现有页面结构
2. 保持导航栏一致
3. 遵循设计规范

### Q: 如何调试后端？

查看 Railway Dashboard 的 Logs
