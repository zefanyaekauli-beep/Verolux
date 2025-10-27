import { create } from 'zustand'
export default create(set=>({status:{model_loaded:false, device:'cpu', framework:'none'}, setStatus:(s)=>set({status:s})}))
