const API = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_BASE || 'http://localhost:8000';

async function json<T>(path:string, init?:RequestInit):Promise<T>{
  const r=await fetch(`${API}${path}`,{headers:{'Content-Type':'application/json',...(init?.headers||{})},...init});
  if(!r.ok) throw new Error(await r.text());
  return r.json();
}

export type ShortDramaPlanRequest={
  premise:string;
  genre:string;
  visual_mode:'ai_manhua'|'cinematic_realistic'|'hybrid_live_action';
  platform:string;
  episodes:number;
  shots_per_episode:number;
  seconds_per_episode?:number;
  use_gpt?:boolean;
  fallback_to_local?:boolean;
};

export type ShortDramaGenerationJob={
  shot_id?:number;
  prompt:string;
  duration:number;
  camera_motion:string;
};

export type ShortDramaPlan={
  title?:string;
  provider?:string;
  model?:string;
  gpt_warning?:string;
  genre?:string;
  visual_mode?:string;
  premise?:string;
  platform_profile?:Record<string,any>;
  characters?:any[];
  episodes?:any[];
  generation_jobs?:ShortDramaGenerationJob[];
  negative_prompt?:string;
  production_notes?:string[];
  markdown?:string;
};

export const shortDramaApi={
  genres:()=>json<any>('/api/short-drama/genres'),
  plan:(payload:ShortDramaPlanRequest)=>json<ShortDramaPlan>('/api/short-drama/plan',{method:'POST',body:JSON.stringify(payload)}),
  viralScore:(payload:any)=>json<any>('/api/short-drama/viral-score',{method:'POST',body:JSON.stringify(payload)}),
  platformProfile:(platform:string)=>json<any>(`/api/short-drama/platform-profile/${platform}`),
};
