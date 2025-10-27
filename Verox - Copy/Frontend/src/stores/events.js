import { create } from 'zustand'
export default create(set=>({list:[], push:(payload)=>set(s=>({list:[...s.list, ...(payload.detections||[]).map(d=>({ts:payload.ts, cls:d.cls, conf:d.conf}))].slice(-8000)}))}))
