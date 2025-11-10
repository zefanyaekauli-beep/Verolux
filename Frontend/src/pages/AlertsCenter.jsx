import React, { useState } from 'react'
import AlertsPanel from '../components/AlertsPanel'

export default function AlertsCenter(){
  const [rules, setRules] = useState([
    { id: 'r1', name: 'After-hours person in Restricted Area', enabled: true },
    { id: 'r2', name: 'Vehicle idle > 10 min at Loading Dock', enabled: true },
    { id: 'r3', name: 'Crowd > 8 in Gate Area', enabled: false }
  ])
  return (
    <div className="min-h-screen verolux-pattern p-6">
      <div className="max-w-6xl mx-auto grid md:grid-cols-2 gap-6">
        <div className="verolux-card">
          <h2 className="verolux-heading-4 mb-3">Active Alerts</h2>
          <AlertsPanel/>
        </div>
        <div className="verolux-card">
          <h2 className="verolux-heading-4 mb-3">Alert Rules (stub)</h2>
          <div className="space-y-2 verolux-body-secondary">
            {rules.map(r=> (
              <label key={r.id} className="flex items-center justify-between bg-black/30 rounded p-2">
                <span>{r.name}</span>
                <input type="checkbox" checked={r.enabled} onChange={()=>setRules(rs=>rs.map(x=>x.id===r.id?{...x, enabled:!x.enabled}:x))}/>
              </label>
            ))}
          </div>
          <div className="mt-4 verolux-caption">Mobile/SMS integrations can be configured here.</div>
        </div>
      </div>
    </div>
  )
}



