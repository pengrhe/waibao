import { defineStore } from 'pinia'
import { ref } from 'vue'
import { fetchProfile, loginMock, logoutMock, type UserProfile } from '@/api/user'

export const useUserStore = defineStore('user', () => {
  const profile = ref<UserProfile | null>(null)
  const loading = ref(false)

  async function load() {
    loading.value = true
    try {
      profile.value = await fetchProfile()
    } finally {
      loading.value = false
    }
  }

  async function login() {
    profile.value = await loginMock()
    return profile.value
  }

  async function logout() {
    await logoutMock()
    profile.value = await fetchProfile()
  }

  return { profile, loading, load, login, logout }
})
