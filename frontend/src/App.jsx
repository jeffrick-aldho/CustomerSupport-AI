import React, { useMemo, useState } from 'react'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export default function App() {
  const [query, setQuery] = useState('My product arrived late and damaged. Can I get a refund?')
  const [mode, setMode] = useState('strict')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  const modeLabel = useMemo(() => {
    return mode === 'strict' ? 'Strict Policy' : 'Friendly Tone'
  }, [mode])

  async function handleGenerate(e) {
    e.preventDefault()
    setLoading(true)
    setError('')
    setResult(null)

    try {
      const response = await fetch(`${API_BASE_URL}/api/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query, mode }),
      })

      if (!response.ok) {
        const text = await response.text()
        throw new Error(text || 'Request failed')
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError(err.message || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <div className="background" />
      <main className="shell">
        <section className="hero">
          <p className="eyebrow">BM25 + Sarvam AI</p>
          <h1>Customer Support Response Generator</h1>
          <p className="subhead">
            Draft policy-aware support replies with controlled tone and retrieval from local company policies.
          </p>
        </section>

        <section className="card">
          <form onSubmit={handleGenerate} className="form">
            <label>
              Customer Complaint
              <textarea
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                rows="5"
                placeholder="Type the customer issue here..."
              />
            </label>

            <div className="row">
              <label>
                Mode
                <select value={mode} onChange={(e) => setMode(e.target.value)}>
                  <option value="strict">Strict Policy</option>
                  <option value="friendly">Friendly Tone</option>
                </select>
              </label>

              <div className="mode-box">
                <span className="mode-label">{modeLabel}</span>
                <span className="mode-desc">
                  {mode === 'strict'
                    ? 'Lower creativity, concise and deterministic.'
                    : 'Warmer tone with empathetic phrasing.'}
                </span>
              </div>
            </div>

            <button type="submit" disabled={loading}>
              {loading ? 'Generating...' : 'Generate Response'}
            </button>
          </form>
        </section>

        {error && <section className="error">{error}</section>}

        {result && (
          <section className="results">
            <div className="card">
              <h2>AI Response</h2>
              <p className="response">{result.response}</p>
            </div>

            <div className="card">
              <h2>Retrieved Documents</h2>
              {result.sources.length === 0 ? (
                <p>No policy documents were retrieved.</p>
              ) : (
                <div className="docs">
                  {result.sources.map((doc, index) => (
                    <article key={`${doc.title}-${index}`} className="doc">
                      <h3>
                        {doc.title} <span>score: {doc.score.toFixed(3)}</span>
                      </h3>
                      <p>{doc.content}</p>
                    </article>
                  ))}
                </div>
              )}
            </div>

            <div className="card">
              <h2>Debug Info</h2>
              <p>
                Fallback: <strong>{String(result.used_fallback)}</strong>
              </p>
              <p>
                Temperature: <strong>{result.parameters.temperature}</strong>
              </p>
              <p>
                Max tokens: <strong>{result.parameters.max_tokens}</strong>
              </p>
            </div>
          </section>
        )}
      </main>
    </div>
  )
}
