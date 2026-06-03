<script setup lang="ts">
/**
 * 浮动「定制」FAB —— 模拟 8201 那个凸起在原生 tabBar 中间的圆形入口。
 * uniapp 原生 tabBar 不支持中间凸起按钮，所以用 fixed 浮层，4 个 tab 页各引入一次即可。
 */

function goEditor() {
  uni.navigateTo({ url: '/pages/editor/index' })
}
</script>

<template>
  <view class="center-fab" @click="goEditor">
    <view class="center-fab__circle">
      <text class="center-fab__logo">aitee</text>
    </view>
    <text class="center-fab__label">定制</text>
  </view>
</template>

<style lang="scss" scoped>
/**
 * 原生 tabBar 在 H5 / 小程序通常 ~50–60px 高，
 * 圆心要落在 tabBar 顶部稍微靠下：bottom = tabBarHeight/2，
 * 这里取 28px 让 56×56 的圆有 ~22px 凸出在 tabBar 上方。
 */
.center-fab {
  position: fixed;
  left: 50%;
  bottom: 0;
  transform: translateX(-50%);
  width: 76px;
  height: 80px;
  pointer-events: none; /* 只让真正的圆/标签接受点击，避免挡其它 tab */
  z-index: 999;
}

.center-fab__circle {
  pointer-events: auto;
  position: absolute;
  left: 50%;
  bottom: 30px;
  transform: translateX(-50%);
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ff6a6c 0%, #ff4d4f 100%);
  border: 4px solid #fff;
  box-shadow: 0 6px 16px rgba(255, 77, 79, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
}

.center-fab__logo {
  color: #fff;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.5px;
  line-height: 1;
}

.center-fab__label {
  pointer-events: auto;
  position: absolute;
  left: 50%;
  bottom: 6px;
  transform: translateX(-50%);
  font-size: 10px;
  color: #ff4d4f;
  font-weight: 700;
  line-height: 1;
  white-space: nowrap;
}
</style>
