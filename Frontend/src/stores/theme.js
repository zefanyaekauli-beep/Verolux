import { create } from 'zustand'
export default create(set=>({theme:'dark', setTheme:(t)=>set({theme:t})}))
