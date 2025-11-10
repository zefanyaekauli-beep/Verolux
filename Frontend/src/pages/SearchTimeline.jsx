import React, { useEffect, useState } from 'react'

export default function SearchTimeline(){
  const [query, setQuery] = useState({
    from: new Date(Date.now()-3600*1000).toISOString().slice(0,16),
    to: new Date().toISOString().slice(0,16),
    people: true,
    vehicles: true,
    zone: '',
    idleMins: 0
  })
  const [results, setResults] = useState([])

  const runSearch = async () => {
    // Stub: integrate backend search later
    const items = Array.from({length: 10}, (_,i)=>({
      id: `EVT-${Date.now().toString().slice(-6)}-${i}`,
      ts: new Date(Date.now()-i*600000),
      camera: `Camera-${(i%6)+1}`,
      summary: i%2? 'Person in zone' : 'Vehicle idle',
      attributes: i%2? ['person','zone'] : ['vehicle','idle']
    }))
    setResults(items)
  }

  useEffect(()=>{ runSearch() }, [])

  return (
    <div className="min-h-screen verolux-pattern p-6">
      <div className="max-w-6xl mx-auto">
        <h1 className="verolux-heading-3 mb-4">Search / Timeline / Filters</h1>
        <div className="verolux-card mb-4 grid md:grid-cols-4 gap-3">
          <div>
            <label className="text-xs text-slate-500">From</label>
            <input type="datetime-local" value={query.from} onChange={e=>setQuery(q=>({...q, from:e.target.value}))} className="w-full verolux-input"/>
          </div>
          <div>
            <label className="text-xs text-slate-500">To</label>
            <input type="datetime-local" value={query.to} onChange={e=>setQuery(q=>({...q, to:e.target.value}))} className="w-full verolux-input"/>
          </div>
          <div className="flex items-end gap-2">
            <label className="flex items-center gap-1 text-sm"><input type="checkbox" checked={query.people} onChange={e=>setQuery(q=>({...q, people:e.target.checked}))}/>People</label>
            <label className="flex items-center gap-1 text-sm"><input type="checkbox" checked={query.vehicles} onChange={e=>setQuery(q=>({...q, vehicles:e.target.checked}))}/>Vehicles</label>
          </div>
          <div>
            <label className="text-xs text-slate-500">Zone</label>
            <input value={query.zone} onChange={e=>setQuery(q=>({...q, zone:e.target.value}))} placeholder="zone name" className="w-full verolux-input"/>
          </div>
          <div>
            <label className="text-xs text-slate-500">Idle ≥ minutes</label>
            <input type="number" min="0" value={query.idleMins} onChange={e=>setQuery(q=>({...q, idleMins:parseInt(e.target.value||'0',10)}))} className="w-full verolux-input"/>
          </div>
          <div className="flex items-end">
            <button onClick={runSearch} className="verolux-btn verolux-btn-primary">Search</button>
          </div>
        </div>

        <div className="verolux-card">
          <div className="mb-3 verolux-caption">Timeline (stub): {query.from} → {query.to}</div>
          <div className="divide-y">
            {results.map(r=> (
              <div key={r.id} className="py-3 flex items-center justify-between">
                <div>
                  <div className="verolux-body">{r.summary}</div>
                  <div className="verolux-caption">{r.ts.toLocaleString()} · {r.camera}</div>
                </div>
                <div className="flex gap-2 items-center">
                  {r.attributes.map(a=> <span key={a} className="verolux-badge verolux-badge-primary">{a}</span>)}
                  <button className="verolux-btn verolux-btn-outline">Preview</button>
                  <button className="verolux-btn verolux-btn-secondary">Export</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}


