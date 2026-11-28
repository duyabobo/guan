#!/usr/bin/env bash
# 关关雎鸠 一键部署脚本
# 用法：bash deploy.sh [start|stop|restart|logs|status|init-db|clear-db]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[INFO]${NC}  $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }
log_title() { echo -e "\n${CYAN}=== $* ===${NC}"; }

DEFAULT_SSL_CERT_HOST=/home/guan/service.pem
DEFAULT_SSL_KEY_HOST=/home/guan/service.key

env_value() {
    local key="$1"
    local line
    line="$(grep -E "^${key}=" .env | tail -n 1 || true)"
    printf '%s' "${line#*=}"
}

# ── 前置检查 ──────────────────────────────────────────────────────────────────
check_deps() {
    local missing=()
    for cmd in docker docker-compose; do
        command -v "${cmd}" &>/dev/null || missing+=("${cmd}")
    done
    if [[ ${#missing[@]} -gt 0 ]]; then
        log_error "缺少依赖: ${missing[*]}，请先安装后重试"
        exit 1
    fi
    log_info "依赖检查通过 (docker + docker-compose)"
}

# ── 环境变量文件 ──────────────────────────────────────────────────────────────
setup_env() {
    if [[ ! -f ".env" ]]; then
        if [[ -f ".env.example" ]]; then
            cp .env.example .env
            log_warn ".env 不存在，已从 .env.example 复制"
            log_warn "请编辑 .env 填写真实配置（微信/七牛/密钥等），然后重新运行 deploy.sh"
            exit 0
        else
            log_error ".env 和 .env.example 均不存在，无法继续"
            exit 1
        fi
    fi
    log_info "环境变量文件 .env 就绪"
}

# ── 目录初始化 ────────────────────────────────────────────────────────────────
setup_dirs() {
    mkdir -p log sql/init
    log_info "运行目录初始化完成 (log/, sql/init/)"

    if [[ -z "$(ls sql/init/*.sql 2>/dev/null)" ]]; then
        log_warn "sql/init/ 目录为空，MySQL 将以空库启动"
        log_warn "请将建表 DDL 放入 sql/init/ 目录（.sql 文件），首次建库时会自动执行"
    fi
}

# ── 线上证书必须是宿主机上的非空文件，再挂进容器 ────────────────────────────
ensure_ssl_mount() {
    local server_env cert key
    server_env="$(env_value SERVER_ENV)"
    cert="$(env_value SSL_CERT_HOST)"
    key="$(env_value SSL_KEY_HOST)"
    cert="${cert:-${DEFAULT_SSL_CERT_HOST}}"
    key="${key:-${DEFAULT_SSL_KEY_HOST}}"

    if [[ "${server_env}" == "online" ]]; then
        require_ssl_file "${cert}"
        require_ssl_file "${key}"
        log_info "HTTPS 证书就绪 (${cert})"
        return
    fi

    prepare_offline_ssl_file "${cert}"
    prepare_offline_ssl_file "${key}"
}

require_ssl_file() {
    local path="$1"
    if [[ -d "${path}" ]]; then
        log_error "证书路径是目录，请删掉后放上文件: ${path}"
        exit 1
    fi
    if [[ ! -s "${path}" ]]; then
        log_error "HTTPS 证书不存在或为空: ${path}"
        exit 1
    fi
}

prepare_offline_ssl_file() {
    local path="$1"
    if [[ -d "${path}" ]]; then
        log_error "证书路径是目录，请删掉后放上文件: ${path}"
        exit 1
    fi
    if [[ -f "${path}" ]]; then
        return
    fi
    case "${path}" in
        /*)
            log_warn "本机没有证书 ${path}，offline 不会读取；docker compose 挂载可能失败"
            ;;
        *)
            mkdir -p "$(dirname "${path}")"
            touch "${path}"
            log_info "offline 占位证书 ${path}"
            ;;
    esac
}

# ── 启动服务 ──────────────────────────────────────────────────────────────────
cmd_start() {
    log_title "启动服务"
    ensure_ssl_mount
    log_info "拉取基础镜像..."
    docker-compose pull mysql redis 2>/dev/null || true

    log_info "构建应用镜像并启动所有容器..."
    docker-compose up -d --build

    log_info "等待健康检查..."
    local timeout=60
    local elapsed=0
    while ! docker-compose ps | grep -q "app.*Up"; do
        sleep 3
        elapsed=$((elapsed + 3))
        if [[ ${elapsed} -ge ${timeout} ]]; then
            log_warn "应用容器启动超时，请检查日志: bash deploy.sh logs"
            break
        fi
    done

    echo ""
    cmd_status
    print_access_info
}

# ── 停止服务 ──────────────────────────────────────────────────────────────────
cmd_stop() {
    log_title "停止服务"
    docker-compose down
    log_info "所有容器已停止"
}

# ── 重启服务 ──────────────────────────────────────────────────────────────────
cmd_restart() {
    cmd_stop
    cmd_start
}

# ── 查看日志 ──────────────────────────────────────────────────────────────────
cmd_logs() {
    local service="${2:-app}"
    docker-compose logs -f --tail=100 "${service}"
}

# ── 等待 MySQL ────────────────────────────────────────────────────────────────
wait_mysql() {
    log_info "等待 MySQL 就绪..."
    local elapsed=0
    until docker-compose exec mysql mysqladmin ping -h localhost -u root \
        "-p$(grep MYSQL_ROOT_PASSWORD .env | cut -d= -f2)" --silent 2>/dev/null; do
        sleep 2
        elapsed=$((elapsed + 2))
        if [[ ${elapsed} -ge 60 ]]; then
            log_error "MySQL 启动超时，请检查: docker-compose logs mysql"
            exit 1
        fi
        log_info "  等待 MySQL... (${elapsed}s)"
    done
}

# ── 初始化数据库（DDL + 地点，默认不清用户数据）──────────────────────────────
cmd_init_db() {
    log_title "初始化数据库"
    wait_mysql
    log_info "执行初始化脚本..."
    python "${SCRIPT_DIR}/scripts/init_db.py"
}

# ── 清空账号、资料、活动。地区和地点保留 ─────────────────────────────────────
cmd_clear_db() {
    log_title "清空用户数据"
    wait_mysql
    log_info "执行清空脚本..."
    python "${SCRIPT_DIR}/scripts/clear_user_data.py"
}

# ── 查看状态 ──────────────────────────────────────────────────────────────────
cmd_status() {
    log_title "容器状态"
    docker-compose ps
}

# ── 访问地址提示 ──────────────────────────────────────────────────────────────
print_access_info() {
    local app_port
    app_port="$(grep -E '^APP_PORT=' .env | cut -d= -f2 || echo 8888)"

    echo ""
    log_info "┌──────────────────────────────────────────────┐"
    log_info "│  应用地址:          http://localhost:${app_port}     │"
    log_info "└──────────────────────────────────────────────┘"
}

# ── 主入口 ────────────────────────────────────────────────────────────────────
main() {
    log_title "关关雎鸠 部署脚本"
    check_deps

    local action="${1:-start}"

    case "${action}" in
        start)
            setup_env
            setup_dirs
            cmd_start
            ;;
        stop)
            cmd_stop
            ;;
        restart)
            setup_env
            cmd_restart
            ;;
        logs)
            cmd_logs "$@"
            ;;
        status)
            cmd_status
            ;;
        init-db)
            cmd_init_db
            ;;
        clear-db)
            cmd_clear_db
            ;;
        *)
            echo "用法: bash deploy.sh [start|stop|restart|logs|status|init-db|clear-db]"
            echo "  start    - 构建并启动所有服务（默认）"
            echo "  stop     - 停止并移除所有容器"
            echo "  restart  - 重启所有服务"
            echo "  logs     - 查看日志（默认 app，可指定服务名）"
            echo "  status   - 查看容器状态"
            echo "  init-db  - 幂等建表、迁移、补地点，不清用户数据"
            echo "  clear-db - 清空账号、资料、活动和登录态，地区和地点保留"
            exit 1
            ;;
    esac
}

main "$@"
