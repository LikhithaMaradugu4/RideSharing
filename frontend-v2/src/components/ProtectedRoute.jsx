import { useEffect, useState } from 'react'
import { Navigate } from 'react-router-dom'
import tokenStorage from '../services/tokenStorage'

function ProtectedRoute({ children }) {
  const [ready, setReady] = useState(false)
  const [authed, setAuthed] = useState(false)

  useEffect(() => {
    const token = tokenStorage.get('jwt_token')
    setAuthed(!!token)
    setReady(true)
  }, [])

  if (!ready) return null

  return authed ? children : <Navigate to="/login" replace />
}

export default ProtectedRoute
