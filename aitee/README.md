# aitee

AI T 恤 / 帆布包定制平台 — 6 端 + 后端的完整生态。

## 端形态地图（B 方案确定版）

| 子项目 | 端口（dev） | 形态 | 上线方式 | 业务定位 |
|---|---|---|---|---|
| **backend** | 8200 | Python FastAPI | uvicorn/gunicorn 跑 8200，nginx 反代 `api.aitee.com` | 全平台后端 |
| **frontend** | 8201 | Vue3 + Vant 浏览器 H5 | nginx 静态托管 `m.aitee.com` | C 端浏览器入口（**M2 起冻结新功能**） |
| **admin** | 8202 | Vue3 + Element Plus PC | nginx 静态托管 `admin.aitee.com` | 总部后台（21 菜单：商品/订单/财务/BI/分润审核 等） |
| **portal** | 8203 | Vue3 + Vant 移动 H5 | nginx 静态托管 `biz.aitee.com` | B 端业务端，**partner / store / staff 合一**，登录页 tabs 选角色 |
| **miniapp** | 8206 (仅开发) | uniapp Vue3 | `build:mp-weixin` / `build:mp-toutiao` 上传商店 | **C 端微信小程序 + 抖音小程序**（一份代码两端），主战场 |

正式环境 5 个独立部署单元（backend + 3 个 H5 + 2 个小程序包），**`miniapp` 的 H5 模式 8206 不上线**（与 frontend 重复）。

## C 端策略：frontend vs miniapp（B 方案）

- **微信/抖音小程序** = `miniapp`，主战场，业务页面 M2 起全部在这里实装
- **浏览器 H5** = `frontend`，已完工，M2 起仅维护，不加新业务
- 同一个 C 端用户在不同环境走不同入口，登录后 token 来自同一后端

> 不再做 `miniapp h5 build` 上线，避免和 frontend 重复维护。

## 一键启动 / 停 / 状态

```cmd
start-all.bat       一键起全部 5 端（独立 cmd 窗口）
status.bat          看 5 端口运行状态
stop.bat            停全部 5 端
stop.bat 8200       停指定端口
restart.bat backend 重启某个端（backend/frontend/admin/portal/miniapp）
```

## 演示账号汇总（seed 写入）

| 端 | 入口 | 账号 | 密码 |
|---|---|---|---|
| admin | http://localhost:8202 | `admin` | `admin123` |
| portal · 联营伙伴 | http://localhost:8203 | `p_zhang` / `p_li` / `p_wang` | `partner123` |
| portal · 加盟店 | http://localhost:8203 | `s_sz01` (统一) / `s_cs01` (自主) | `store123` |
| portal · 店员 | http://localhost:8203 | `st_sz01_a` / `st_sz01_b` / `st_cs01_a` | `staff123` |
| frontend | http://localhost:8201 | 无需登录（mock） | — |
| miniapp-h5 | http://localhost:8206 | mock 一键登录 | — |

## 阶段进度

- **M1（当前完成）**：6 端骨架启动 + 登录闭环，38 张表 + seed
- **M2**：C 端业务接口 / AI 三模式 / 订单引擎；admin 8 个 CRUD；miniapp 业务页面实装
- **M3**：分润 / 结算 / 对账 / BI / 提现审核 / 设备 mock SDK

详见 `c:\Users\admin\.cursor\plans\aitee_阶段_2_全并行_*.plan.md`。

## 关键决策记录

| 日期 | 决策 | 原因 |
|---|---|---|
| 2026-05-26 | 端口从 5173/5174.../8000 改为 8200-8206 一体 | 跟其他项目冲突，统一端口段 |
| 2026-05-26 | B 端三个项目 partner/store/staff 合并为 portal | 三端形态相同，共享 80% 代码，5 端比 7 端易维护 |
| 2026-05-26 | miniapp H5 模式不上线 | 与 frontend 重复 |
| 2026-05-26 | bcrypt 5.0 → 4.0.1 | 与 passlib 1.7.4 兼容 |
| 2026-05-26 | uvicorn 去掉 --reload | reloader+worker 双进程让 stop 复杂化 |

## 安全要点

- **严禁** `Get-Process python | Stop-Process` / `taskkill /IM python.exe`：机器上同时跑着其他 Python 服务（如 8000 端口的服务），脚本统一按端口号杀，仅锁 8200-8206
- 网络下载（npm/pip）统一走代理 `127.0.0.1:7890`
- OpenRouter API key 已入 `backend\.env`（gitignore），数据库 `model_channels` 表同步
