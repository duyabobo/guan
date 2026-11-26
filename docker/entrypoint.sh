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
under_review=${UNDER_REVIEW:-0}
list_max_distance_km=${LIST_MAX_DISTANCE_KM:-100}

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

[aliyun_sms]
aliyun_sms_access_key_id=${ALIYUN_SMS_ACCESS_KEY_ID:-}
aliyun_sms_access_key_secret=${ALIYUN_SMS_ACCESS_KEY_SECRET:-}
aliyun_sms_sign_name=${ALIYUN_SMS_SIGN_NAME:-}
aliyun_sms_verify_template_code=${ALIYUN_SMS_VERIFY_TEMPLATE_CODE:-}
aliyun_sms_notice_template_code=${ALIYUN_SMS_NOTICE_TEMPLATE_CODE:-}
EOF

echo "[entrypoint] Config ready. Filling weekend activities..."
python script/fill_weekend_activities.py || echo "[entrypoint] weekend activity fill failed, continue starting"

echo "[entrypoint] Starting cron..."
cron

echo "[entrypoint] Starting application..."
exec python main.py
