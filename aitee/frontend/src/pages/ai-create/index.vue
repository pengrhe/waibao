<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import NavBar from '@/components/NavBar.vue'
import { fetchAiStyles, generateAiImages } from '@/api/ai'
import type { AiSample } from '@/types'

const router = useRouter()

const styles = ref<string[]>([])
const activeStyle = ref('卡通')
const prompt = ref('')
const generating = ref(false)
const results = ref<AiSample[]>([])
const tip = ref('')

const presets = ['夕阳下的猫咪', '宇宙星辰', '森林精灵', '城市夜景', '海浪轮廓', '夏日柠檬']

onMounted(async () => {
  styles.value = await fetchAiStyles()
})

async function onGenerate() {
  if (!prompt.value.trim()) {
    showToast('请先描述要生成的图案')
    return
  }
  generating.value = true
  tip.value = '正在唤醒 AI 模型…'
  setTimeout(() => (tip.value = '正在分析关键元素…'), 700)
  setTimeout(() => (tip.value = '正在调整风格细节…'), 1500)
  try {
    results.value = await generateAiImages({ prompt: prompt.value, style: activeStyle.value, count: 4 })
    tip.value = ''
  } finally {
    generating.value = false
  }
}

function pick(s: AiSample) {
  router.replace({ path: '/editor', query: { aiUrl: s.imageUrl } })
}
</script>

<template>
  <div class="ai">
    <NavBar title="AI 创作" />

    <section class="prompt">
      <div class="prompt__title">输入想要的图案</div>
      <textarea v-model="prompt" rows="3" placeholder="例如：一只在夕阳下打哈欠的橘猫，复古绘本风格" />
      <div class="prompt__presets">
        <button
          v-for="p in presets"
          :key="p"
          class="prompt__preset"
          @click="prompt = p"
        >
          {{ p }}
        </button>
      </div>
    </section>

    <section class="styles">
      <div class="styles__title">选择风格</div>
      <div class="styles__list">
        <button
          v-for="s in styles"
          :key="s"
          class="styles__item"
          :class="{ 'styles__item--active': activeStyle === s }"
          @click="activeStyle = s"
        >
          {{ s }}
        </button>
      </div>
    </section>

    <section v-if="generating" class="generating">
      <div class="generating__bubble">
        <span class="i-material-symbols:auto-awesome-rounded" />
      </div>
      <div class="generating__tip">{{ tip }}</div>
      <div class="generating__progress">
        <div class="generating__bar" />
      </div>
    </section>

    <section v-else-if="results.length" class="results">
      <div class="results__title">为你生成了 {{ results.length }} 张</div>
      <div class="results__grid">
        <button v-for="r in results" :key="r.id" class="results__item" @click="pick(r)">
          <img :src="r.imageUrl" alt="" />
          <div class="results__use">选择此图</div>
        </button>
      </div>
      <button class="results__regen" @click="onGenerate">
        <span class="i-material-symbols:cached-rounded" />
        重新生成
      </button>
    </section>

    <div class="bar">
      <button class="bar__btn" :disabled="generating" @click="onGenerate">
        <span class="i-material-symbols:auto-awesome-rounded" />
        生成图案
      </button>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.ai {
  min-height: 100vh;
  background: $color-bg-page;
  padding-bottom: 80px;
}

.prompt {
  background: #fff;
  margin: 12px;
  border-radius: 12px;
  padding: 14px;

  &__title {
    font-size: 14px;
    font-weight: 700;
    margin-bottom: 10px;
  }

  textarea {
    width: 100%;
    border: 1px solid $color-divider;
    border-radius: 8px;
    padding: 10px 12px;
    font-size: 14px;
    resize: none;
    outline: none;
  }

  &__presets {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 10px;
  }

  &__preset {
    background: $color-bg-tag;
    color: $color-text-secondary;
    font-size: 12px;
    padding: 4px 10px;
    border-radius: $radius-pill;
  }
}

.styles {
  background: #fff;
  margin: 0 12px 12px;
  border-radius: 12px;
  padding: 14px;

  &__title {
    font-size: 14px;
    font-weight: 700;
    margin-bottom: 10px;
  }

  &__list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  &__item {
    padding: 6px 14px;
    border-radius: $radius-pill;
    background: $color-bg-tag;
    color: $color-text-secondary;
    font-size: 13px;

    &--active {
      background: $color-primary;
      color: #fff;
      font-weight: 700;
    }
  }
}

.generating {
  text-align: center;
  padding: 40px 24px;

  &__bubble {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: linear-gradient(135deg, #ff6a6c, #ff4d4f);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 36px;
    box-shadow: 0 10px 30px rgba(255, 77, 79, 0.3);
    animation: pulse 1.5s ease-in-out infinite;
  }

  &__tip {
    margin-top: 16px;
    font-size: 13px;
    color: $color-text-regular;
  }

  &__progress {
    margin: 16px auto 0;
    width: 200px;
    height: 4px;
    background: $color-bg-tag;
    border-radius: 2px;
    overflow: hidden;
    position: relative;
  }

  &__bar {
    position: absolute;
    inset: 0;
    background: linear-gradient(90deg, transparent, $color-primary, transparent);
    animation: progress 1.5s linear infinite;
  }
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.08);
  }
}

@keyframes progress {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

.results {
  margin: 12px;

  &__title {
    font-size: 14px;
    font-weight: 700;
    margin-bottom: 10px;
  }

  &__grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
  }

  &__item {
    background: #fff;
    border-radius: 12px;
    overflow: hidden;
    aspect-ratio: 1;
    position: relative;
    padding: 0;

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
  }

  &__use {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 32px;
    background: rgba(255, 77, 79, 0.9);
    color: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: 700;
  }

  &__regen {
    margin-top: 12px;
    width: 100%;
    height: 40px;
    border: 1px solid $color-primary;
    color: $color-primary;
    border-radius: $radius-pill;
    background: #fff;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
  }
}

.bar {
  position: fixed;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  max-width: 480px;
  padding: 12px 16px;
  background: #fff;
  border-top: 1px solid $color-divider;
  z-index: 9;

  &__btn {
    width: 100%;
    height: 44px;
    border-radius: $radius-pill;
    background: $color-primary;
    color: #fff;
    font-weight: 700;
    font-size: 15px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 4px;

    &:disabled {
      opacity: 0.5;
    }
  }
}
</style>
