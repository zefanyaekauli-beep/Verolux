import React, { useEffect, useState } from 'react'

export default function Operations(){
  const [idle, setIdle] = useState([])
  useEffect(()=>{
    const iv = setInterval(()=>{
      setIdle(prev=>[...prev, { ts:new Date(), dock: Math.random()*10, warehouse: Math.random()*6 }].slice(-100))
    }, 2000)
    return ()=>clearInterval(iv)
  },[])
  return (
    <div className="min-h-screen verolux-pattern p-6">
      <div className="max-w-6xl mx-auto">
        <h1 className="verolux-heading-3 mb-4">Operations Analytics</h1>
        <div className="grid md:grid-cols-2 gap-6">
          <div className="verolux-card">
            <h2 className="verolux-heading-4 mb-2">Vehicle Idle (min)</h2>
            <div className="verolux-caption">Streaming idle estimates (stub)
              <div className="mt-3 space-y-1 verolux-body-secondary">
                {idle.slice(-10).map((r,i)=> (
                  <div key={i} className="flex justify-between"><span>{r.ts.toLocaleTimeString()}</span><span>Dock {r.dock.toFixed(1)} · Warehouse {r.warehouse.toFixed(1)}</span></div>
                ))}
              </div>
            </div>
          </div>
          <div className="verolux-card">
            <h2 className="verolux-heading-4 mb-2">Presence & Zones</h2>
            <ul className="verolux-body-secondary space-y-1">
              <li>Restricted Area (after-hours): alerts ON</li>
              <li>Loading Dock: crowd threshold 8</li>
              <li>Forklift Bay: PPE required</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}



