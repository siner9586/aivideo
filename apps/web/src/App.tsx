import React,{useState}from'react';
import{parsePrompt,storyboard,generateText,videoUrl}from'./lib/api';
import{projectApi,type Project}from'./lib/projectApi';
import'./styles/app.css';
import{PromptEditor}from'./components/PromptEditor';
import{GenerationSettings}from'./components/GenerationSettings';
import{StoryboardPanel}from'./components/StoryboardPanel';
import{VideoPreview}from'./components/VideoPreview';
import{SafetyNotice}from'./components/SafetyNotice';
import{ProjectSidebar}from'./components/ProjectSidebar';
import{PromptTemplateLibrary}from'./components/PromptTemplateLibrary';
import{TimelineEditor}from'./components/TimelineEditor';
import{QueuePanel}from'./components/QueuePanel';
import{ComposerPanel}from'./components/ComposerPanel';
import{QualityPanel}from'./components/QualityPanel';
import{AssetLibrary}from'./components/AssetLibrary';
import{BackendSelector}from'./components/BackendSelector';

export default function App(){
  const[prompt,setPrompt]=useState('生成一段 8 秒电影级写实风格视频：夜晚的中国传统茶楼，暖金色光线，镜头缓慢推进，人物围坐茶案低声交谈，画面高级、稳定、细节丰富。');
  const[settings,setSettings]=useState<any>({backend:'mock',duration:8,fps:12,aspect_ratio:'16:9',resolution:'480p',camera_motion:'slow_push_in',negative_prompt:'低清晰度、闪烁、抖动、水印'});
  const[parsed,setParsed]=useState<any>();const[story,setStory]=useState<any>();const[task,setTask]=useState<any>();const[project,setProject]=useState<Project|null>(null);const[busy,setBusy]=useState(false);const[err,setErr]=useState('');const[finalVideo,setFinalVideo]=useState('');
  async function runParse(){try{const p=await parsePrompt(prompt);const s=await storyboard(prompt);setParsed(p);setStory(s);if(project){const updated=await projectApi.update(project.project_id,{original_prompt:prompt,parsed_spec:p,storyboard:s,generation_settings:settings});setProject(updated)}}catch(e:any){setErr(e.message)}}
  async function runGen(){setBusy(true);setErr('');try{await runParse();const res=await generateText({prompt,...settings});setTask(res)}catch(e:any){setErr(e.message)}finally{setBusy(false)}}
  async function makeShotsFromStory(){if(!project){setErr('请先创建或选择项目');return}if(!story?.shots?.length){await runParse()}const source=(story?.shots||[]);let current=project;for(const shot of source){const created=await projectApi.addShot(project.project_id,{title:`Shot ${shot.shot_id}`,duration:shot.duration,visual_prompt:shot.visual_prompt,action_prompt:shot.action_prompt,camera_motion:shot.camera_motion,backend:settings.backend});current={...current,shots:[...current.shots,created]}}setProject(current)}
  return <div className="app beta"><header className="header"><div><h1>AI Video Studio Beta</h1><p>Prompt → 分镜 → 镜头编辑 → 队列生成 → 合成导出</p></div><div className="status">后端：{settings.backend} · API: configurable</div></header>
    <main className="workspace"><aside className="leftRail"><ProjectSidebar current={project} onSelect={setProject} onCreate={setProject}/><PromptTemplateLibrary idea={prompt} onApply={(x:any)=>{setPrompt(x.prompt);setSettings({...settings,...x.settings,negative_prompt:x.negative_prompt})}}/><AssetLibrary/></aside>
    <section className="centerRail"><div className="card"><h2>创作输入</h2><PromptEditor prompt={prompt} setPrompt={setPrompt}/><GenerationSettings settings={settings} setSettings={setSettings}/><BackendSelector value={settings.backend} onChange={v=>setSettings({...settings,backend:v})}/><div className="actions"><button className="btn secondary" onClick={runParse}>解析与生成分镜</button><button className="btn secondary" onClick={makeShotsFromStory}>写入项目时间线</button><button className="btn" onClick={runGen}>{busy?'生成中...':'快速生成 Mock Demo'}</button></div>{err&&<p className="error">{err}</p>}</div><StoryboardPanel parsed={parsed} story={story}/><TimelineEditor project={project} onProject={setProject}/></section>
    <aside className="rightRail"><QueuePanel/><div className="panel"><h3>快速预览</h3><VideoPreview url={task?.task_id?videoUrl(task.task_id):undefined}/>{task?.result?.output_path&&<p className="muted">{task.result.output_path}</p>}</div><ComposerPanel project={project} onOutput={setFinalVideo}/><QualityPanel videoPath={task?.result?.output_path||finalVideo} projectId={project?.project_id}/></aside></main><SafetyNotice/><footer className="notice">当前项目：{project?.project_id||'未选择'} · 输出目录：data/projects 与 data/outputs · 真实模型默认关闭，mock backend 可无 GPU 运行。</footer></div>
}
