import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UserRole } from '@/types/auth'

const TOKEN_KEY = 'zhihire_token'
const ROLE_KEY = 'zhihire_role'
const USERNAME_KEY = 'zhihire_username'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string>(localStorage.getItem(TOKEN_KEY) || '')
  const role = ref<UserRole | ''>((localStorage.getItem(ROLE_KEY) as UserRole) || '')
  const username = ref<string>(localStorage.getItem(USERNAME_KEY) || '')

  const isLoggedIn = computed(() => !!token.value)

  function setAuth(newToken: string, newRole: UserRole, newUsername: string) {
    token.value = newToken
    role.value = newRole
    username.value = newUsername
    localStorage.setItem(TOKEN_KEY, newToken)
    localStorage.setItem(ROLE_KEY, newRole)
    localStorage.setItem(USERNAME_KEY, newUsername)
  }

  function logout() {
    token.value = ''
    role.value = ''
    username.value = ''
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(ROLE_KEY)
    localStorage.removeItem(USERNAME_KEY)
  }

  return { token, role, username, isLoggedIn, setAuth, logout }
})
