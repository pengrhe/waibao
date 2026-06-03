# aitee-miniapp

uniapp Vue3 项目，一份代码编译微信小程序 + 抖音小程序 + H5 预览。

## 启动

```cmd
cd D:\wp\waibao\aitee\miniapp
npm install
npm run dev:h5            # http://localhost:8206
npm run dev:mp-weixin     # 编译产物在 dist/dev/mp-weixin，用微信开发者工具打开
npm run dev:mp-toutiao    # 编译产物在 dist/dev/mp-toutiao，用抖音开发者工具打开
```

需后端已起在 http://127.0.0.1:8200。H5 走 vite proxy；小程序在 manifest.json 的 mp-weixin/mp-toutiao 下需要把请求域名加白。

停服务：`stop.bat`（按 8206 杀 H5 dev server）。

## 目录

```
miniapp/src
├── pages/
│   ├── index/        # 首页（tab）
│   ├── gallery/      # 印花库（tab）
│   ├── cart/         # 购物车（tab）
│   ├── mine/         # 我的（tab）
│   ├── login/        # mock 微信/抖音登录
│   ├── editor/       # AI 定制编辑器（M2 实装）
│   ├── ai-create/    # AI 创作三模式（M2 实装）
│   └── city-ip/      # AI 城市 IP（M2 实装）
├── store/auth.ts     # pinia 鉴权
├── utils/request.ts  # uni.request 封装
├── utils/env.ts      # API base 平台兼容
├── manifest.json     # 双端 appid + h5 devServer 5179
└── pages.json        # 路由 + tabBar
```

## 部署策略（重要）

按 **B 方案**：

| 编译模式 | 命令 | 是否上线 | 说明 |
|---|---|---|---|
| `dev:mp-weixin` / `build:mp-weixin` | npm | **上线** | 微信小程序商店，**主战场** |
| `dev:mp-toutiao` / `build:mp-toutiao` | npm | **上线** | 抖音小程序，docx 要求 |
| `dev:h5` / `build:h5` | npm | **不上线** | 仅开发调试用，避免每次开微信工具；浏览器 H5 用户走 `frontend` 项目（端口 8201），不重复部署 |

> **正式环境 8206 端口不存在**，仅本地开发期有。

## M1 状态

- tabBar 4 项已配
- 首页能调后端 `/api/v1/health` 验证联通
- 微信小程序 appid / 抖音小程序 appid 暂用占位符（上架前替换）
- 登录走 mock；M2 接微信 `wx.login` + 抖音 `tt.login` + 后端 `/api/v1/user/auth/login/wx|dy`

## M2 待办

- 完整业务页面（订单、地址、优惠券、设计稿、编辑器、AI 三模式、城市 IP）
- 真微信/抖音登录 + mock 支付页
- 门店扫码下单页（partner_qr / store_qr / staff_verify_qr）
