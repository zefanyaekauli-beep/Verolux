import { create } from 'zustand'
export default create(set=>({currentPage:'Dashboard', setPage:(p)=>set({currentPage:p})}))
