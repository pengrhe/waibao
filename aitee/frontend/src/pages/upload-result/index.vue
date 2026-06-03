<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import NavBar from '@/components/NavBar.vue'

const router = useRouter()
const fileInput = ref<HTMLInputElement | null>(null)
const dataUrl = ref('')

function pick() {
  fileInput.value?.click()
}

function onChange(e: Event) {
  const t = e.target as HTMLInputElement
  const f = t.files?.[0]
  if (!f) return
  if (f.size > 8 * 1024 * 1024) {
    showToast('图片过大，请选 8MB 以内')
    return
  }
  const r = new FileReader()
  r.onload = () => {
    dataUrl.value = r.result as string
  }
  r.readAsDataURL(f)
}

function useImage() {
  if (!dataUrl.value) return showToast('请先选择图片')
  router.replace({ path: '/editor', query: { uploadUrl: dataUrl.value } })
}
</script>

<template>
  <div class="up">
    <NavBar title="来图定制" />

    <div class="up__intro">
      <span class="i-material-symbols:image-outline-rounded up__icon" />
      <p>上传任意图片，自动适配 T 恤打印工艺</p>
      <ul>
        <li>支持 JPG / PNG / WebP，单文件 ≤ 8MB</li>
        <li>建议 1:1 比例、最长边 ≥ 1024px</li>
        <li>Demo 版本不做实际去底处理</li>
      </ul>
    </div>

    <div class="up__pic" @click="pick">
      <img v-if="dataUrl" :src="dataUrl" alt="" />
      <template v-else>
        <span class="i-material-symbols:add-photo-alternate-outline-rounded up__pic-icon" />
        <span>点击上传图片</span>
      </template>
    </div>

    <input ref="fileInput" type="file" accept="image/*" hidden @change="onChange" />

    <div class="bar">
      <button class="btn-ghost" @click="pick">重新选择</button>
      <button class="btn-primary" :disabled="!dataUrl" @click="useImage">用此图定制</button>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.up {
  min-height: 100vh;
  background: $color-bg-page;
  padding-bottom: 80px;
}

.up__intro {
  background: #fff;
  margin: 12px;
  padding: 16px;
  border-radius: 12px;
  text-align: center;

  p {
    margin: 8px 0 12px;
    font-size: 14px;
    color: $color-text-primary;
  }

  ul {
    text-align: left;
    color: $color-text-secondary;
    font-size: 12px;
    line-height: 1.6;
    margin-top: 8px;

    li {
      list-style: disc inside;
    }
  }
}

.up__icon {
  font-size: 48px;
  color: $color-primary;
}

.up__pic {
  margin: 0 12px 12px;
  background: #fff;
  border: 2px dashed $color-divider;
  border-radius: 12px;
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 8px;
  color: $color-text-placeholder;
  font-size: 14px;
  overflow: hidden;
  cursor: pointer;

  img {
    width: 100%;
    height: 100%;
    object-fit: contain;
  }
}

.up__pic-icon {
  font-size: 56px;
  color: $color-primary;
  opacity: 0.6;
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
  display: flex;
  gap: 10px;
  z-index: 9;

  .btn-ghost,
  .btn-primary {
    flex: 1;
    height: 44px;
  }

  .btn-primary:disabled {
    opacity: 0.5;
  }
}
</style>
