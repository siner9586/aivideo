export type Backend = 'mock'|'diffusers'|'external'|'comfyui';
export interface GenerateRequest { prompt:string; backend:Backend; duration:number; fps:number; seed?:number; negative_prompt?:string; aspect_ratio:string; resolution:string; camera_motion?:string; }
