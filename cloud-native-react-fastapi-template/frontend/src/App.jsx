import { useState, useEffect } from 'react'

function App() {
  const [message, setMessage] = useState('Loading...')
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch('/api/hello')
      .then(response => {
        if (!response.ok) {
          throw new Error('Network Error')
        }
        return response.json()
      })
      .then(data => {
        setMessage(data.message)
      })
      .catch(err => {
        console.error(err)
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
        <h2>Backend Message:</h2>
        {error ? (
          <div className="error-message">
            <p>{error}</p>
            <small>Check that the backend is running on port 8000</small>
          </div>
        ) : (
          <p className="backend-message">{message}</p>
        )}
      </main>

    </div>
  )
}

export default App
