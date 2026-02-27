# English Mastery 部署指南

## 快速开始

### 1. 环境要求

- Docker 20.0+
- Docker Compose 2.0+
- 云服务器（腾讯云/阿里云 CVM，建议 2核4G 以上）

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp ../backend/.env.example ../backend/.env

# 编辑配置
vim ../backend/.env
```

关键配置项：
```env
# 数据库密码（请修改为强密码）
DB_PASSWORD=your_secure_password

# JWT 密钥（请使用随机字符串）
JWT_SECRET_KEY=your-super-secret-key-change-in-production

# 微信支付配置（如需支付功能）
WECHAT_MCHID=your_mchid
WECHAT_APPID=your_appid
# ...
```

### 3. 部署服务

```bash
# 进入部署目录
cd deploy

# 设置环境变量
export DB_PASSWORD=your_secure_password
export JWT_SECRET_KEY=your-super-secret-key
export MYSQL_ROOT_PASSWORD=root_secure_password

# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 4. 验证部署

```bash
# 检查 API 健康状态
curl http://localhost/health

# 检查前端页面
curl http://localhost/
```

## 服务说明

| 服务 | 端口 | 说明 |
|------|------|------|
| nginx | 80, 443 | 反向代理 + 静态资源 |
| api | 8000 | FastAPI 后端服务 |
| mysql | 3306 | MySQL 数据库 |
| redis | 6379 | Redis 缓存 |

## 运维命令

### 查看日志
```bash
# 所有服务日志
docker-compose logs -f

# 指定服务日志
docker-compose logs -f api
docker-compose logs -f nginx
```

### 重启服务
```bash
# 重启所有服务
docker-compose restart

# 重启指定服务
docker-compose restart api
```

### 更新部署
```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker-compose up -d --build
```

### 数据库备份
```bash
# 备份数据库
docker exec english-mastery-mysql mysqldump -u root -p english_mastery > backup_$(date +%Y%m%d).sql

# 恢复数据库
docker exec -i english-mastery-mysql mysql -u root -p english_mastery < backup.sql
```

## HTTPS 配置

### 1. 获取 SSL 证书

推荐使用 Let's Encrypt 免费证书：
```bash
# 安装 certbot
apt install certbot

# 获取证书
certbot certonly --standalone -d your-domain.com
```

### 2. 配置证书

```bash
# 复制证书到 ssl 目录
mkdir -p ssl
cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ssl/cert.pem
cp /etc/letsencrypt/live/your-domain.com/privkey.pem ssl/key.pem
```

### 3. 修改 Nginx 配置

编辑 `nginx.conf`，取消 HTTPS 配置的注释，并修改域名。

### 4. 重启 Nginx

```bash
docker-compose restart nginx
```

## 性能优化

### MySQL 优化

编辑 `docker-compose.yml`，添加 MySQL 配置：
```yaml
mysql:
  command: >
    --innodb_buffer_pool_size=512M
    --max_connections=200
    --query_cache_size=64M
```

### Redis 优化

```yaml
redis:
  command: >
    redis-server
    --maxmemory 256mb
    --maxmemory-policy allkeys-lru
```

## 监控告警

### 使用 Prometheus + Grafana

1. 添加监控服务到 docker-compose.yml
2. 配置 Prometheus 采集指标
3. 在 Grafana 配置仪表盘

### 日志收集

推荐使用 ELK Stack 或腾讯云日志服务进行日志收集和分析。

## 常见问题

### Q: 数据库连接失败
A: 检查 MySQL 容器是否启动完成，可能需要等待几秒钟。

### Q: API 返回 502
A: 检查后端服务是否启动，查看 `docker-compose logs api`。

### Q: 静态资源 404
A: 确认 Nginx 配置中的路径映射正确。

## 安全建议

1. 修改默认密码
2. 配置防火墙，只开放必要端口
3. 使用 HTTPS
4. 定期备份数据
5. 及时更新依赖包
