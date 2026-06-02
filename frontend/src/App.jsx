import { useEffect, useMemo, useState } from 'react'

const demoSecret = import.meta.env.VITE_DEMO_SECRET || ''

function App() {
  const [status, setStatus] = useState(null)
  const [product, setProduct] = useState(null)
  const [orders, setOrders] = useState([])
  const [form, setForm] = useState({ customer_name: 'Demo Buyer', customer_email: 'buyer@epita.demo', quantity: 1, secret: demoSecret })
  const [notice, setNotice] = useState('')

  const total = useMemo(() => product ? Number(product.price) * Number(form.quantity || 1) : 0, [product, form.quantity])

  const loadStore = async () => {
    const [statusResponse, productsResponse, ordersResponse] = await Promise.all([
      fetch('/api/status'),
      fetch('/api/products'),
      fetch('/api/orders'),
    ])
    setStatus(await statusResponse.json())
    const products = await productsResponse.json()
    setProduct(products[0])
    setOrders(await ordersResponse.json())
  }

  useEffect(() => {
    loadStore().catch(() => setNotice('Backend not reachable. Start Docker Compose and refresh.'))
  }, [])

  const checkout = async (event) => {
    event.preventDefault()
    setNotice('')
    const response = await fetch('/api/checkout', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Demo-Secret': form.secret,
      },
      body: JSON.stringify({
        customer_name: form.customer_name,
        customer_email: form.customer_email,
        quantity: Number(form.quantity),
      }),
    })

    if (!response.ok) {
      const error = await response.json()
      setNotice(error.detail || 'Checkout failed')
      return
    }

    const order = await response.json()
    setNotice(`Order #${order.id} saved in PostgreSQL.`)
    await loadStore()
  }

  if (!product) {
    return <main className="shell"><section className="panel">Loading RoomPulse Store...</section></main>
  }

  return (
    <main className="shell">
      <section className="hero">
        <div className="hero-copy">
          <span className="eyebrow">Smart office IoT ecommerce demo</span>
          <h1>Sell the meeting-room device that frees unused spaces automatically.</h1>
          <p>{product.description}</p>
          <div className="checks">
            <span>Calendar sync</span>
            <span>No-show release</span>
            <span>Privacy by design</span>
          </div>
        </div>
        <div className="product-card">
          <img src={product.image} alt={product.name} />
          <h2>{product.name}</h2>
          <p>{product.tagline}</p>
          <div className="price-row">
            <strong>{status?.currency || 'EUR'} {Number(product.price).toFixed(2)}</strong>
            <span>{product.stock} in stock</span>
          </div>
        </div>
      </section>

      <section className="grid">
        <form className="panel checkout" onSubmit={checkout}>
          <h2>Live checkout</h2>
          <label>Name<input value={form.customer_name} onChange={e => setForm({ ...form, customer_name: e.target.value })} /></label>
          <label>Email<input value={form.customer_email} onChange={e => setForm({ ...form, customer_email: e.target.value })} /></label>
          <label>Quantity<input type="number" min="1" max="10" value={form.quantity} onChange={e => setForm({ ...form, quantity: e.target.value })} /></label>
          <label>Demo secret<input value={form.secret} onChange={e => setForm({ ...form, secret: e.target.value })} /></label>
          <div className="total"><span>Total</span><strong>{status?.currency || 'EUR'} {total.toFixed(2)}</strong></div>
          <button type="submit">Place demo order</button>
          {notice && <p className="notice">{notice}</p>}
        </form>

        <section className="panel ops">
          <h2>Service checks</h2>
          <div className="status-line"><span>PostgreSQL</span><strong>{status?.database ? 'connected' : 'offline'}</strong></div>
          <div className="status-line"><span>Docker secret</span><strong>{status?.secret_loaded ? 'loaded' : 'missing'}</strong></div>
          <div className="status-line"><span>API</span><strong>{status?.app || 'RoomPulse Store'}</strong></div>
          <h3>Recent PostgreSQL orders</h3>
          <div className="orders">
            {orders.length === 0 ? <p>No orders yet.</p> : orders.map(order => (
              <article key={order.id}>
                <strong>#{order.id} · {order.customer_name}</strong>
                <span>{order.quantity} unit(s) · {status?.currency || 'EUR'} {Number(order.total).toFixed(2)}</span>
              </article>
            ))}
          </div>
        </section>
      </section>
    </main>
  )
}

export default App
