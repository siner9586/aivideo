import {useState} from 'react';
import type {Project} from '../lib/projectApi';
import {composerApi,videoFileUrl} from '../lib/composerApi';

type Props={project:Project|null;onOutput?:(path:string)=>void};
export function ComposerPanel({project,onOutput}:Props){const[output,setOutput]=useState('');const[err,setErr]=useState('');async function compose(){if(!project)return;try{const r:any=await composerApi.compose(project.project_id,{title:project.title,ending_text:'Created with AI Video Studio'});setOutput(r.output_video_path);onOutput?.(r.output_video_path);setErr('')}catch(e:any){setErr(e.message)}}return <div className="panel"><h3>视频合成</h3>{!project&&<p className="muted">请选择项目。</p>}{project&&<><p className="muted">镜头数：{project.shots.length}</p><button className="btn" onClick={compose}>合成完整视频</button><a className="btn secondary linkBtn" href={composerApi.exportUrl(project.project_id)}>下载项目 ZIP</a></>}{err&&<p className="error">{err}</p>}{output&&<><p className="muted">输出：{output}</p><video controls src={videoFileUrl(output)} /></>}</div>}
