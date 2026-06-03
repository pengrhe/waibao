# aitee — 前端 H5 Demo

aitee（AI T 恤 / 帆布包定制）小程序的高保真前端原型。

- 纯前端、所有数据本地 mock + localStorage 持久化
- 浏览器直接打开就能看，不依赖任何后端
- 一份代码 16 个路由页，覆盖完整商业闭环

## 一键启动（Windows）

双击 `start.bat` 即可。脚本会自动：

1. 检查 `node_modules`，缺则走代理 `127.0.0.1:7890` 安装依赖
2. 启动 vite dev server，监听 `:8201`，并允许同 WiFi 手机访问

## 手动启动

```bash
cd D:\wp\waibao\aitee\frontend
npm install              # 首次
npm run dev              # http://localhost:8201
npm run dev -- --host    # 同 WiFi 手机扫码
npm run build            # 静态产物 dist/
npm run preview          # 本地预览生产产物
```

> Node 18+ / npm 9+，本机已用 Node 22.22 / npm 10.9 验证通过。

## 给客户演示的推荐操作流（完整业务闭环）

1. **首页**：下拉看主视觉、5 入口、新人 7.8 折券倒计时、人气推荐、4 个内容专区
2. 点击底部中间的红色「定制」按钮 → 进入 **编辑器**
3. 顶部「切换款式 ▼」→ **款式选择**（短袖 T / 帆布包 / 卫衣 / 亲子装 / 宠物装），选一款返回
4. 编辑器底部「印花素材」→ 弹出印花选择 → 任选一张加入图层
5. 拖拽图层、缩放（右下绿点）、旋转（右上蓝点）、删除（左上黑点）
6. 顶部色块切换 T 恤颜色；右侧「背面」按钮切换正反；左下「撤销 / 重做」试一下
7. 「文字」工具 → 输入文案 + 选颜色 → 确定
8. 「来图定制」→ 从相册选一张图片 → 自动加图层
9. 「AI 创作」→ 输 prompt + 选风格 → 「生成图案」（mock 2~3 秒返回 4 张）→ 选其中一张回到编辑器
10. 右下角「加入购物车」→ 选尺码 → 确认
11. 底部 tabbar 进 **购物车** → 全选 → 「结算」
12. **结算页**：选地址（默认已有一个示例地址）+ 选优惠券（新人 7.8 折）→ 「提交订单」
13. 自动模拟支付（约 1 秒）→ 跳到 **订单详情**，状态时间线从「已支付」一路推进到「打印中」
14. 底部 tabbar 进「我的」→ 看到我的设计、我的订单、优惠券、地址；底部「重置 Demo」可一键回到初始演示态

## 16 个路由

| 路由 | 页面 |
|---|---|
| `/` | 首页 |
| `/gallery` | 印花库 |
| `/editor` | 定制编辑器（核心） |
| `/product-picker` | 款式选择 |
| `/cart` | 购物车 |
| `/checkout` | 结算 |
| `/mine` | 我的 |
| `/order/list` | 订单列表 |
| `/order/:id` | 订单详情 |
| `/design-list` | 我的设计 |
| `/address/list` | 地址管理 |
| `/address/edit` | 编辑地址 |
| `/coupon` | 优惠券 |
| `/login` | 登录 |
| `/ai-create` | AI 创作 |
| `/upload-result` | 来图定制 |

## 技术栈

- Vue 3 + TypeScript + Vite 5
- Vue Router 4（hash 模式）/ Pinia
- Vant 4（自动按需引入）/ unplugin-icons + Material Symbols
- postcss-px-to-viewport-8-plugin（设计稿宽度 375）
- 编辑器交互：DOM `transform` + Pointer Events，撤销重做使用 pinia 历史栈

## 目录

```
src/
├── api/              mock API（与未来真实接口同签名）
│   ├── address.ts ai.ts cart.ts coupon.ts design.ts home.ts
│   ├── order.ts pattern.ts product.ts request.ts user.ts
├── mock/             静态种子数据
│   ├── ai-samples.ts banners.ts patterns.ts products.ts
│   ├── recommend.ts seed.ts topics.ts
├── assets/styles/    全局 SCSS 变量与基础样式
├── components/       AppTabbar BrandHeader Countdown EditorLayer NavBar PagePlaceholder
├── pages/            16 个路由页面
├── router/           hash 路由
├── store/            pinia: bootstrap user cart editor
├── types/            TS 类型定义
├── utils/            placeholder（占位 SVG）/ delay / format / id / storage
├── App.vue
└── main.ts
```

## 占位素材

所有 T 恤底图、印花、Banner、推荐卡、专区卡均由 `src/utils/placeholder.ts` **代码动态生成 SVG**，未使用任何参考图原素材，避免侵权。需要正式素材时替换 mock 中的 `imageUrl` 字段即可。

## localStorage 持久化

| key | 内容 |
|---|---|
| `aitee:user` | 当前登录态 |
| `aitee:cart` | 购物车 |
| `aitee:designs` | 我的设计稿 |
| `aitee:orders` | 订单 |
| `aitee:addresses` | 地址 |
| `aitee:coupons` | 优惠券 |
| `aitee:patternFavs` | 印花收藏 ID |
| `aitee:seeded:v1` | 首次种子初始化标记 |

「我的」页面底部 **重置 Demo 数据** 按钮可一键清空全部并恢复初始种子。

## 阶段说明

本工程是 **阶段 1**：前端 Demo。阶段 2 将接 FastAPI 后端 + 微信小程序，详见 `D:\wp\waibao\aitee\开发说明.docx`。

## 定位（B 方案确定）

| 阶段 | frontend 角色 |
|---|---|
| 阶段 1（M1 前） | C 端唯一演示载体，客户已确认 UI/功能 |
| **阶段 2（M2 起）** | **冻结新功能**，仅作为浏览器 H5 入口和商务演示；新业务全部在 `miniapp` 实装 |
| 上线 | `npm run build` → nginx 静态托管，例如 `m.aitee.com`，C 端浏览器用户走这里 |

**为什么 B 方案**：C 端业务核心战场是微信/抖音小程序（uniapp 一套代码两端），浏览器 H5 已足够覆盖剩余场景，不再两份 C 端业务代码同步演进。详见 `aitee/README.md` "端形态地图"。
