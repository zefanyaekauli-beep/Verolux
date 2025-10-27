import React from 'react'
import useEvents from '../stores/events'
export default function RecentEvents(){
  const events = useEvents(s=>s.list)
  return <div className='card'>
    <div style={{fontWeight:600, marginBottom:8}}>Recent Events</div>
    <div style={{maxHeight:240, overflow:'auto'}}>
      {events.slice(-400).reverse().map((e,i)=>(
        <div key={i} style={{fontSize:12, borderTop:'1px dashed #1f2937', padding:'6px 0'}}>
          <b>{e.cls}</b> {Math.round(e.conf*100)}% · {new Date(e.ts*1000).toLocaleTimeString()}
        </div>
      ))}
    </div>
  </div>
}
