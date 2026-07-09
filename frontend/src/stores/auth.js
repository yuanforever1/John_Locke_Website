import { defineStore } from 'pinia'
import client from '@/api/client'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    access: localStorage.getItem('access') || '',
    refresh: localStorage.getItem('refresh') || '',
    profile: null,
    loaded: false,
  }),
  getters: {
    isAuthenticated: (state) => !!state.access,
    displayName: (state) =>
      state.profile?.nickname || state.profile?.username || '学者',
  },
  actions: {
    setTokens({ access, refresh }) {
      this.access = access
      this.refresh = refresh
      localStorage.setItem('access', access)
      localStorage.setItem('refresh', refresh)
    },
    async login(username, password) {
      const res = await client.post('/auth/login/', { username, password })
      this.setTokens(res.data)
      await this.fetchProfile()
    },
    async register(payload) {
      const res = await client.post('/auth/register/', payload)
      this.setTokens(res.data.tokens)
      this.profile = res.data.user
      this.loaded = true
    },
    async fetchProfile() {
      const res = await client.get('/auth/me/')
      this.profile = res.data
      this.loaded = true
      return res.data
    },
    async updateProfile(payload) {
      const res = await client.put('/auth/me/', payload)
      this.profile = res.data
      return res.data
    },
    async uploadAvatar(file) {
      const form = new FormData()
      form.append('avatar', file)
      const res = await client.put('/auth/me/avatar/', form)
      this.profile = res.data
      return res.data
    },
    logout() {
      this.access = ''
      this.refresh = ''
      this.profile = null
      this.loaded = false
      localStorage.removeItem('access')
      localStorage.removeItem('refresh')
    },
  },
})
