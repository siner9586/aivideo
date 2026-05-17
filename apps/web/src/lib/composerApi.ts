const API = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_BASE || 'http://localhost:8000';
async function json<T>(path:string, init?:RequestInit):Promise<T>{ const r=await fetch(`${API}${path}`,{headers:{'Content-Type':'application/json',...(init?.headers||{})},...init}); if(!r.ok) throw new Error(await r.text()); return r.json(); }
export const composerApi={compose:(projectId:string,settings:any)=>json(`/api/composer/${projectId}/compose`,{method:'POST',body:JSON.stringify(settings)}),exportUrl:(projectId:string)=>`${API}/api/composer/${projectId}/export`};
export function videoFileUrl(path?:string){ if(!path) return undefined; const name=path.split('/').pop()?.replace('.mp4','') || ''; return `${API}/api/assets/${name}/video`; }
