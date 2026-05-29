import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { userService } from '@/services/userService'
import { useAuthStore } from '../store/authStore' 
import type { User, UserStatus } from '@/types/domain'

export default function ProfilePage() {
  const navigate = useNavigate()
  
  const logoutInStore = useAuthStore((state) => state.logout)
  
  const [user, setUser] = useState<User | null>(null)
  const [name, setName] = useState('')
  const [surname, setSurname] = useState('')
  const [email, setEmail] = useState('')
  // 1. ZMIANA: Stan początkowy zmieniony na zgodny z backendem 'ACTIVE'
  const [status, setStatus] = useState<UserStatus>('ACTIVE')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [successMessage, setSuccessMessage] = useState('')

  useEffect(() => {
    setLoading(true)
    userService.getCurrentUser()
      .then(currentUser => {
        setUser(currentUser)
        setName(currentUser.name || '')
        setSurname(currentUser.surname || '')
        setEmail(currentUser.email || '')
        // Jeśli backend z jakiegoś powodu nie przysłał statusu, ustawiamy 'ACTIVE'
        setStatus(currentUser.status || 'ACTIVE')
      })
      .catch((err) => {
        console.error("Błąd ładowania profilu:", err)
        const cachedUserId = localStorage.getItem('userId') || 'nowy_użytkownik';
        
        // 2. ZMIANA: Dopasowanie obiektu placeholder do nowych typów domenowych
        setUser({
          userId: cachedUserId,
          email: '',
          name: '',
          surname: '',
          status: 'ACTIVE', // Zmiana z AVAILABLE na ACTIVE
          isOnline: true
        })
      })
      .finally(() => setLoading(false))
  }, [])

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!user) return

    setSaving(true)
    setSuccessMessage('')

    try {
      const updatedUser = await userService.updateCurrentUser({ name, surname, status, email })
      setUser(updatedUser)
      setSuccessMessage('Profil został pomyślnie zaktualizowany na serwerze!')
    } catch (err) {
      console.error("Błąd zapisu profilu:", err)
    } finally {
      setSaving(false)
    }
  }

  // Zmieniamy funkcję na async
  const handleLogout = async () => {
    try {
      // Czekamy, aż serwer usunie token z bazy i Zustand wyczyści localStorage
      await logoutInStore() 
    } catch (err) {
      console.error("Błąd podczas wylogowywania w komponencie:", err)
    } finally {
      // Dopiero gdy wszystko się skończy, bezpiecznie przekierowujemy na /login
      navigate('/login')
    }
  }

  if (loading) {
    return <div style={{ padding: '24px', textAlign: 'center', color: '#1a202c' }}>Ładowanie danych profilu...</div>
  }

  if (!user) {
    return <div style={{ padding: '24px', textAlign: 'center', color: 'red' }}>Nie odnaleziono profilu użytkownika.</div>
  }

  return (
    <div style={{ padding: '24px', maxWidth: '600px', margin: '0 auto', fontFamily: 'sans-serif' }}>
      <h2 style={{ marginBottom: '24px', color: '#1a202c' }}>Mój Profil</h2>

      <div style={{ background: 'white', border: '1px solid #e2e8f0', borderRadius: '12px', padding: '24px', boxShadow: '0 4px 6px rgba(0,0,0,0.02)' }}>
        <form onSubmit={handleSave}>
          {successMessage && (
            <div style={{ padding: '12px', background: '#e6fffa', color: '#319795', borderRadius: '6px', fontSize: '14px', fontWeight: 'bold', marginBottom: '16px' }}>
              {successMessage}
            </div>
          )}

          {/* E-mail */}
          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', fontSize: '14px', fontWeight: 'bold', color: '#4a5568', marginBottom: '6px' }}>
              Adres e-mail
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="np. jan.kowalski@example.com"
              style={{
                width: '100%',
                padding: '10px 12px',
                borderRadius: '6px',
                border: '1px solid #cbd5e0',
                background: '#ffffff',
                color: '#1a202c',
                fontSize: '14px',
                boxSizing: 'border-box'
              }}
            />
          </div>

          {/* Imię */}
          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', fontSize: '14px', fontWeight: 'bold', color: '#4a5568', marginBottom: '6px' }}>
              Imię
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              style={{
                width: '100%',
                padding: '10px 12px',
                borderRadius: '6px',
                border: '1px solid #cbd5e0',
                background: '#ffffff',
                color: '#1a202c',
                fontSize: '14px',
                boxSizing: 'border-box'
              }}
            />
          </div>

          {/* Nazwisko */}
          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', fontSize: '14px', fontWeight: 'bold', color: '#4a5568', marginBottom: '6px' }}>
              Nazwisko
            </label>
            <input
              type="text"
              value={surname}
              onChange={(e) => setSurname(e.target.value)}
              required
              style={{
                width: '100%',
                padding: '10px 12px',
                borderRadius: '6px',
                border: '1px solid #cbd5e0',
                background: '#ffffff',
                color: '#1a202c',
                fontSize: '14px',
                boxSizing: 'border-box'
              }}
            />
          </div>

          {/* Status Dostępności */}
          <div style={{ marginBottom: '24px' }}>
            <label style={{ display: 'block', fontSize: '14px', fontWeight: 'bold', color: '#4a5568', marginBottom: '6px' }}>
              Status konta użytkownika
            </label>
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value as UserStatus)}
              style={{
                width: '100%',
                padding: '10px 12px',
                borderRadius: '6px',
                border: '1px solid #cbd5e0',
                background: '#ffffff',
                color: '#1a202c',
                fontSize: '14px',
                cursor: 'pointer'
              }}
            >
              {/* 3. ZMIANA: Opcje selecta zmienione na zgodne z bazą danych kolegi */}
              <option value="ACTIVE" style={{ color: '#1a202c', backgroundColor: '#ffffff' }}>Aktywny (ACTIVE)</option>
              <option value="INACTIVE" style={{ color: '#1a202c', backgroundColor: '#ffffff' }}>Nieaktywny (INACTIVE)</option>
              <option value="BANNED" style={{ color: '#1a202c', backgroundColor: '#ffffff' }}>Zablokowany (BANNED)</option>
            </select>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '32px' }}>
            <button
              type="submit"
              disabled={saving}
              style={{
                padding: '10px 20px',
                background: '#0070f3',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontWeight: 'bold',
                fontSize: '14px'
              }}
            >
              {saving ? 'Zapisywanie...' : 'Zapisz zmiany'}
            </button>

            <button
              type="button"
              onClick={handleLogout}
              style={{
                padding: '10px 20px',
                background: '#fff',
                color: '#e53e3e',
                border: '1px solid #fc8181',
                borderRadius: '6px',
                cursor: 'pointer',
                fontWeight: 'bold',
                fontSize: '14px'
              }}
            >
              Wyloguj się
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}