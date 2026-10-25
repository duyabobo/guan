#!/usr/bin/env bash
# 容器启动入口：从环境变量生成配置文件后启动应用
set -euo pipefail

CONFIG_FILE="/app/app.conf"

echo "[entrypoint] Generating ${CONFIG_FILE} from environment variables..."

cat > "${CONFIG_FILE}" << EOF
[global]
port=${PORT:-8888}
server=${SERVER_ENV:-offline}
debug=${DEBUG:-false}
cookie_secret=${COOKIE_SECRET:-change_me_in_production}

[mysql]
username=${MYSQL_USER:-guan}
password=${MYSQL_PASSWORD:-guan123}
host=${MYSQL_HOST:-mysql}
port=${MYSQL_PORT:-3306}
database=${MYSQL_DATABASE:-guan}

[redis]
host=${REDIS_HOST:-redis}
port=${REDIS_PORT:-6379}
password=${REDIS_PASSWORD:-}

[weixin]
appid=${WX_APPID:-}
secret=${WX_SECRET:-}
token=${WX_TOKEN:-}
EncodingAESKey=${WX_ENCODING_AES_KEY:-}
subscribe_template_id=${WX_SUBSCRIBE_NOTI_TID:-}

[volc]
volc_ark_api_key=${VOLC_ARK_API_KEY:-}
volc_ark_api_base=${VOLC_ARK_API_BASE:-https://ark.cn-beijing.volces.com/api/v3}
volc_ark_model=${VOLC_ARK_MODEL:-doubao-seed-2-1-lite-260915}

[qiniu]
access_key=${QINIU_ACCESS_KEY:-}
secret_key=${QINIU_SECRET_KEY:-}
head_img_bucket_name=${QINIU_BUCKET:-}
EOF

echo "[entrypoint] Config ready. Starting application..."
exec python main.py
