import { useEffect, useState } from 'react'

function App() {
  const [message, setMessage] = useState('Loading...')
  const [dbStatus, setDbStatus] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    Promise.all([
      fetch('/api/hello').then(response => {
        if (!response.ok) throw new Error('Backend unavailable')
        return response.json()
      }),
      fetch('/api/db/status').then(response => {
        if (!response.ok) throw new Error('Database status unavailable')
        return response.json()
      }),
    ])
      .then(([helloData, dbData]) => {
        setMessage(helloData.message)
        setDbStatus(dbData)
      })
      .catch(() => {
        setError('Unable to reach the FastAPI backend')
      })
  }, [])

  return (
    <div className="container">
      <header className="header">
        <h1>Cloud Native Template</h1>
        <p className="subtitle">React + FastAPI + Docker</p>
      </header>

      <main className="card">
        <h2>Backend Message</h2>
        {error ? (
          <div className="error-message">
            <p>{error}</p>
            <small>Check that the backend is running on port 8000</small>
          </div>
        ) : (
          <>
            <p className="backend-message">{message}</p>
            {dbStatus && (
              <div className="db-status">
                <p>DB enabled: {dbStatus.enabled ? 'yes' : 'no'}</p>
                <p>DB type: {dbStatus.type ?? 'none'}</p>
                <p>DB connected: {dbStatus.connected ? 'yes' : 'no'}</p>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  )
}

export default App
