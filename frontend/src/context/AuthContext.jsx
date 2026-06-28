import { createContext, useContext, useState, useEffect } from 'react'
import { authAPI } from '../services/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [admin, setAdmin] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('gt_access')
    if (token) {
      authAPI.me()
        .then(({ data }) => setAdmin(data))
        .catch(() => { localStorage.removeItem('gt_access'); localStorage.removeItem('gt_refresh') })
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  const login = async (email, password) => {
    const { data } = await authAPI.login({ email, password })
    localStorage.setItem('gt_access', data.access)
    localStorage.setItem('gt_refresh', data.refresh)
    const me = await authAPI.me()
    setAdmin(me.data)
    return me.data
  }

  const logout = async () => {
    try { await authAPI.logout(localStorage.getItem('gt_refresh')) } catch {}
    localStorage.removeItem('gt_access')
    localStorage.removeItem('gt_refresh')
    setAdmin(null)
  }

  return <AuthContext.Provider value={{ admin, loading, login, logout }}>{children}</AuthContext.Provider>
}