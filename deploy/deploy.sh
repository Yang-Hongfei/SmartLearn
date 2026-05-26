#!/bin/bash
# SmartLearn 一键部署脚本 — Ubuntu Server 24.04 LTS
# 用法：chmod +x deploy.sh && ./deploy.sh --mysql-password "YourPass" --deepseek-key "sk-xxx"

set -e

APP_DIR="/opt/smartlearn"
MYSQL_PASSWORD=""
DEEPSEEK_KEY=""

echo "====================================="
echo " SmartLearn 一键部署 (Ubuntu 24.04)"
echo "====================================="

# ---- 参数 ----
while [[ $# -gt 0 ]]; do
    case $1 in
        --mysql-password) MYSQL_PASSWORD="$2"; shift 2 ;;
        --deepseek-key) DEEPSEEK_KEY="$2"; shift 2 ;;
        *) echo "未知参数: $1"; exit 1 ;;
    esac
done

if [ -z "$MYSQL_PASSWORD" ]; then
    echo "用法: ./deploy.sh --mysql-password <密码> [--deepseek-key <key>]"
    exit 1
fi

# ---- 1. 环境检查 ----
echo "[1/8] 检查环境..."
command -v java >/dev/null 2>&1 || { echo "请先安装 Java: sudo apt install openjdk-17-jdk -y"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "请先安装 Python 3: sudo apt install python3 -y"; exit 1; }
command -v node >/dev/null 2>&1 || { echo "请先安装 Node.js: sudo apt install nodejs npm -y"; exit 1; }
command -v nginx >/dev/null 2>&1 || { echo "请先安装 Nginx: sudo apt install nginx -y"; exit 1; }
echo "  OK"

# ---- 2. 构建前端 ----
echo "[2/8] 构建前端..."
cd "$(dirname "$0")/../frontend"
npm install --silent
npm run build
echo "  OK"

# ---- 3. 构建 SpringBoot ----
echo "[3/8] 构建 SpringBoot..."
cd "$(dirname "$0")/../springboot-backend"
mvn clean package -DskipTests -q
echo "  OK"

# ---- 4. 安装 FastAPI 依赖 ----
echo "[4/8] 安装 FastAPI 依赖..."
cd "$(dirname "$0")/../fastapi-ai"
pip3 install -r requirements.txt -q
echo "  OK"

# ---- 5. 配置 ----
echo "[5/8] 配置..."

# .env
if [ -n "$DEEPSEEK_KEY" ]; then
    cat > .env << EOF
DEEPSEEK_API_KEY=$DEEPSEEK_KEY
EMBEDDING_API_KEY=$DEEPSEEK_KEY
LLM_MODEL=deepseek-chat
CHROMA_PATH=./chroma_data
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=Neo4j123456
EOF
    echo "  API Key 已配置"
else
    echo "  跳过 API Key（启动后在前端配置）"
fi

# ---- 6. 部署文件 ----
echo "[6/8] 部署文件..."
mkdir -p $APP_DIR
cp -r "$(dirname "$0")/../frontend/dist" $APP_DIR/frontend-dist
cp "$(dirname "$0")/../springboot-backend/target/smartlearn-backend-0.1.0.jar" $APP_DIR/
cp -r "$(dirname "$0")/../fastapi-ai" $APP_DIR/
echo "  OK"

# ---- 7. Nginx 配置 ----
echo "[7/8] 配置 Nginx..."
cat > /etc/nginx/sites-available/smartlearn << 'NGINX'
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
NGINX

# Enable the site (Ubuntu uses sites-available/sites-enabled)
ln -sf /etc/nginx/sites-available/smartlearn /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

nginx -t
systemctl restart nginx
echo "  OK"

# ---- 8. Systemd 服务 ----
echo "[8/8] 注册服务..."

cat > /etc/systemd/system/smartlearn-springboot.service << EOF
[Unit]
Description=SmartLearn SpringBoot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$APP_DIR
ExecStart=/usr/bin/java -jar $APP_DIR/smartlearn-backend-0.1.0.jar
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

cat > /etc/systemd/system/smartlearn-fastapi.service << EOF
[Unit]
Description=SmartLearn FastAPI
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$APP_DIR/fastapi-ai
ExecStart=/usr/bin/python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=on-failure
RestartSec=10
Environment="PATH=/usr/bin:/usr/local/bin"

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable smartlearn-fastapi smartlearn-springboot
systemctl restart smartlearn-fastapi smartlearn-springboot

# ---- 防火墙 ----
ufw allow http 2>/dev/null || true
ufw --force enable 2>/dev/null || true

echo ""
echo "====================================="
echo " 部署完成！"
echo " 访问 http://$(hostname -I | awk '{print $1}')"
echo ""
echo " 服务管理："
echo "   systemctl status smartlearn-fastapi"
echo "   systemctl status smartlearn-springboot"
echo "   journalctl -u smartlearn-fastapi -f"
echo "====================================="
