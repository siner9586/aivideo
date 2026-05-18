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
import{ShortDramaWorkspace}from'./components/ShortDramaWorkspace';

export default function App(){
  const[prompt,setPrompt]=useState('Create an 8-second cinematic realistic video in a traditional tea house with warm light and slow push-in camera.');
  const[settings,setSettings]=useState<any>({backend:'mock',duration:8,fps:12,aspect_ratio:'16:9',resolution:'480p',camera_motion:'slow_push_in',negative_prompt:'low quality, flicker, shake, watermark'});
  const[parsed,setParsed]=useState<any>();const[story,setStory]=useState<any>();const[task,setTask]=useState<any>();const[project,setProject]=useState<Project|null>(null);const[busy,setBusy]=useState(false);const[err,setErr]=useState('');const[finalVideo,setFinalVideo]=useState('');
  async function runParse(){try{const p=await parsePrompt(prompt);const s=await storyboard(prompt);setParsed(p);setStory(s);if(project){const updated=await projectApi.update(project.project_id,{original_prompt:prompt,parsed_spec:p,storyboard:s,generation_settings:settings});setProject(updated)}return s}catch(e:any){setErr(e.message);return undefined}}
  async function runGen(){setBusy(true);setErr('');try{await runParse();const res=await generateText({prompt,...settings});setTask(res)}catch(e:any){setErr(e.message)}finally{setBusy(false)}}
  async function makeShotsFromStory(){if(!project){setErr('Create or select a project first');return}const sourceStory=story?.shots?.length?story:await runParse();const source=(sourceStory?.shots||[]);if(!source.length){setErr('No storyboard shots yet');return}let current=project;for(const shot of source){const created=await projectApi.addShot(project.project_id,{title:`Shot ${shot.shot_id}`,duration:shot.duration,visual_prompt:shot.visual_prompt,action_prompt:shot.action_prompt,camera_motion:shot.camera_motion,backend:settings.backend});current={...current,shots:[...current.shots,created]}}setProject(current)}
  return <div className="app beta"><header className="header"><div><h1>AI Video Studio Beta</h1><p>Prompt to storyboard to timeline to queue to final video, with Short Drama Studio.</p></div><div className="status">Backend: {settings.backend}</div></header>
    <main className="workspace"><aside className="leftRail"><ProjectSidebar current={project} onSelect={setProject} onCreate={setProject}/><PromptTemplateLibrary idea={prompt} onApply={(x:any)=>{setPrompt(x.prompt);setSettings({...settings,...x.settings,negative_prompt:x.negative_prompt})}}/><AssetLibrary/></aside>
    <section className="centerRail"><ShortDramaWorkspace project={project} onProject={setProject}/><div className="card"><h2>General Video Input</h2><PromptEditor prompt={prompt} setPrompt={setPrompt}/><GenerationSettings settings={settings} setSettings={setSettings}/><BackendSelector value={settings.backend} onChange={v=>setSettings({...settings,backend:v})}/><div className="actions"><button className="btn secondary" onClick={runParse}>Parse and storyboard</button><button className="btn secondary" onClick={makeShotsFromStory}>Write to timeline</button><button className="btn" onClick={runGen}>{busy?'Generating...':'Quick mock demo'}</button></div>{err&&<p className="error">{err}</p>}</div><StoryboardPanel parsed={parsed} story={story}/><TimelineEditor project={project} onProject={setProject}/></section>
    <aside className="rightRail"><QueuePanel/><div className="panel"><h3>Preview</h3><VideoPreview url={task?.task_id?videoUrl(task.task_id):undefined}/>{task?.result?.output_path&&<p className="muted">{task.result.output_path}</p>}</div><ComposerPanel project={project} onOutput={setFinalVideo}/><QualityPanel videoPath={task?.result?.output_path||finalVideo} projectId={project?.project_id}/></aside></main><SafetyNotice/><footer className="notice">Current project: {project?.project_id||'none'} · outputs: data/projects and data/outputs · mock backend runs without GPU.</footer></div>
}
