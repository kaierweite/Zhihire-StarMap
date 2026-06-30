# 第19天开发任务（详细版）

# 项目：智聘星图——基于银河麒麟操作系统的AI智能匹配与能力图谱平台

## 今日目标

完成Docker部署，编写docker-compose.yml和install.sh，确保可在银河麒麟V11上运行。

## 今日能力要求

- Docker Compose（熟练）
- Shell脚本（熟练）
- 银河麒麟系统（了解）

**最终产出：**

```text
deploy/
├──docker-compose.yml           # 编排文件
├──install.sh                   # 一键安装脚本
├──uninstall.sh                 # 卸载脚本
├──start.sh                     # 启动脚本
├──stop.sh                      # 停止脚本
├──restart.sh                   # 重启脚本
├──nginx/
│   └──zhihire.conf             # Nginx配置
├──backend/
│   ├──Dockerfile               # 后端Dockerfile
│   └──application-prod.yml     # 生产配置
├──frontend/
│   ├──Dockerfile               # 前端Dockerfile
│   └──nginx.conf               # 前端Nginx配置
├──ai-service/
│   ├──Dockerfile               # AI服务Dockerfile
│   └──.env                     # AI服务生产环境变量
├──database/
│   ├──init.sql                 # 数据库初始化脚本
│   └──Dockerfile               # 数据库镜像配置（可选）
├──.env                         # 全局环境变量
└──README.md                    # 部署说明
```

---

# 第一阶段：Dockerfile编写（2小时）

## 任务1：后端Dockerfile

```dockerfile
# backend/Dockerfile

# 构建阶段
FROM maven:3.9-eclipse-temurin-21 AS builder
WORKDIR /build
COPY pom.xml .
RUN mvn dependency:go-offline -B
COPY src ./src
RUN mvn package -DskipTests -Pprod

# 运行阶段
FROM eclipse-temurin:21-jre
WORKDIR /app
COPY --from=builder /build/target/zhihire-backend.jar app.jar

# 创建上传目录
RUN mkdir -p /data/upload

# 生产环境使用非root用户运行
RUN groupadd -r zhihire && useradd -r -g zhihire zhihire
RUN chown -R zhihire:zhihire /app /data
USER zhihire

EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar", "--spring.profiles.active=prod"]
```

## 任务2：前端Dockerfile

```dockerfile
# frontend/Dockerfile

# 构建阶段
FROM node:20-alpine AS builder
WORKDIR /build
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# 运行阶段
FROM nginx:alpine
COPY --from=builder /build/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 任务3：AI服务Dockerfile

```dockerfile
# ai-service/Dockerfile

FROM python:3.12-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

# 第二阶段：Docker Compose编排（1小时）

## 任务1：docker-compose.yml

```yaml
version: "3.8"

services:
  # 前端
  frontend:
    build:
      context: ../frontend
      dockerfile: ../deploy/frontend/Dockerfile
    ports:
      - "80:80"
    depends_on:
      - backend
    networks:
      - zhihire-net

  # 后端
  backend:
    build:
      context: ../backend
      dockerfile: ../deploy/backend/Dockerfile
    ports:
      - "8080:8080"
    environment:
      - SPRING_PROFILES_ACTIVE=prod
      - DB_URL=jdbc:postgresql://database:5432/zhihire
      - DB_USERNAME=zhihire
      - DB_PASSWORD=${DB_PASSWORD}
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - AI_SERVICE_URL=http://ai-service:8000
    volumes:
      - upload-data:/data/upload
    depends_on:
      database:
        condition: service_healthy
      redis:
        condition: service_started
    networks:
      - zhihire-net

  # AI服务
  ai-service:
    build:
      context: ../ai-service
      dockerfile: ../deploy/ai-service/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    depends_on:
      - ollama
    networks:
      - zhihire-net

  # Ollama（AI模型）
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama-data:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    networks:
      - zhihire-net

  # PostgreSQL数据库
  database:
    image: postgres:16-alpine
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=zhihire
      - POSTGRES_USER=zhihire
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ../database/schema.sql:/docker-entrypoint-initdb.d/01-schema.sql
      - ../database/seed.sql:/docker-entrypoint-initdb.d/02-seed.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U zhihire"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - zhihire-net

  # Redis缓存
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    command: redis-server --requirepass ${REDIS_PASSWORD}
    networks:
      - zhihire-net

  # Nginx反向代理
  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx/zhihire.conf:/etc/nginx/conf.d/zhihire.conf
      - upload-data:/var/www/upload:ro
    depends_on:
      - frontend
      - backend
    networks:
      - zhihire-net

volumes:
  postgres-data:
  redis-data:
  ollama-data:
  upload-data:

networks:
  zhihire-net:
    driver: bridge
```

---

# 第三阶段：安装部署脚本（1.5小时）

## 任务1：install.sh

```bash
#!/bin/bash
#
# 智聘星图 - 一键安装脚本
# 支持: Ubuntu 20.04+ / CentOS 7+ / 银河麒麟 V11
#

set -e

echo "========================================="
echo "  智聘星图 - 一键安装脚本"
echo "  基于银河麒麟操作系统的AI智能匹配与能力图谱平台"
echo "========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 检测操作系统
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        VERSION=$VERSION_ID
    else
        echo -e "${RED}无法检测操作系统${NC}"
        exit 1
    fi
    echo -e "${BLUE}检测到操作系统: $OS $VERSION${NC}"
}

# 检查环境
check_environment() {
    echo -e "${YELLOW}检查运行环境...${NC}"

    # 检查Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Docker未安装，开始安装...${NC}"
        install_docker
    else
        echo -e "${GREEN}Docker已安装: $(docker --version)${NC}"
    fi

    # 检查Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        if ! docker compose version &> /dev/null; then
            echo -e "${RED}Docker Compose未安装，开始安装...${NC}"
            install_docker_compose
        else
            echo -e "${GREEN}Docker Compose已安装: $(docker compose version)${NC}"
            COMPOSE_CMD="docker compose"
        fi
    else
        echo -e "${GREEN}Docker Compose已安装: $(docker-compose --version)${NC}"
        COMPOSE_CMD="docker-compose"
    fi

    # 检查Git
    if ! command -v git &> /dev/null; then
        echo -e "${YELLOW}Git未安装，跳过代码拉取${NC}"
    else
        echo -e "${GREEN}Git已安装: $(git --version)${NC}"
    fi
}

# 安装Docker
install_docker() {
    if [ "$OS" = "kylin" ]; then
        # 银河麒麟安装Docker
        sudo yum install -y yum-utils
        sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
        sudo yum install -y docker-ce docker-ce-cli containerd.io
    elif [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
        sudo apt-get update
        sudo apt-get install -y docker.io
    else
        curl -fsSL https://get.docker.com | bash
    fi
    sudo systemctl start docker
    sudo systemctl enable docker
    echo -e "${GREEN}Docker安装完成${NC}"
}

# 配置环境变量
setup_env() {
    echo -e "${YELLOW}配置环境变量...${NC}"

    if [ ! -f .env ]; then
        cat > .env << EOF
# 数据库密码
DB_PASSWORD=zhihire_2024_Strong

# Redis密码
REDIS_PASSWORD=zhihire_redis_2024

# JWT密钥
JWT_SECRET=zhihire-prod-jwt-secret-key-2024

# 环境
ENV=production
EOF
        echo -e "${GREEN}.env文件已创建，请修改默认密码${NC}"
    else
        echo -e "${GREEN}.env文件已存在${NC}"
    fi
}

# 构建和启动
build_and_start() {
    echo -e "${YELLOW}开始构建和启动服务...${NC}"

    # 下载Ollama模型（后台执行）
    echo -e "${BLUE}开始下载AI模型（约4.5GB，可能需要较长时间）...${NC}"
    docker exec ollama ollama pull qwen2.5:7b || true &

    # 构建并启动
    $COMPOSE_CMD up -d --build

    echo -e "${GREEN}所有服务已启动${NC}"
}

# 显示访问信息
show_info() {
    echo ""
    echo "========================================="
    echo -e "${GREEN}  部署完成！${NC}"
    echo ""
    echo "  访问地址:"
    echo "  前端:         http://localhost:80"
    echo "  后端API:      http://localhost:8080"
    echo "  Swagger文档:  http://localhost:8080/swagger-ui.html"
    echo "  AI服务:       http://localhost:8000"
    echo "  Ollama:       http://localhost:11434"
    echo ""
    echo "  默认账号:"
    echo "  管理员: admin / admin123"
    echo ""
    echo "  管理命令:"
    echo "  启动:  ./start.sh"
    echo "  停止:  ./stop.sh"
    echo "  日志:  $COMPOSE_CMD logs -f"
    echo "========================================="
}

# 主流程
main() {
    detect_os
    check_environment
    setup_env
    build_and_start
    show_info
}

main
```

---

# 第四阶段：Nginx配置（30分钟）

```nginx
# deploy/nginx/zhihire.conf

upstream frontend {
    server frontend:80;
}

upstream backend {
    server backend:8080;
}

upstream ai-service {
    server ai-service:8000;
}

# HTTP → HTTPS 重定向
server {
    listen 80;
    server_name zhihire.example.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS
server {
    listen 443 ssl http2;
    server_name zhihire.example.com;

    # SSL证书（生产环境替换为真实证书）
    ssl_certificate /etc/nginx/ssl/zhihire.crt;
    ssl_certificate_key /etc/nginx/ssl/zhihire.key;

    # 前端静态文件
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 后端API
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        # WebSocket支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_read_timeout 120s;
    }

    # AI服务
    location /ai-api/ {
        rewrite ^/ai-api/(.*) /$1 break;
        proxy_pass http://ai-service;
        proxy_read_timeout 300s;
    }

    # Swagger文档
    location /swagger-ui/ {
        proxy_pass http://backend;
    }

    # 上传文件访问
    location /api/files/ {
        alias /var/www/upload/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }

    # 安全头
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-Content-Type-Options "nosniff";
    add_header X-XSS-Protection "1; mode=block";
}
```

---

# 第19天验收标准

必须完成：

✅ 后端镜像构建成功

✅ 前端镜像构建成功

✅ AI服务镜像构建成功

✅ docker-compose.yml编排完成

✅ install.sh一键安装脚本

✅ 数据库自动初始化

✅ 银河麒麟V11上可运行

✅ Nginx反向代理配置

✅ 前端API代理正确

✅ 数据卷持久化

✅ Git已提交
