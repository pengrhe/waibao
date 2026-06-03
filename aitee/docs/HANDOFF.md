# aitee 项目交接文档（截至 2026-05-27）

> 本文档用于把开发进展同步给新的 Cursor 会话/新成员。新会话开局只需 `@aitee/docs/HANDOFF.md` 即可获取完整上下文。
> 原始详细聊天记录：`[aitee 8206 对齐 8201](c4b65c63-6ece-4ac4-af3c-fab04b1404c5)`

---

## 1. 项目结构与端口

| 端口 | 服务 | 路径 | 技术栈 |
|---|---|---|---|
| 8200 | aitee-backend | `aitee/backend` | FastAPI + SQLAlchemy 2 + SQLite，路由前缀 `/api/v1` |
| 8201 | aitee-frontend | `aitee/frontend` | Vue3 + Vant + Vite，**C 端 H5 demo**（产品级，视觉打磨过） |
| 8202 | aitee-admin | `aitee/admin` | 管理后台 |
| 8203 | aitee-portal | `aitee/b-portals` | B 端门户（合作商/门店/员工） |
| 8206 | aitee-miniapp（H5 预览） | `aitee/miniapp` | uniapp + Vue3 + Vite，**目标三端：H5 / 微信小程序 / 抖音小程序** |

启动：`aitee/start-all.bat`；停止：`aitee/stop.bat`；状态：`aitee/status.bat`；单独重启：`aitee/restart.bat <backend|frontend|admin|portal|miniapp>`

---

## 2. M2 已完成的全部功能

### 后端（`aitee/backend`）
- C 端业务 API 全套：home/banners、topics、ai/styles、ai/generate（OpenRouter `google/gemini-3-pro` + fallback）、city-ip/popular、city-ip/hints、city-ip/{city}、city-ip/{city}/regenerate、products、patterns、designs、cart、orders、coupons、messages、qr、addresses、user/profile、user/prefs、payments/mock/notify
- 订单引擎：状态机 `pending_pay → paid/pending_print → printing → printed/pending_pickup → completed`（+ `canceled / refunded`）
- mock 支付：`payments/mock/notify` 触发订单状态推进
- Admin CRUD 全面（商品/印花/分类/优惠券模板/banner/topic/订单/用户/打印站点等）
- 多平台登录通道：`wx_app / dy_app / h5`，所有渠道都接 mock code → 颁发 JWT

### 前端 H5（`aitee/frontend`，端口 8201）
- 完整 14 个业务页 + 5 个公共组件（`BrandHeader / AppTabbar / Countdown / NavBar / EditorLayer`）
- 全局样式：`src/assets/styles/variables.scss`（主色 #FF4D4F、warm 渐变、间距 4/8/12/16/24、圆角 12/16/pill、阴影 sm/md/lg）

### miniapp（`aitee/miniapp`，端口 8206 是 H5 预览）
- 17 个页面（首页 / 编辑器 / AI 创作 / 城市 IP / 印花库 / 商品列表 / 商品详情 / 购物车 / 结算 / 订单列表 / 订单详情 / 我的 / 地址列表 / 地址编辑 / 优惠券 / 消息 / 登录）
- 公共组件：`BrandHeader / Countdown / SectionHead`
- 平台适配封装：`src/utils/platform.ts`（`getPlatformLoginCode / setShareInfo / requestSubscribe / WX_TPL / mockPay / allowGuestBrowse / isWechat / isDouyin / isH5`）
- 渠道 header：`request.ts` 所有请求自动带 `X-Aitee-Channel: dy_app|wx_app|h5`
- 全局分享：`App.vue` 注入 `onShareAppMessage / onShareTimeline`，页面用 `setShareInfo()` 上报
- 抖音游客模式：`mine` 页未登录时显示「抖音游客模式 · 浏览免登录」

### 端到端验收
- `aitee/scripts/m2_smoke.py` 跑通：C 端 mock 登录 → profile → 商品/印花 → 加购 → 下单 → mock 支付 → 消息中心 → AI 生成 4 张 → 城市 IP 详情 → Admin 登录 + CRUD 抽查
- 已修：Python 脚本 UTF-8 编码（Windows GBK 报错）、`pay_amount` → `amount_total` 字段对齐

---

## 3. 本轮（5/27）刚做的：8206 视觉对齐 8201

### 痛点
8201（frontend）是产品级 demo，做了几周。8206（miniapp H5 预览）原来只是路由占位、功能能跑，**视觉密度差距巨大**。用户决定：以 8201 为基准重做 miniapp 全部核心页，H5 优先，小程序端兼容性后续单独处理。

### 改动清单

**基础设施**
- `miniapp/src/styles/variables.scss` + `global.scss`：完整复制 8201 设计令牌
- `miniapp/vite.config.ts` 重写：scss `additionalData`、`@/` 别名、`/api` proxy 到 8200、自定义中间件把 `/static/*` 映射到 `src/static/`（**修复 uniapp vite 默认不把 src/static 当 publicDir 的问题**）
- `miniapp/src/utils/format.ts` 新增（fmtPrice/fmtTime/fmtCountdown/maskPhone + 订单状态 i18n）
- `miniapp/src/components/`：`BrandHeader.vue`、`Countdown.vue`、`SectionHead.vue`
- `miniapp/src/static/img/{entry,home,patterns}/*.png`：从 `frontend/public/assets/img/` 拷贝 19 张图
- `miniapp/src/pages.json`：所有业务页加 `navigationStyle: custom`（让自定义 BrandHeader 顶上去）

**17 个页面全部按 8201 视觉重写**（详见聊天历史的逐页对比表）：
- `index/index` — Hero 240px + 打字机 Prompt CTA + 5 卡 Bento（含 CSS 城市天际线）+ 新人券倒计时 + 案例 feed + Topic 横滚
- `editor/index` — sticky header + 颜色色块 + T 恤 CSS mockup（脖子+袖子+暗色切换）+ 安全区虚线 + movable-view 图层 + 右侧 4 浮按钮 + 左下撤销重做 + 4 工具栏 + 价格+加购底栏 + 印花/文字/尺码 3 弹层
- `ai-create/index` — 三模式 segment + 参考图选择 + textarea+presets + 风格 chip + pulse bubble + 渐变进度条 + 结果 grid（fallback 标签）
- `city-ip/index` — 紫渐变搜索区 + 热门 chip + 城市 Hero + 风格权重 segmented bar + 文化元素 chip 增删 + 黑色重新生成 CTA + 三类 tab + 网格
- `gallery / product-list / product-detail / cart / checkout / orders / order-detail / mine / addresses / address-edit / coupons / messages / login`

### 验收
- 17 个页面 200 编译通过，无 lint 错误
- `/static/img/*.png` 全部 200 可加载
- 9 个核心后端 API 通过 8206 → 8200 代理全部 200

---

## 4. 关键文件索引（新对话最常用）

```
aitee/
├── backend/app/
│   ├── routers/c/        # C 端业务路由（按域划分：home/ai/city/products/...）
│   ├── routers/admin/    # Admin CRUD
│   ├── schemas/c.py      # C 端 Pydantic（OrderOut 用 amount_total 不是 pay_amount）
│   ├── services/         # 业务服务层（订单状态机、AI、城市 IP）
│   └── main.py           # 所有路由统一前缀 /api/v1
├── frontend/src/          # 8201 H5 demo（视觉基准，不要动）
├── miniapp/
│   ├── src/
│   │   ├── pages/        # 17 个业务页（已对齐 8201）
│   │   ├── components/   # BrandHeader / Countdown / SectionHead
│   │   ├── styles/       # variables.scss / global.scss
│   │   ├── utils/        # request / env / platform / format
│   │   ├── api/index.ts  # 所有后端 API（Auth/User/Address/Coupon/Product/Pattern/Design/Cart/Order/Home/CityIp/AI/Messages/QR/Payments）
│   │   ├── store/auth.ts
│   │   ├── static/img/   # 从 frontend 拷过来的图资源
│   │   └── pages.json    # 所有页 navigationStyle: custom
│   └── vite.config.ts    # /api proxy + /static 中间件
├── scripts/m2_smoke.py    # 端到端冒烟测试
└── docs/HANDOFF.md        # 本文档
```

---

## 5. 已知约束 / 坑

1. **`/static/*` 在 uniapp h5 dev 默认不可访问**：必须用 `miniapp/vite.config.ts` 里那个 `serveStaticInDev` 插件兜底（已加好）
2. **Pydantic 字段名易混**：`amount_total` vs `pay_amount` 是后者已删；订单 schema 看 `backend/app/schemas/c.py` 的 `OrderOut`
3. **小程序兼容性未做**：本轮只对齐 H5，wx/dy 编译会有 `backdrop-filter` / 复杂 SVG / `grid` 部分失效，需要 `#ifdef MP-WEIXIN/MP-TOUTIAO` 降级，**这是下一阶段任务**
4. **代理**：所有网络下载（pip / npm / git clone）走 `127.0.0.1:7890`（参见 `.cursor/rules/proxy-settings.mdc`）
5. **杀进程**：重启服务**严禁** `Get-Process python | Stop-Process`；按端口找 PID 杀（见 `.cursor/rules/kill-process-by-port.mdc`）
6. **后端 8200 没有 /health 路由**，用 `/api/v1/home/banners` 探活

---

## 6. 后续可继续的事

- **M3 - 小程序端兼容**：把 8206 那套 UI 在 mp-weixin / mp-toutiao 下编译通过，逐页 `#ifdef` 降级
- **M3 - 真支付接入**：微信支付 / 抖音支付替换 `platform.mockPay`
- **M3 - 真 AI 调用**：现在 `AI.generate` 已通 OpenRouter `google/gemini-3-pro`，但生产需要加配额、限流、回退池
- **视觉精修**：hero 背景换深圳实景图、bento 加更多入口、editor 加图层旋转手柄
- **B 端门户 8203**：合作商/门店/员工三端的真业务页面
- **打印工厂对接**：订单进入 `printing` 状态后实际推送到工厂

---

## 7. 启动方式

```bat
:: 全部启动
aitee\start-all.bat

:: 单个重启
aitee\restart.bat backend
aitee\restart.bat miniapp

:: 看状态
aitee\status.bat

:: 全停
aitee\stop.bat
```

冒烟测试（要先启动 backend 8200）：

```bat
cd aitee\scripts
python m2_smoke.py
```

---

**新会话开局建议提示词**：
> 这是 aitee 项目。先读 `@aitee/docs/HANDOFF.md` 了解全部进展，再回答我接下来的问题。
