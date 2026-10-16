FROM docker.1panel.live/library/python:3.11-slim

WORKDIR /app

# 安装系统依赖（pymysql/gcc/gevent 编译需要）
# deb.debian.org 从构建网络不可达，改走中科大镜像
RUN sed -i 's|deb.debian.org|mirrors.ustc.edu.cn|g' /etc/apt/sources.list.d/debian.sources \
    && apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 先复制依赖文件，利用 Docker 层缓存
COPY requirements.txt .
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt

# 复制项目代码
COPY . .

# 创建日志目录
RUN mkdir -p /app/log

# 配置文件名由环境变量 CONFNAME 控制，entrypoint 会生成对应 .conf 文件
ENV CONFNAME=app
ENV LOG_DIR=/app/log
ENV PYTHONUNBUFFERED=1

EXPOSE 8888

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
