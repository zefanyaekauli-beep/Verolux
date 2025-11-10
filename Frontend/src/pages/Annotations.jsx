import React, { useState } from 'react'

export default function Annotations(){
  const [clips, setClips] = useState([])
  const [note, setNote] = useState('')

  const addClip = () => {
    const id = `CLP-${Date.now().toString().slice(-6)}`
    setClips(prev=> [{ id, ts: new Date(), note }, ...prev])
    setNote('')
  }

  const share = (clip) => {
    // Stub: integrate email/whatsapp
    alert(`Share link created for ${clip.id}`)
  }

  return (
    <div className="min-h-screen verolux-pattern p-6">
      <div className="max-w-5xl mx-auto">
        <h1 className="verolux-heading-3 mb-4">Annotations & Sharing</h1>
        <div className="verolux-card mb-4">
          <div className="verolux-caption mb-2">Create an annotation for the current incident/clip</div>
          <textarea value={note} onChange={e=>setNote(e.target.value)} rows={3} className="w-full verolux-input" placeholder="Add notes (what, who, action)..."/>
          <div className="mt-3 flex gap-2">
            <button onClick={addClip} disabled={!note.trim()} className="verolux-btn verolux-btn-primary disabled:opacity-50">Save Annotation</button>
            <button className="verolux-btn verolux-btn-outline">Attach Snapshot</button>
            <button className="verolux-btn verolux-btn-outline">Attach Video Clip</button>
          </div>
        </div>

        <div className="verolux-card">
          <h2 className="verolux-heading-4 mb-3">Recent Annotations</h2>
          <div className="divide-y">
            {clips.length===0 && <div className="verolux-caption py-6">No annotations yet.</div>}
            {clips.map(c=> (
              <div key={c.id} className="py-3 flex items-center justify-between">
                <div>
                  <div className="verolux-body">{c.id}</div>
                  <div className="verolux-caption">{c.ts.toLocaleString()}</div>
                  <div className="verolux-body-secondary mt-1">{c.note}</div>
                </div>
                <div className="flex gap-2">
                  <button onClick={()=>share(c)} className="verolux-btn verolux-btn-outline">Share</button>
                  <button className="verolux-btn verolux-btn-secondary">Download</button>
                </div>
              </div>
            ))}
          </div>
          <div className="verolux-caption mt-3">Audit log and permissions integration can be added here.</div>
        </div>
      </div>
    </div>
  )
}


