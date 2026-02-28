# API 文档

本目录包含 API 接口的详细文档。

## 在线文档

访问 Swagger UI 查看完整 API 文档：
https://english-mastery-production.up.railway.app/docs

## API 概览

### 认证接口 `/api/v1/auth`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/register` | 用户注册 |
| POST | `/login` | 用户登录 |
| POST | `/refresh` | 刷新 Token |
| GET | `/me` | 获取当前用户 |

### 进度接口 `/api/v1/progress`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 获取学习进度 |
| POST | `/sync` | 同步进度数据 |
| POST | `/checkin` | 每日打卡 |

### 素材接口 `/api/v1/materials`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 获取素材列表 |
| POST | `/` | 创建新素材 |
| GET | `/{id}` | 获取素材详情 |
| DELETE | `/{id}` | 删除素材 |
| POST | `/{id}/retry` | 重试处理 |

## 响应格式

```json
{
  "code": 0,
  "message": "成功",
  "data": { ... }
}
```
