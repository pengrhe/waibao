# @aitee/portal

aitee 业务端 H5（合并 partner + store + staff 三个角色）。

## 启动

```cmd
cd D:\wp\waibao\aitee\b-portals
npm install
npm run dev          # http://localhost:8203
```

## 角色模块

每个角色一个目录，互不耦合。新增角色 = 加一个 `modules/<role>/` + 在 `modules/index.ts` 注册。

```
src/modules/<role>/
├── index.ts        # PortalModule 配置：role/label/brand/menus/routes/defaultUser
└── Dashboard.vue   # 首页（其余子页 M2 实装）
```

## 登录流程

1. `Login.vue` 顶部 van-tabs 选角色 → 自动填默认账号
2. 提交 → 调 `/api/v1/{role}/auth/login` → 拿 token + user.role
3. `useAuthStore` 持久化到 localStorage
4. 路由跳 `/{role}/dashboard`
5. 后续每次进入 `/x/...` 路由，守卫检查 `auth.user.role === x`，否则跳回自己 dashboard

## 数据流

```
登录页 → POST /api/v1/<role>/auth/login → token + user{role}
                                         ↓
                       useAuthStore.setAuth()  (localStorage)
                                         ↓
                       router.beforeEach 注入对应 role 路由
                                         ↓
                  Shell.vue 取 auth.user.role → 渲染 brand+menus
                                         ↓
                       modules/<role>/Dashboard.vue 渲染
```
