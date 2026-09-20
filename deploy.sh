#!/usr/bin/env bash
# 关关雎鸠 一键部署脚本
# 用法：bash deploy.sh [start|stop|restart|logs|status]
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

# ── 启动服务 ──────────────────────────────────────────────────────────────────
cmd_start() {
    log_title "启动服务"
    log_info "拉取基础镜像..."
    docker-compose pull mysql redis rabbitmq 2>/dev/null || true

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

# ── 查看状态 ──────────────────────────────────────────────────────────────────
cmd_status() {
    log_title "容器状态"
    docker-compose ps
}

# ── 访问地址提示 ──────────────────────────────────────────────────────────────
print_access_info() {
    local app_port
    app_port="$(grep -E '^APP_PORT=' .env | cut -d= -f2 || echo 8888)"
    local mq_port
    mq_port="$(grep -E '^RABBITMQ_MGMT_PORT=' .env | cut -d= -f2 || echo 15672)"

    echo ""
    log_info "┌──────────────────────────────────────────────┐"
    log_info "│  应用地址:          http://localhost:${app_port}     │"
    log_info "│  RabbitMQ 管理界面: http://localhost:${mq_port}    │"
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
        *)
            echo "用法: bash deploy.sh [start|stop|restart|logs|status]"
            echo "  start   - 构建并启动所有服务（默认）"
            echo "  stop    - 停止并移除所有容器"
            echo "  restart - 重启所有服务"
            echo "  logs    - 查看日志（默认 app，可指定服务名）"
            echo "  status  - 查看容器状态"
            exit 1
            ;;
    esac
}

main "$@"
