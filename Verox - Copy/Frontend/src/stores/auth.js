import { create } from 'zustand'
const USERS={admin:{password:'admin',role:'admin'},viewer:{password:'viewer',role:'viewer'}}
export default create(set=>({user:{username:'admin',role:'admin'}, login:(u,p)=>{const x=USERS[u]; if(x&&x.password===p) set({user:{username:u,role:x.role}}); else alert('Invalid credentials')}, logout:()=>set({user:null})}))
