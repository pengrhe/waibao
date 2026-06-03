# aitee b-portals

B 端业务 H5（合并版，npm workspaces monorepo）：

```
b-portals\
├── apps\
│   └── portal\     # 业务端：合并 联营伙伴 + 加盟店 + 店员（端口 8203）
│       └── src\
│           ├── modules\
│           │   ├── partner\   # 看板/二维码/分润/提现
│           │   ├── store\     # 门店/设备/结算/优惠
│           │   └── staff\     # 订单/核销/录单/设备
│           ├── views\
│           │   ├── Login.vue  # 多角色 tabs 统一登录页
│           │   └── Shell.vue  # 按 token role 动态渲染 brand+menus
│           └── router\        # /:role/* 路由表 + 越权拦截
└── packages\
    └── shared\    # 共享：axios / pinia auth / 公共布局组件 / 类型
```

> 历史背景：M1 初始版 partner-web / store-web / staff-web 三个独立项目；后选 B 方案合并为单一 `portal`，按角色分模块。`admin` 仍独立（PC 形态）。

## 启动

```cmd
cd D:\wp\waibao\aitee\b-portals
npm install                      # 首次
npm run dev                      # http://localhost:8203
```

或在根目录用 `restart.bat portal` / `stop.bat 8203`。

需 backend 已起在 8200。

## 默认账号（seed 写入）

| 角色 | 用户名 | 密码 | 备注 |
|---|---|---|---|
| partner | p_zhang / p_li / p_wang | partner123 | 联营伙伴 |
| store | s_sz01 / s_cs01 | store123 | 加盟店（s_sz01 统一结算 / s_cs01 自主结算）|
| staff | st_sz01_a / st_sz01_b / st_cs01_a | staff123 | 店员 |

登录页顶部 tabs 切换角色，每个 tab 已默认填好示例账号。

## 路由

| URL | 角色 | 说明 |
|---|---|---|
| `/login` | 公开 | 多角色统一登录（已登录自动跳 dashboard） |
| `/partner/dashboard /qr /profit /withdraw` | partner | 联营伙伴 |
| `/store/dashboard /devices /settle /promo` | store | 加盟店 |
| `/staff/dashboard /scan /manual /devices` | staff | 店员 |

**越权拦截**：partner 账号访问 `/store/...` 会被路由守卫自动跳回 `/partner/dashboard`。

## 共享 shared 包

`@aitee/shared` 复用：
- `getHttp()` axios + 自动带 token + 业务错误码处理
- `useAuthStore()` pinia 鉴权 + localStorage 持久化
- `PortalShell` 顶栏 + 底 tabbar 公共骨架（按品牌 brand 渲染）
- `PagePlaceholder` 占位页
- `createPortalRouter()` 单角色场景的快捷路由（本 portal 不用，因为要按 role 动态注入）

## 新增角色

新增 B 端角色（如 supplier 供应商）只需：
1. `src/modules/supplier/index.ts` 声明 `brand + menus + routes`
2. `src/modules/supplier/Dashboard.vue` 写首页
3. 在 `src/modules/index.ts` 注册
4. backend 加 `/api/v1/supplier/auth/login` 路由

无需新建项目、无需调脚本。
