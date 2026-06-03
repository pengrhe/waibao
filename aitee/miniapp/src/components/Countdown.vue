<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { fmtCountdown } from '../utils/format'

interface Props {
  endTime: number
  size?: 'sm' | 'md' | 'lg'
  blockBg?: string
  blockColor?: string
}
const props = withDefaults(defineProps<Props>(), {
  size: 'md',
  blockBg: '#FF4D4F',
  blockColor: '#fff',
})
const emit = defineEmits<{ end: [] }>()

const now = ref(Date.now())
let timer: any = null

onMounted(() => {
  timer = setInterval(() => {
    now.value = Date.now()
    if (props.endTime - now.value <= 0) {
      emit('end')
      if (timer) clearInterval(timer)
    }
  }, 1000)
})

onBeforeUnmount(() => { if (timer) clearInterval(timer) })

const remaining = computed(() => fmtCountdown(props.endTime - now.value))
</script>

<template>
  <view class="countdown" :class="`countdown--${size}`">
    <text class="countdown__num" :style="{ background: blockBg, color: blockColor }">{{ remaining.h }}</text>
    <text class="countdown__sep">时</text>
    <text class="countdown__num" :style="{ background: blockBg, color: blockColor }">{{ remaining.m }}</text>
    <text class="countdown__sep">分</text>
    <text class="countdown__num" :style="{ background: blockBg, color: blockColor }">{{ remaining.s }}</text>
    <text class="countdown__sep">秒</text>
  </view>
</template>

<style lang="scss" scoped>
.countdown { display: inline-flex; align-items: center; font-weight: 700; }
.countdown__num {
  display: inline-block;
  min-width: 22px;
  padding: 2px 5px;
  border-radius: 4px;
  text-align: center;
  line-height: 1.2;
  margin: 0 2px;
}
.countdown__sep { color: $color-text-secondary; font-size: 11px; font-weight: 500; margin: 0 2px; }
.countdown--sm { font-size: 11px;
  .countdown__num { min-width: 18px; padding: 1px 4px; font-size: 11px; }
}
.countdown--md { font-size: 13px; }
.countdown--lg { font-size: 16px;
  .countdown__num { min-width: 28px; padding: 4px 8px; }
}
</style>
