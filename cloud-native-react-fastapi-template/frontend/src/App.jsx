import { useState, useEffect } from 'react'

function App() {
  const [message, setMessage] = useState('Chargement...')
  const [error, setError] = useState(null)

  useEffect(() => {
    // Appel à l'API FastAPI via proxy
    fetch('/api/hello')
      .then(response => {
        if (!response.ok) {
          throw new Error('Erreur réseau')
        }
        return response.json()
      })
      .then(data => {
        setMessage(data.message)
      })
      .catch(err => {
        console.error(err)
        setError('Impossible de contacter le backend FastAPI')
      })
  }, [])

  return (
    <div className="container">
      <header className="header">
        <h1>Cloud Native Template</h1>
        <p className="subtitle">React + FastAPI + Docker</p>
      </header>
      
      <main className="card">
        <h2>Message du Backend :</h2>
        {error ? (
          <div className="error-message">
            <p>{error}</p>
            <small>Vérifiez que le backend tourne sur le port 8000</small>
          </div>
        ) : (
          <p className="backend-message">{message}</p>
        )}
      </main>

    </div>
  )
}

export default App
