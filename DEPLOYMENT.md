# 工厂生产协同系统部署说明

## 本地运行

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

## 联网部署

使用 Render、Railway 或 Fly.io 时：

1. 将项目上传到 GitHub 私有仓库。
2. 创建一个 PostgreSQL 数据库，并把连接地址设置为 `DATABASE_URL`。
3. 设置随机的 `SECRET_KEY`。
4. 设置 `ADMIN_USERNAME` 和 `ADMIN_PASSWORD`，它们用于首次创建管理员账号；密码不要写入代码仓库。
5. 使用 `Procfile` 中的 Gunicorn 启动命令。
6. 部署完成后，在浏览器中通过平台生成的 HTTPS 链接访问。

当前系统会在没有 `DATABASE_URL` 时继续使用本地 `factory.db`，方便开发；线上多人协同时必须配置 PostgreSQL。SQLite 数据库文件和本地 `backups/` 目录不应作为线上唯一数据存储。

## 权限规则

- 未登录：可以查看订单、工序、物料、打卡和统计数据。
- 编辑者：登录后可以修改生产数据。
- 管理员：额外可以在“账号管理”中创建协同账号。
