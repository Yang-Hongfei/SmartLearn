# SmartLearn Ubuntu Server 24.04 LTS 部署指南

## 架构

```
浏览器 → Nginx(:80) → Vue 静态文件
                    → /api/* → SpringBoot(:8080) → FastAPI(:8000) → DeepSeek
                                                    ↓
                                              MySQL(:3306)
                                              Neo4j(:7687)
```

## 一、环境准备

### 1.1 基础工具

```bash
sudo apt update
sudo apt install -y wget vim git curl
```

### 1.2 安装 Java（OpenJDK 17）

Spring Boot 2.7 兼容 Java 8-17，Ubuntu 24.04 推荐装 OpenJDK 17：

```bash
sudo apt install -y openjdk-17-jdk
java -version
```

### 1.3 Python 3

Ubuntu 24.04 自带 Python 3.12，安装 pip：

```bash
sudo apt install -y python3 python3-pip python3-venv
python3 --version
```

### 1.4 安装 Node.js 18+

```bash
sudo apt install -y nodejs npm
node --version
```

如需更新版本：

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo bash -
sudo apt install -y nodejs
```

### 1.5 安装 MySQL 8

```bash
sudo apt install -y mysql-server
sudo systemctl start mysql
sudo systemctl enable mysql
```

MySQL 初始化：

```bash
sudo mysql
```

```sql
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'YourPassword666!';
FLUSH PRIVILEGES;
CREATE DATABASE smartlearn DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

导入表结构：

```bash
mysql -u root -p smartlearn < springboot-backend/src/main/resources/db/schema.sql
```

### 1.6 Neo4j（可选，知识图谱需要）

```bash
sudo apt install -y docker.io
sudo systemctl start docker

sudo docker run -d --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/Neo4j123456 \
  neo4j:4.4
```

## 二、构建打包

### 2.1 前端

```bash
cd frontend
npm install
npm run build
# 产出 dist/ 目录
```

### 2.2 SpringBoot

部署前修改 `springboot-backend/src/main/resources/application.yml`：

```yaml
spring:
  datasource:
    password: 你的MySQL密码        # 改这里

smartlearn:
  ai:
    base-url: http://127.0.0.1:8000  # 改这里（部署用 127.0.0.1）
```

构建：

```bash
cd springboot-backend
mvn clean package -DskipTests
# 产出 target/smartlearn-backend-0.1.0.jar
```

### 2.3 FastAPI

```bash
cd fastapi-ai
pip3 install -r requirements.txt
# 配置 .env（或启动后在前端设置 API Key）
```

`.env` 模板：

```env
DEEPSEEK_API_KEY=sk-你的Key
EMBEDDING_API_KEY=sk-你的Key
LLM_MODEL=deepseek-chat
CHROMA_PATH=./chroma_data
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=Neo4j123456
```

## 三、部署

假设项目目录为 `/opt/smartlearn`：

```bash
sudo mkdir -p /opt/smartlearn

# 前端静态文件
sudo cp -r frontend/dist /opt/smartlearn/frontend-dist

# SpringBoot JAR
sudo cp springboot-backend/target/smartlearn-backend-0.1.0.jar /opt/smartlearn/

# FastAPI
sudo cp -r fastapi-ai /opt/smartlearn/
```

### 3.1 配置 Nginx

```bash
sudo apt install -y nginx
```

创建 `/etc/nginx/sites-available/smartlearn`：

```nginx
server {
    listen 80;
    server_name _;

    root /opt/smartlearn/frontend-dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Api-Key $http_x_api_key;
        proxy_read_timeout 600s;
        proxy_connect_timeout 30s;
    }
}
```

启用站点：

```bash
sudo ln -s /etc/nginx/sites-available/smartlearn /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### 3.2 Systemd 服务

**SpringBoot** — 创建 `/etc/systemd/system/smartlearn-springboot.service`：

```ini
[Unit]
Description=SmartLearn SpringBoot
After=network.target mysql.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/smartlearn
ExecStart=/usr/bin/java -jar /opt/smartlearn/smartlearn-backend-0.1.0.jar
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**FastAPI** — 创建 `/etc/systemd/system/smartlearn-fastapi.service`：

```ini
[Unit]
Description=SmartLearn FastAPI
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/smartlearn/fastapi-ai
ExecStart=/usr/bin/python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=on-failure
RestartSec=10
Environment="PATH=/usr/bin:/usr/local/bin"

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl start smartlearn-fastapi smartlearn-springboot
sudo systemctl enable smartlearn-fastapi smartlearn-springboot
```

### 3.3 防火墙

Ubuntu 使用 `ufw`：

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw --force enable
sudo ufw status
```

## 四、验证

```bash
# 检查服务状态
systemctl status smartlearn-fastapi smartlearn-springboot nginx

# 测试接口
curl http://127.0.0.1:8000/api/health
curl http://127.0.0.1:8080/api/questions/count
curl http://127.0.0.1/
```

浏览器访问 `http://服务器IP`，进入首页后点击右上角齿轮图标配置 DeepSeek API Key 即可使用 AI 功能。

## 五、更新部署

```bash
cd /path/to/project

# 前端
cd frontend && npm run build && sudo cp -r dist/* /opt/smartlearn/frontend-dist/

# 后端
cd springboot-backend && mvn clean package -DskipTests
sudo systemctl stop smartlearn-springboot
sudo cp target/smartlearn-backend-0.1.0.jar /opt/smartlearn/
sudo systemctl start smartlearn-springboot

# FastAPI
cd fastapi-ai
sudo systemctl restart smartlearn-fastapi
```

## 六、日志

```bash
journalctl -u smartlearn-fastapi -f
journalctl -u smartlearn-springboot -f
tail -f /var/log/nginx/access.log
```

## 七、一键部署脚本

```bash
chmod +x deploy/deploy.sh
./deploy/deploy.sh --mysql-password "你的密码" --deepseek-key "sk-xxx"
```

DeepSeek Key 可选，跳过则在启动后通过前端设置。

## 八、生产环境建议

- 在 `application.yml` 中修改数据库密码，不要用默认密码
- 配置 Nginx HTTPS（Let's Encrypt + certbot）
- FastAPI 只监听 `127.0.0.1`（不对外暴露 8000 端口）
- MySQL 绑定 `127.0.0.1`：编辑 `/etc/mysql/mysql.conf.d/mysqld.cnf`，设 `bind-address = 127.0.0.1`
- 定期备份 MySQL：`mysqldump -u root -p smartlearn > backup.sql`