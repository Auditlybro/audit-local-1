import { useState, useRef, useCallback } from 'react'
import './App.css'
import NoticeDoctor from './NoticeDoctor'

const API_BASE = 'http://localhost:8000'

type Page = 'ghost' | 'notice'

type TallyRow = {
  date: string
  voucher_type: string
  party_name: string
  amount: number
  ledger_name: string
  narration: string
  is_duplicate: boolean
}

/** Indian date: DD MMM YYYY */
function formatDateIndian(date: Date): string {
  const d = date.getDate()
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const m = months[date.getMonth()]
  const y = date.getFullYear()
  return `${d.toString().padStart(2, '0')} ${m} ${y}`
}

/** Tally date YYYYMMDD → "05 Apr 2024" */
function formatTallyDate(dateStr: string): string {
  const raw = dateStr.replace(/\D/g, '').slice(0, 8)
  if (raw.length !== 8) return dateStr
  const year = raw.slice(0, 4)
  const month = raw.slice(4, 6)
  const day = raw.slice(6, 8)
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const mi = parseInt(month, 10) - 1
  if (mi < 0 || mi > 11) return dateStr
  return `${day} ${months[mi]} ${year}`
}

/** Indian numbering: 221100 -> 2,21,100 */
function formatAmountNum(n: number): string {
  const abs = Math.abs(n)
  const str = String(Math.floor(abs))
  if (str.length <= 3) return n < 0 ? `-${str}` : str
  let result = str.slice(-3)
  let rest = str.slice(0, -3)
  while (rest.length) {
    result = rest.slice(-2) + ',' + result
    rest = rest.slice(0, -2)
  }
  return n < 0 ? `-${result}` : result
}

const NAV_ITEMS: { id: Page; label: string; icon: string; disabled?: boolean }[] = [
  { id: 'ghost', label: 'Ghost Analyst', icon: '📊' },
  { id: 'notice', label: 'Notice Doctor', icon: '📋' },
  { id: 'ghost', label: 'Case Memory', icon: '🧠', disabled: true },
  { id: 'ghost', label: 'Settings', icon: '⚙️', disabled: true },
]

function navPage(item: (typeof NAV_ITEMS)[0]): Page {
  return item.disabled ? 'ghost' : item.id
}

function App() {
  const [page, setPage] = useState<Page>('ghost')
  const [rows, setRows] = useState<TallyRow[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [dragOver, setDragOver] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleFile = useCallback(async (file: File) => {
    if (!file.name.toLowerCase().endsWith('.xml')) {
      setError('Please select a .xml file.')
      return
    }
    setError(null)
    setLoading(true)
    setRows([])
    try {
      const form = new FormData()
      form.append('file', file)
      const res = await fetch(`${API_BASE}/parse-tally`, {
        method: 'POST',
        body: form,
      })
      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data.detail || res.statusText)
      }
      const data: TallyRow[] = await res.json()
      setRows(data)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Upload failed.')
    } finally {
      setLoading(false)
      if (inputRef.current) inputRef.current.value = ''
    }
  }, [])

  const handleUpload = () => {
    const input = inputRef.current
    if (!input?.files?.length) return
    handleFile(input.files[0])
  }

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    const f = e.dataTransfer.files[0]
    if (f) handleFile(f)
  }

  const onDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(true)
  }

  const onDragLeave = () => setDragOver(false)

  const totalAmount = rows.reduce((s, r) => s + r.amount, 0)
  const duplicateCount = rows.filter((r) => r.is_duplicate).length
  const dates = rows.map((r) => r.date).filter(Boolean)
  const dateRange = dates.length
    ? `${formatTallyDate(dates.reduce((a, b) => (a < b ? a : b)))} – ${formatTallyDate(dates.reduce((a, b) => (a > b ? a : b)))}`
    : '—'

  const pageTitle = page === 'ghost' ? 'Ghost Analyst' : 'Notice Doctor'
  const pageSubtitle =
    page === 'ghost' ? 'Tally XML → Ledger Reconciliation' : 'GST Notice → Draft Reply'

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="sidebar-logo">
          <span className="sidebar-logo-icon">AL</span>
          <span className="sidebar-logo-text">Audit-Local</span>
        </div>
        <nav className="sidebar-nav">
          {NAV_ITEMS.map((item, i) => (
            <button
              key={`${item.id}-${i}`}
              type="button"
              className={`sidebar-nav-item ${!item.disabled && ((page === 'ghost' && i === 0) || (page === 'notice' && i === 1)) ? 'active' : ''} ${item.disabled ? 'disabled' : ''}`}
              onClick={() => !item.disabled && setPage(navPage(item))}
              style={{ animationDelay: `${i * 50}ms` }}
            >
              <span className="sidebar-nav-icon">{item.icon}</span>
              <span>{item.label}</span>
            </button>
          ))}
        </nav>
        <div className="sidebar-footer">
          <span className="sidebar-offline-dot" />
          100% Offline · DPDP Compliant
        </div>
      </aside>

      <div className="main-wrap">
        <header className="topbar">
          <div>
            <h1 className="topbar-title">{pageTitle}</h1>
            <p className="topbar-subtitle">{pageSubtitle}</p>
          </div>
          <time className="topbar-date">{formatDateIndian(new Date())}</time>
        </header>

        <main className="main-content">
          {page === 'notice' && <NoticeDoctor />}

          {page === 'ghost' && (
            <div className="ghost-page">
              <div
                className={`upload-zone ${dragOver ? 'drag-over' : ''}`}
                onDrop={onDrop}
                onDragOver={onDragOver}
                onDragLeave={onDragLeave}
                onClick={() => inputRef.current?.click()}
              >
                <input
                  ref={inputRef}
                  type="file"
                  accept=".xml"
                  onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
                  style={{ display: 'none' }}
                />
                <span className="upload-zone-icon">📄</span>
                <span className="upload-zone-text">
                  Drop Tally XML file here or click to browse
                </span>
              </div>

              {loading && (
                <div className="ghost-loading">
                  <span className="spinner" />
                  <span>Parsing…</span>
                </div>
              )}

              {error && <div className="ghost-error">{error}</div>}

              {rows.length > 0 && !loading && (
                <>
                  <div className="ghost-stats">
                    <div className="ghost-stat-card">
                      <span className="ghost-stat-value">{rows.length}</span>
                      <span className="ghost-stat-label">Total Vouchers</span>
                    </div>
                    <div className="ghost-stat-card">
                      <span className="ghost-stat-value">{formatAmountNum(totalAmount)}</span>
                      <span className="ghost-stat-label">Total Amount</span>
                    </div>
                    <div className="ghost-stat-card">
                      <span className="ghost-stat-value">{duplicateCount}</span>
                      <span className="ghost-stat-label">Duplicates Found</span>
                    </div>
                    <div className="ghost-stat-card">
                      <span className="ghost-stat-value ghost-stat-date">{dateRange}</span>
                      <span className="ghost-stat-label">Date Range</span>
                    </div>
                  </div>
                  <div className="ghost-table-wrap">
                    <table className="ghost-table">
                      <thead>
                        <tr>
                          <th>Date</th>
                          <th>Party Name</th>
                          <th>Amount</th>
                          <th>Ledger</th>
                          <th>Type</th>
                          <th>Duplicate?</th>
                        </tr>
                      </thead>
                      <tbody>
                        {rows.map((row, i) => (
                          <tr
                            key={i}
                            className={row.is_duplicate ? 'duplicate' : ''}
                            style={{ animationDelay: `${i * 20}ms` }}
                          >
                            <td className="ghost-cell-mono">{formatTallyDate(row.date)}</td>
                            <td>{row.party_name}</td>
                            <td className="ghost-cell-mono">{formatAmountNum(row.amount)}</td>
                            <td>{row.ledger_name}</td>
                            <td>{row.voucher_type}</td>
                            <td>{row.is_duplicate ? 'Yes' : '—'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </>
              )}
            </div>
          )}
        </main>
      </div>
    </div>
  )
}

export default App
