# aitee-backend

FastAPI + SQLAlchemy 2 + Alembic 后端，服务于 C 端 H5 / 微信 / 抖音、总部后台、店员端、伙伴端、加盟店端。

## 快速开始（Windows）

```cmd
cd D:\wp\waibao\aitee\backend
start.bat
```

`start.bat` 自动：
1. 建 `.venv`（不存在时）
2. 装 `requirements.txt`（首次）
3. 拷贝 `.env.example` → `.env`（首次）
4. 跑 `alembic upgrade head` 建表（首次）
5. `uvicorn` 起服务（`--reload`）

启动后：
- 服务：http://localhost:8200
- 文档：http://localhost:8200/docs
- 健康：http://localhost:8200/api/v1/health

停服务：`stop.bat`（按端口 8200 杀进程，调用根目录 `aitee\stop.bat 8200`）。

## 目录

```
backend\
├── app\
│   ├── core\        # config / db / security
│   ├── models\      # SQLAlchemy ORM
│   ├── schemas\     # Pydantic
│   ├── routers\
│   │   ├── c\       # /api/v1/*           C 端
│   │   └── admin\   # /api/v1/admin/*     总部后台
│   ├── services\    # 业务服务
│   ├── deps\        # 依赖注入（鉴权等）
│   └── main.py
├── alembic\         # 数据库迁移
├── scripts\         # seed 等
├── uploads\         # 本地文件存储
├── requirements.txt
├── alembic.ini
└── start.bat
```

## 鉴权双体系

- C 端 token：`Authorization: Bearer <c-jwt>`，密钥 `JWT_SECRET_C`
- B 端 token：`Authorization: Bearer <b-jwt>`，密钥 `JWT_SECRET_B`，含 `role` 字段（admin / partner / store / staff）

C/B 完全隔离，C 端 token 无法访问 admin 路径。

## 阶段 2 状态

- M1（当前）：骨架 + 健康检查
- M2：核心业务接口 + AI 三模式 + city-ip
- M3：分润 / 结算 / 对账 / BI
