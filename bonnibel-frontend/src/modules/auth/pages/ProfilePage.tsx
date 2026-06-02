import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { userService } from '@/services/userService'
import { useAuthStore } from '../store/authStore' // 1. IMPORT TWOJEGO STORE'A
import type { User, UserStatus } from '@/types/domain'

export default function ProfilePage() {
  const navigate = useNavigate()
  
  // 2. WYCIĄGAMY FUNKCJĘ WYLOGOWANIA ZE STORE'A
  const logoutInStore = useAuthStore((state) => state.logout)
  
  const [user, setUser] = useState<User | null>(null)
  const [name, setName] = useState('')
  const [surname, setSurname] = useState('')
  const [email, setEmail] = useState('')
  const [status, setStatus] = useState<UserStatus>('AVAILABLE')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [successMessage, setSuccessMessage] = useState('')

  useEffect(() => {
    userService.getCurrentUser()
      .then(currentUser => {
        setUser(currentUser)
        setName(currentUser.name || '')
        setSurname(currentUser.surname || '')
        setEmail(currentUser.email || '')
        setStatus(currentUser.status || 'AVAILABLE')
      })
      .catch((err) => {
        console.error("Błąd ładowania profilu:", err)
        // 3. OBSŁUGA NOWEGO UŻYTKOWNIKA:
        // Jeśli profilu nie ma (np. świeżo po rejestracji), tworzymy pusty obiekt placeholder,
        // dzięki czemu strona się nie zablokuje i użytkownik uzupełni dane po raz pierwszy.
        const cachedUserId = localStorage.getItem('userId') || 'nowy_użytkownik';
        setUser({
          userId: cachedUserId,
          email: '',
          name: '',
          surname: '',
          status: 'AVAILABLE',
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

  // 4. POPRAWIONE WYLOGOWANIE KORZYSTAJĄCE Z CENTRALNEGO AUTORYZOWANEGO SYSTEMU
  const handleLogout = () => {
    logoutInStore() // To czyści cały localStorage oraz przestawia stan aplikacji w Zustand
    navigate('/login')
  }

  if (loading) {
    return <div style={{ padding: '24px', textAlign: 'center' }}>Ładowanie danych profilu...</div>
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
                border: '1px solid #cbd5e0', // Ładniejsza, wyraźniejsza ramka
                background: '#ffffff',       // Zmienione na białe tło - sygnalizuje możliwość pisania
                color: '#1a202c',            // Zmienione na ciemny tekst
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
              Status dostępności w zespole
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
              <option value="AVAILABLE" style={{ color: '#1a202c', backgroundColor: '#ffffff' }}>Dostępny (AVAILABLE)</option>
              <option value="BUSY" style={{ color: '#1a202c', backgroundColor: '#ffffff' }}>Zajęty (BUSY)</option>
              <option value="OPEN_TO_TASKS" style={{ color: '#1a202c', backgroundColor: '#ffffff' }}>Wolny do zadań (OPEN_TO_TASKS)</option>
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
