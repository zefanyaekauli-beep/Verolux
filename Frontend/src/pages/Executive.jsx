import React from 'react'

export default function Executive(){
  const cards = [
    { title:'Unauthorized Entries (30d)', value:'42', change:'+8%', color:'bg-red-600' },
    { title:'Avg Response Time', value:'2.4m', change:'-12%', color:'bg-blue-600' },
    { title:'Camera Uptime', value:'99.2%', change:'+0.4%', color:'bg-emerald-600' },
    { title:'Vehicle Idle >10m', value:'17', change:'-5%', color:'bg-amber-600' },
  ]
  return (
    <div className="min-h-screen verolux-pattern p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="verolux-heading-3 mb-6">Executive Dashboard</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4 mb-6">
          {cards.map((c,i)=> (
            <div key={i} className={`rounded-xl p-5 text-white ${c.color} shadow-lg`}>
              <div className="verolux-caption">{c.title}</div>
              <div className="text-3xl font-bold mt-2">{c.value}</div>
              <div className="text-sm opacity-90 mt-1">{c.change}</div>
            </div>
          ))}
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="verolux-card">
            <h2 className="verolux-heading-4 mb-2">Top Sites by Incidents</h2>
            <ul className="verolux-body-secondary space-y-2">
              <li>Warehouse West · 12</li>
              <li>Plant A · 9</li>
              <li>HQ Lobby · 6</li>
            </ul>
          </div>
          <div className="verolux-card">
            <h2 className="verolux-heading-4 mb-2">Monthly Trend</h2>
            <div className="verolux-caption">Charts here (integrate with analytics)</div>
          </div>
        </div>
      </div>
    </div>
  )
}



