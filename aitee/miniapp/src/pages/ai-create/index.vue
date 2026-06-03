<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import BrandHeader from '../../components/BrandHeader.vue'
import { AI, User } from '../../api'

type Mode = 't2i' | 'i2i' | 'ti2i'

const mode = ref<Mode>('t2i')
const prompt = ref('')
const activeStyle = ref('国潮')
const styles = ref<string[]>(['国潮', '极简', 'Y2K', '赛博朋克', '水彩', '像素', '3D', '复古'])
const sourceUrl = ref('')
const samples = ref<any[]>([])
const generating = ref(false)
const fallback = ref(false)
const tip = ref('')

const modes = [
  { key: 't2i' as Mode, label: '文生图', icon: '📝', desc: '一句话生成' },
  { key: 'i2i' as Mode, label: '图生图', icon: '🖼️', desc: '基于参考图' },
  { key: 'ti2i' as Mode, label: '图+文', icon: '✨', desc: '参考图 + 描述' },
]

const presets = ['夕阳下的猫咪', '宇宙星辰', '森林精灵', '城市夜景', '海浪轮廓', '夏日柠檬', '深圳天际线']

onLoad(async (opt) => {
  if (opt?.mode) mode.value = opt.mode as Mode
  if (opt?.prompt) prompt.value = decodeURIComponent(String(opt.prompt))
})

onMounted(async () => {
  try {
    const r = await AI.styles()
    if (r?.length) styles.value = r
  } catch {}
})

async function pickSource() {
  try {
    const r = await new Promise<any>((resolve, reject) => {
      uni.chooseImage({ count: 1, success: resolve, fail: reject })
    })
    sourceUrl.value = (r.tempFilePaths && r.tempFilePaths[0]) || ''
  } catch {}
}

async function generate() {
  if (mode.value !== 't2i' && !sourceUrl.value) {
    uni.showToast({ title: '请先选择参考图', icon: 'none' })
    return
  }
  if (mode.value !== 'i2i' && !prompt.value.trim()) {
    uni.showToast({ title: '请先描述图案', icon: 'none' })
    return
  }
  generating.value = true
  tip.value = '正在唤醒 AI 模型…'
  setTimeout(() => { if (generating.value) tip.value = '正在分析关键元素…' }, 700)
  setTimeout(() => { if (generating.value) tip.value = '正在调整风格细节…' }, 1500)
  setTimeout(() => { if (generating.value) tip.value = '马上就好…' }, 2500)
  try {
    User.reportPref('ai_style', activeStyle.value).catch(() => {})
    const r: any = await AI.generate({
      type: mode.value,
      prompt: prompt.value,
      style: activeStyle.value,
      source_image_url: sourceUrl.value,
      n: 4,
    })
    samples.value = r.samples || []
    fallback.value = r.fallback
    tip.value = ''
  } catch (e) {
    tip.value = ''
  } finally { generating.value = false }
}

function useSample(s: any) {
  uni.navigateTo({ url: `/pages/editor/index?pattern_url=${encodeURIComponent(s.image_url)}` })
}
</script>

<template>
  <view class="ai">
    <BrandHeader title="AI 创作" show-back :show-logo="false" />

    <!-- 三模式 -->
    <view class="modes">
      <view
        v-for="m in modes"
        :key="m.key"
        class="modes__opt"
        :class="{ on: mode === m.key }"
        @click="mode = m.key"
      >
        <text class="modes__icon">{{ m.icon }}</text>
        <text class="modes__label">{{ m.label }}</text>
        <text class="modes__desc">{{ m.desc }}</text>
      </view>
    </view>

    <!-- 参考图（i2i/ti2i）-->
    <view v-if="mode !== 't2i'" class="card">
      <view class="card__title">参考图</view>
      <view class="picker" @click="pickSource">
        <image v-if="sourceUrl" :src="sourceUrl" class="picker__img" mode="aspectFit" />
        <view v-else class="picker__empty">
          <text class="picker__plus">+</text>
          <text class="picker__text">点击选择本地图片</text>
        </view>
      </view>
    </view>

    <!-- prompt 输入 -->
    <view v-if="mode !== 'i2i'" class="card">
      <view class="card__title">输入想要的图案</view>
      <textarea
        v-model="prompt"
        class="prompt__ta"
        placeholder="例如：一只在夕阳下打哈欠的橘猫，复古绘本风格"
        maxlength="200"
      />
      <view class="presets">
        <view v-for="p in presets" :key="p" class="preset" @click="prompt = p">{{ p }}</view>
      </view>
    </view>

    <!-- 风格选择 -->
    <view class="card">
      <view class="card__title">选择风格</view>
      <view class="styles">
        <view
          v-for="s in styles"
          :key="s"
          class="style"
          :class="{ on: activeStyle === s }"
          @click="activeStyle = s"
        >{{ s }}</view>
      </view>
    </view>

    <!-- 生成中 -->
    <view v-if="generating" class="generating">
      <view class="generating__bubble"><text>✦</text></view>
      <text class="generating__tip">{{ tip }}</text>
      <view class="generating__progress">
        <view class="generating__bar" />
      </view>
    </view>

    <!-- 结果 -->
    <view v-else-if="samples.length" class="results">
      <view class="results__head">
        <text class="results__title">为你生成了 {{ samples.length }} 张</text>
        <text v-if="fallback" class="results__fb">占位图（fallback）</text>
      </view>
      <view class="results__grid">
        <view v-for="s in samples" :key="s.id" class="result" @click="useSample(s)">
          <image :src="s.image_url" class="result__img" mode="aspectFill" />
          <view class="result__use">选择此图 →</view>
        </view>
      </view>
      <view class="results__regen" @click="generate">
        <text>↻ 重新生成</text>
      </view>
    </view>

    <!-- 底部 CTA -->
    <view class="bar safe-area">
      <view class="bar__btn" :class="{ 'bar__btn--dis': generating }" @click="generate">
        <text class="bar__btn-icon">✦</text>
        <text>{{ generating ? '生成中…' : '生成图案' }}</text>
      </view>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.ai {
  min-height: 100vh;
  background:
    radial-gradient(120% 30% at 50% 0%, #fff1f5 0%, transparent 70%),
    $color-bg-page;
  padding-bottom: 100px;
}

.modes {
  display: flex;
  gap: 8px;
  margin: 8px 12px 0;

  &__opt {
    flex: 1;
    background: #fff;
    padding: 14px 8px 10px;
    border-radius: 14px;
    text-align: center;
    border: 1px solid rgba(0,0,0,.04);
    transition: all .15s;

    &.on {
      background: linear-gradient(135deg, #ff7a2a, #ff4d6e);
      border-color: transparent;
      box-shadow: 0 6px 14px rgba(255,77,79,.25);
      .modes__icon { transform: scale(1.1); }
      .modes__label { color: #fff; }
      .modes__desc { color: rgba(255,255,255,.85); }
    }
  }
  &__icon { display: block; font-size: 24px; transition: transform .2s; }
  &__label { display: block; font-size: 13px; font-weight: 700; color: #1f2937; margin-top: 4px; }
  &__desc { display: block; font-size: 10px; color: $color-text-placeholder; margin-top: 2px; }
}

.card {
  background: #fff;
  margin: 10px 12px 0;
  border-radius: 14px;
  padding: 14px;
  &__title { font-size: 14px; font-weight: 700; margin-bottom: 10px; color: #1f2937; }
}

.picker {
  background: $color-bg-tag;
  border-radius: 10px;
  border: 1px dashed $color-border;
  min-height: 120px;
  display: flex; align-items: center; justify-content: center;
  &__img { max-width: 100%; max-height: 200px; border-radius: 10px; }
  &__empty {
    display: flex; flex-direction: column; align-items: center; gap: 6px;
    color: $color-text-placeholder;
  }
  &__plus {
    width: 36px; height: 36px; line-height: 32px; text-align: center;
    border-radius: 50%; background: #fff; font-size: 22px; font-weight: 700;
    color: $color-primary;
  }
  &__text { font-size: 12px; }
}

.prompt__ta {
  width: 100%;
  border: 1px solid $color-divider;
  border-radius: 10px;
  padding: 10px 12px;
  font-size: 14px;
  min-height: 80px;
  background: #fafafa;
  box-sizing: border-box;
}

.presets {
  display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px;
}
.preset {
  background: $color-bg-tag;
  color: $color-text-secondary;
  font-size: 12px;
  padding: 4px 12px;
  border-radius: 999px;
}

.styles {
  display: flex; flex-wrap: wrap; gap: 8px;
}
.style {
  padding: 6px 14px;
  border-radius: 999px;
  background: $color-bg-tag;
  color: $color-text-secondary;
  font-size: 13px;
  border: 1px solid transparent;
  &.on {
    background: $color-primary-light;
    color: $color-primary;
    border-color: $color-primary;
    font-weight: 700;
  }
}

.generating {
  text-align: center;
  padding: 40px 24px;
  &__bubble {
    width: 80px; height: 80px; border-radius: 50%;
    background: linear-gradient(135deg, #ff8a3a, #ff4d4f);
    display: inline-flex; align-items: center; justify-content: center;
    box-shadow: 0 10px 30px rgba(255,77,79,.3);
    animation: pulse 1.5s ease-in-out infinite;
    text { color: #fff; font-size: 36px; line-height: 1; }
  }
  &__tip { display: block; margin-top: 16px; font-size: 13px; color: $color-text-regular; }
  &__progress {
    margin: 16px auto 0;
    width: 200px; height: 4px;
    background: $color-bg-tag;
    border-radius: 2px;
    overflow: hidden;
    position: relative;
  }
  &__bar {
    position: absolute; inset: 0;
    background: linear-gradient(90deg, transparent, $color-primary, transparent);
    animation: progress 1.5s linear infinite;
  }
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.08); }
}
@keyframes progress {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.results {
  margin: 14px 12px 0;
  &__head { display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 10px; padding: 0 4px; }
  &__title { font-size: 15px; font-weight: 800; color: #1f2937; }
  &__fb { font-size: 11px; color: $color-text-placeholder; }
  &__grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
  &__regen {
    margin-top: 14px;
    height: 40px; line-height: 40px;
    border: 1px solid $color-primary;
    color: $color-primary;
    border-radius: 999px;
    background: #fff;
    font-weight: 700;
    text-align: center;
    font-size: 13px;
  }
}
.result {
  position: relative;
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  aspect-ratio: 1;
  &__img { width: 100%; height: 100%; }
  &__use {
    position: absolute; bottom: 0; left: 0; right: 0;
    height: 32px; line-height: 32px;
    background: rgba(255,77,79,.92); color: #fff;
    text-align: center; font-size: 12px; font-weight: 700;
  }
}

.bar {
  position: fixed; bottom: 0; left: 0; right: 0;
  padding: 12px 16px;
  background: #fff;
  border-top: 1px solid $color-divider;
  z-index: 9;
}
.safe-area { padding-bottom: calc(12px + env(safe-area-inset-bottom)); }
.bar__btn {
  height: 44px;
  border-radius: 999px;
  background: linear-gradient(135deg, #ff7a2a, #ff4d4f);
  color: #fff;
  font-weight: 700; font-size: 15px;
  display: flex; align-items: center; justify-content: center; gap: 6px;
  box-shadow: 0 6px 16px rgba(255,77,79,.35);
  &--dis { opacity: .6; }
}
.bar__btn-icon { font-size: 16px; line-height: 1; }
</style>
