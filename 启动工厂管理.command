#!/bin/bash

# 双击此文件即可启动工厂生产协同系统
set -u
cd "$(dirname "$0")"

ADMIN_FILE="$(pwd)/.factory-admin.env"
if [ ! -f "$ADMIN_FILE" ]; then
  echo "首次启动需要设置一个管理员账号。"
  read -r -p "管理员账号: " ADMIN_USERNAME
  read -r -s -p "管理员密码（至少 8 位）: " ADMIN_PASSWORD
  echo
  if [ "${#ADMIN_PASSWORD}" -lt 8 ]; then
    echo "密码至少需要 8 位。"
    read -r -p "按回车键退出..."
    exit 1
  fi
  printf 'export ADMIN_USERNAME=%q\nexport ADMIN_PASSWORD=%q\n' "$ADMIN_USERNAME" "$ADMIN_PASSWORD" > "$ADMIN_FILE"
  chmod 600 "$ADMIN_FILE"
fi
source "$ADMIN_FILE"

PORT="${FACTORY_PORT:-5001}"
URL="http://127.0.0.1:${PORT}/"

if ! command -v python3 >/dev/null 2>&1; then
  echo "未找到 Python 3，请先安装 Python 3。"
  read -r -p "按回车键退出..."
  exit 1
fi

if [ ! -d ".venv" ]; then
  echo "首次运行，正在准备运行环境..."
  python3 -m venv .venv || exit 1
fi

PYTHON_BIN="$(pwd)/.venv/bin/python"

if ! "$PYTHON_BIN" -c "import flask, flask_sqlalchemy, openpyxl, psycopg" >/dev/null 2>&1; then
  echo "正在安装系统依赖，首次运行可能需要一点时间..."
  "$PYTHON_BIN" -m pip install -r requirements.txt || exit 1
fi

echo "工厂生产协同系统正在启动..."
echo "访问地址：${URL}"
open "$URL"

"$PYTHON_BIN" -c "from app import app; app.run(host='127.0.0.1', port=${PORT}, debug=False)"
