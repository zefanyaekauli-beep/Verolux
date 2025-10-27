import React from 'react'
import useAlerts from '../stores/alerts'
export default function AlertsPanel(){
  const alerts = useAlerts(s=>s.active)
  return <div className='card'>
    <div style={{fontWeight:600, marginBottom:8}}>Active Alerts</div>
    {alerts.length? alerts.slice(0,50).map((a,i)=>(
      <div key={i} style={{fontSize:12, borderTop:'1px solid #1f2937', padding:'6px 0'}}>
        <b>{a.type}</b> · {new Date(a.ts*1000).toLocaleTimeString()} · {a.message}
      </div>
    )) : <div style={{opacity:.7}}>No alerts</div>}
  </div>
}
