import { atom } from 'jotai'

export interface User {
  id: number
  email: string
  full_name: string
  role: 'admin' | 'manager' | 'estimator' | 'viewer'
}

// User atom - will be null when not logged in
export const userAtom = atom<User | null>(null)

// Token atom - stores the JWT token
export const tokenAtom = atom<string | null>(null)

// Load user from local storage on initialization
const storedUser = localStorage.getItem('user')
const storedToken = localStorage.getItem('token')

if (storedUser && storedToken) {
  try {
    const parsedUser = JSON.parse(storedUser)
    userAtom.init = parsedUser
    tokenAtom.init = storedToken
  } catch (error) {
    console.error('Failed to parse stored user:', error)
    // Clear invalid storage
    localStorage.removeItem('user')
    localStorage.removeItem('token')
  }
}

// Store user in localStorage when it changes
export const persistUserAtom = atom(
  (get) => get(userAtom),
  (get, set, nextUser: User | null) => {
    set(userAtom, nextUser)
    if (nextUser) {
      localStorage.setItem('user', JSON.stringify(nextUser))
    } else {
      localStorage.removeItem('user')
    }
  }
)

// Store token in localStorage when it changes
export const persistTokenAtom = atom(
  (get) => get(tokenAtom),
  (get, set, nextToken: string | null) => {
    set(tokenAtom, nextToken)
    if (nextToken) {
      localStorage.setItem('token', nextToken)
    } else {
      localStorage.removeItem('token')
    }
  }
)

// Convenience atom for checking if user is logged in
export const isLoggedInAtom = atom(
  (get) => get(userAtom) !== null
)

// Current user role atom
export const userRoleAtom = atom(
  (get) => get(userAtom)?.role
)

// Check if user has specific role
export const hasRoleAtom = atom(
  (get) => (role: User['role'] | User['role'][]) => {
    const userRole = get(userRoleAtom)
    if (!userRole) return false
    
    if (Array.isArray(role)) {
      return role.includes(userRole)
    }
    
    return userRole === role
  }
)

// Check if user is admin
export const isAdminAtom = atom(
  (get) => get(userRoleAtom) === 'admin'
)

// Logout function atom
export const logoutAtom = atom(
  null,
  (get, set) => {
    set(persistUserAtom, null)
    set(persistTokenAtom, null)
    // Redirect to login will be handled by the ProtectedRoute component
  }
)
