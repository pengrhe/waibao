<script setup lang="ts">
interface Props {
  title: string
  more?: string  // 跳转 url 或空（隐藏）
  moreText?: string
}
const props = withDefaults(defineProps<Props>(), { moreText: '全部' })
function go() {
  if (props.more) uni.navigateTo({ url: props.more }).catch(() => uni.switchTab({ url: props.more! }))
}
</script>

<template>
  <view class="section-head">
    <text class="section-head__title">{{ title }}</text>
    <view v-if="more" class="section-head__more" @click="go">
      <text>{{ moreText }}</text>
      <text class="section-head__arrow">›</text>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.section-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  padding: 0 4px;
  margin-bottom: 12px;
}
.section-head__title {
  font-size: 18px;
  font-weight: 800;
  letter-spacing: -0.3px;
  color: #111;
}
.section-head__more {
  font-size: 12px;
  color: $color-text-secondary;
  display: inline-flex;
  align-items: center;
  gap: 2px;
}
.section-head__arrow { font-size: 14px; line-height: 1; }
</style>
