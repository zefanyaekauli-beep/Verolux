import React, { useEffect, useRef, useState } from 'react'
import useEvents from '../stores/events'
import useAlerts from '../stores/alerts'

export default function CameraTile({ title='Camera', source='webcam:0' }){
  const imgRef = useRef(null), canvasRef = useRef(null), wsRef = useRef(null)
  const [status, setStatus] = useState('connecting'); const [fps, setFps] = useState(0)
  const push = useEvents(s=>s.push); const evalAlerts = useAlerts(s=>s.eval)

  useEffect(()=>{
    let attempts = 0; let closed = false
    const connect = () => {
      const url = (location.protocol==='https:'?'wss://':'ws://') + location.host + `/ws/detections?source=${encodeURIComponent(source)}`
      const ws = new WebSocket(url); wsRef.current = ws
      ws.onopen = () => { setStatus('connected'); attempts=0 }
      ws.onclose = () => { setStatus('disconnected'); if(!closed){ const delay = Math.min(30000, 1000*Math.pow(2, attempts++)); setTimeout(connect, delay) } }
      ws.onerror = () => setStatus('error')
      ws.onmessage = (ev) => {
        const msg = JSON.parse(ev.data)
        if (msg.type === 'detections'){
          setFps(msg.fps||0); draw(msg.detections); push(msg); evalAlerts(msg)
        }
      }
    }
    connect()
    return ()=>{ closed = true; try{ wsRef.current?.close() }catch{} }
  }, [source])

  const draw = (dets)=>{
    const img=imgRef.current, canvas=canvasRef.current; if(!img||!canvas) return
    const w=img.naturalWidth||img.width, h=img.naturalHeight||img.height; if(!w||!h) return
    const dpr=window.devicePixelRatio||1; canvas.width=Math.round(w*dpr); canvas.height=Math.round(h*dpr)
    canvas.style.width=w+'px'; canvas.style.height=h+'px'
    const ctx=canvas.getContext('2d'); ctx.setTransform(dpr,0,0,dpr,0,0); ctx.clearRect(0,0,w,h)
    for (const d of (dets||[])){
      const [x1,y1,x2,y2]=d.bbox||[]; if([x1,y1,x2,y2].some(v=>typeof v!=='number')) continue
      const rx1=x1*w, ry1=y1*h, rw=(x2-x1)*w, rh=(y2-y1)*h
      ctx.lineWidth=2; ctx.strokeStyle='#00ff88'; ctx.strokeRect(rx1,ry1,rw,rh)
      const label=`${d.cls||'obj'} ${Math.round((d.conf||0)*100)}%`
      const tw=ctx.measureText(label).width+10; ctx.fillStyle='rgba(0,0,0,.6)'; ctx.fillRect(rx1, Math.max(0, ry1-16), tw, 16)
      ctx.fillStyle='#fff'; ctx.fillText(label, rx1+4, Math.max(12, ry1-4))
    }
  }

  return <div className='card'>
    <div className='flex' style={{justifyContent:'space-between'}}>
      <div style={{fontWeight:600}}>{title}</div>
      <div className='badge'>WS: {status} · {fps.toFixed(1)} FPS</div>
    </div>
    <div style={{position:'relative', width:'100%', maxWidth:640}}>
      <img ref={imgRef} src={`/stream?source=${encodeURIComponent(source)}`} alt={title} style={{width:'100%', display:'block'}} onLoad={()=>draw([])}/>
      <canvas ref={canvasRef} style={{position:'absolute', left:0, top:0, pointerEvents:'none'}}/>
    </div>
  </div>
}
