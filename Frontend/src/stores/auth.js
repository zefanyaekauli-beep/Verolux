import { create } from 'zustand'

// Get API base URL dynamically - use network IP if accessed via network, otherwise localhost
const getApiBase = () => {
  const hostname = window.location.hostname
  // If accessed via IP address (network), use that IP for backend
  if (hostname !== 'localhost' && hostname !== '127.0.0.1') {
    return `http://${hostname}:8002`
  }
  // Otherwise use localhost
  return 'http://127.0.0.1:8002'
}

const API_BASE = getApiBase()

export default create(set => ({
  user: null,
  token: null,
  
  login: async (username, password) => {
    try {
      console.log(`Attempting login for: ${username} to ${API_BASE}/auth/login`)
      
      const response = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ username, password }),
        credentials: 'include'
      })
      
      console.log(`Login response status: ${response.status}`)
      
      if (!response.ok) {
        // Try to get error message from response
        let errorMessage = 'Login failed'
        try {
          const errorData = await response.json()
          errorMessage = errorData.detail || errorData.message || `HTTP ${response.status}: ${response.statusText}`
        } catch (e) {
          errorMessage = `HTTP ${response.status}: ${response.statusText || 'Connection error'}`
        }
        
        console.error('Login failed:', errorMessage)
        alert(`Login failed: ${errorMessage}`)
        return false
      }
      
      const data = await response.json()
      console.log('Login successful, received token')
      
      if (!data.access_token) {
        console.error('No access token in response:', data)
        alert('Login failed: No token received from server')
        return false
      }
      
      set({ 
        user: { username, role: username === 'admin' ? 'admin' : 'viewer' },
        token: data.access_token 
      })
      localStorage.setItem('token', data.access_token)
      return true
      
    } catch (error) {
      console.error('Login error:', error)
      
      // Better error messages
      let errorMessage = 'Login failed'
      if (error.message.includes('fetch')) {
        errorMessage = `Cannot connect to server at ${API_BASE}. Is the backend running?`
      } else if (error.message.includes('Network')) {
        errorMessage = 'Network error. Check your connection and ensure backend is running.'
      } else {
        errorMessage = `Login error: ${error.message}`
      }
      
      alert(errorMessage)
      return false
    }
  },
  
  logout: () => {
    set({ user: null, token: null })
    localStorage.removeItem('token')
  },
  
  getAuthHeaders: () => {
    const token = localStorage.getItem('token')
    return token ? { 'Authorization': `Bearer ${token}` } : {}
  },
  
  initAuth: () => {
    const token = localStorage.getItem('token')
    if (token) {
      // Verify token is still valid by making a test request
      fetch(`${API_BASE}/internal/health`, {
        headers: { 'Authorization': `Bearer ${token}` }
      }).then(response => {
        if (response.ok) {
          // Token is valid, restore user state
          const username = 'admin' // In real implementation, decode from token
          set({ 
            user: { username, role: username === 'admin' ? 'admin' : 'viewer' },
            token: token 
          })
        } else {
          // Token is invalid, clear it
          localStorage.removeItem('token')
        }
      }).catch(() => {
        localStorage.removeItem('token')
      })
    }
  }
}))
