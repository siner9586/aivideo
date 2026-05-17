import {useEffect,useState} from 'react';
import {templateApi,type PromptTemplate} from '../lib/templateApi';

type Props={idea:string;onApply:(payload:any)=>void};
export function PromptTemplateLibrary({idea,onApply}:Props){const[items,setItems]=useState<PromptTemplate[]>([]);const[err,setErr]=useState('');useEffect(()=>{templateApi.list().then(setItems).catch((e:any)=>setErr(e.message))},[]);async function apply(id:string){try{onApply(await templateApi.apply(id,idea))}catch(e:any){setErr(e.message)}}return <div className="panel"><h3>Prompt 模板库</h3>{err&&<p className="error">{err}</p>}<div className="list">{items.map(t=><button key={t.template_id} className="listItem" onClick={()=>apply(t.template_id)}><b>{t.title}</b><span>{t.category}</span><small>{t.description}</small></button>)}</div></div>}
