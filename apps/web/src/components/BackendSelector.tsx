type Props={value:string;onChange:(v:string)=>void};
const backends=['mock','comfyui','diffusers_t2v','diffusers_i2v','external','wan','cogvideox','hunyuan','ltx'];
export function BackendSelector({value,onChange}:Props){return <div className="panel"><h3>生成后端</h3><select value={value} onChange={e=>onChange(e.target.value)}>{backends.map(b=><option key={b} value={b}>{b}</option>)}</select><p className="muted">默认 mock 可在无 GPU、无模型权重环境运行；真实模型需在后端配置后启用。</p></div>}
