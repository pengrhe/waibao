# aitee-admin

总部后台 H5（Vue3 + Vite + Element Plus + Pinia）。

## 启动

```cmd
cd D:\wp\waibao\aitee\admin
start.bat
```

- 地址：http://localhost:8202
- 默认账号：`admin` / `admin123`（由 `backend/scripts/seed.py` 写入）
- 需后端已起在 http://127.0.0.1:8000（vite proxy `/api` → backend）

## 21 个菜单

工作台 / 商品 / 印花库 / Banner / 首页专区 / 城市 IP / 文化元素 / 用户 / 优惠券 / 订单 / 退款 / 联营伙伴 / 加盟店 / 店员 / 设备 / 财务总览 / 提现审核 / 对账 / 数据统计 / AI 模型通道 / 系统配置 / 后台账号

M1 阶段除登录、工作台外其余为占位页，M2 逐个填充实际 CRUD。
