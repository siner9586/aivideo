import type { GenerateRequest } from './types';
const API = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_BASE || 'http://localhost:8000';
export async function parsePrompt(prompt:string){ const r=await fetch(`${API}/api/parse`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({prompt})}); return r.json(); }
export async function storyboard(prompt:string){ const r=await fetch(`${API}/api/storyboard`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({prompt,num_shots:3})}); return r.json(); }
export async function generateText(req:GenerateRequest){ const r=await fetch(`${API}/api/generate/text-to-video`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(req)}); return r.json(); }
export function videoUrl(taskId:string){ return `${API}/api/assets/${taskId}/video`; }
export async function postprocess(taskId:string, subtitle:string){ const r=await fetch(`${API}/api/postprocess/${taskId}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({subtitle, aspect_ratio:'16:9'})}); return r.json(); }
