import { useState } from 'react'
import './NoticeDoctor.css'

const API_BASE = 'http://localhost:8000'

/** Indian numbering: 221100 -> 2,21,100 (lakhs/crores). */
function formatAmount(amt: string): string {
  const s = amt.replace(/,/g, '').trim()
  const n = parseFloat(s)
  if (Number.isNaN(n)) return amt
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

type NoticeSummary = {
  notice_type: string
  section_number: string
  tax_period: string
  amount_demanded: string
  deadline: string
}

type LawSection = {
  section_id: string
  title: string
  summary: string
}

type DraftReplyResponse = {
  notice_summary: NoticeSummary
  relevant_sections: LawSection[]
  draft_reply: string
}

export default function NoticeDoctor() {
  const [noticeText, setNoticeText] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<DraftReplyResponse | null>(null)
  const [draftReply, setDraftReply] = useState('')
  const [copied, setCopied] = useState(false)

  const handleAnalyze = async () => {
    if (!noticeText.trim()) {
      setError('Please paste a GST notice.')
      return
    }
    setError(null)
    setResult(null)
    setLoading(true)
    setCopied(false)
    try {
      const res = await fetch(`${API_BASE}/draft-reply`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ notice_text: noticeText }),
      })
      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data.detail || res.statusText)
      }
      const data: DraftReplyResponse = await res.json()
      setResult(data)
      setDraftReply(data.draft_reply || '')
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Request failed.')
    } finally {
      setLoading(false)
    }
  }

  const handleCopyReply = async () => {
    const text = result ? draftReply : ''
    if (!text) return
    try {
      await navigator.clipboard.writeText(text)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      setError('Copy failed.')
    }
  }

  const summary = result?.notice_summary
  const sections = result?.relevant_sections ?? []

  const isSectionCitedInNotice = (sectionId: string) => {
    if (!noticeText.trim() || !sectionId) return false
    const lower = noticeText.toLowerCase()
    const idLower = sectionId.toLowerCase()
    if (lower.includes(idLower)) return true
    const numericPart = sectionId.replace(/\s/g, '').replace(/section|rule/gi, '').trim()
    if (numericPart && lower.includes(numericPart)) return true
    return false
  }

  return (
    <div className="notice-doctor">
      <div className="notice-doctor-layout">
        <div className="notice-doctor-left">
          <label className="notice-doctor-label">Paste GST notice (plain text)</label>
          <textarea
            className="notice-doctor-textarea"
            value={noticeText}
            onChange={(e) => setNoticeText(e.target.value)}
            placeholder="Paste the full text of the GST notice here..."
            rows={16}
          />
          <button
            type="button"
            className="notice-doctor-btn"
            onClick={handleAnalyze}
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="notice-doctor-btn-spinner" />
                <span>Analyzing…</span>
              </>
            ) : (
              'Analyze & Draft Reply'
            )}
          </button>
        </div>

        <div className="notice-doctor-right">
          {loading && (
            <div className="notice-doctor-loading">
              <span className="spinner" />
              <span>Analyzing notice & drafting reply…</span>
            </div>
          )}

          {error && <div className="notice-doctor-error">{error}</div>}

          {result && !loading && (
            <>
              <section className="notice-doctor-block">
                <h3>Notice summary</h3>
                <dl className="notice-doctor-summary">
                  <div><dt>Type</dt><dd>{summary?.notice_type || '—'}</dd></div>
                  <div><dt>Section</dt><dd>{summary?.section_number || '—'}</dd></div>
                  <div><dt>Tax period</dt><dd>{summary?.tax_period || '—'}</dd></div>
                  <div><dt>Amount demanded</dt><dd className={summary?.amount_demanded ? 'amount-value' : ''}>{summary?.amount_demanded ? `₹${formatAmount(summary.amount_demanded)}` : '—'}</dd></div>
                  <div><dt>Deadline</dt><dd>{summary?.deadline || '—'}</dd></div>
                </dl>
              </section>

              <section className="notice-doctor-block">
                <h3>Relevant law sections</h3>
                <ul className="notice-doctor-sections">
                  {sections.length === 0 ? (
                    <li className="notice-doctor-section-empty">No sections retrieved.</li>
                  ) : (
                    sections.map((s, i) => {
                      const cited = isSectionCitedInNotice(s.section_id)
                      return (
                        <li key={i} className="notice-doctor-section">
                          <span className="notice-doctor-section-head">
                            <strong>{s.section_id}</strong>
                            {' '}
                            <span className={cited ? 'notice-doctor-badge cited' : 'notice-doctor-badge related'}>
                              {cited ? 'DIRECTLY CITED' : 'RELATED'}
                            </span>
                          </span>
                          <span className="notice-doctor-section-title"> — {s.title}</span>
                          <p>{s.summary}</p>
                        </li>
                      )
                    })
                  )}
                </ul>
              </section>

              <section className="notice-doctor-block">
                <h3>Draft reply</h3>
                <div className="notice-doctor-reply-wrap">
                  <textarea
                    className="notice-doctor-reply"
                    value={draftReply}
                    onChange={(e) => setDraftReply(e.target.value)}
                    rows={12}
                  />
                  <button
                    type="button"
                    className="notice-doctor-copy"
                    onClick={handleCopyReply}
                    disabled={!draftReply?.trim()}
                  >
                    {copied ? 'Copied ✓' : 'Copy Reply'}
                  </button>
                </div>
              </section>
            </>
          )}

          {!result && !loading && !error && (
            <div className="notice-doctor-placeholder">
              Paste a notice and click &quot;Analyze & Draft Reply&quot; to see summary and draft.
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
