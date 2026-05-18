import {useMemo,useState} from 'react';
import {queueApi} from '../lib/queueApi';
import {projectApi,type Project} from '../lib/projectApi';
import {shortDramaApi,type ShortDramaPlan} from '../lib/shortDramaApi';

type Props={project:Project|null;onProject:(p:Project)=>void};

const GENRES=[
  ['revenge','逆袭/复仇'],['rebirth','重生'],['urban_romance','都市情感'],['xianxia','修仙'],
  ['business','商战'],['family','家庭伦理'],['suspense','悬疑'],['comedy','喜剧反套路']
];
const VIDEO_BACKENDS=['mock','local_open_video','ltx','wan','cogvideox','hunyuan','comfyui','diffusers_t2v','external'];

export function ShortDramaWorkspace({project,onProject}:Props){
  const[premise,setPremise]=useState('被背叛的女主重回宴会现场，当众夺回公司控制权。');
  const[genre,setGenre]=useState('revenge');
  const[visualMode,setVisualMode]=useState<'ai_manhua'|'cinematic_realistic'|'hybrid_live_action'>('cinematic_realistic');
  const[episodes,setEpisodes]=useState(3);
  const[shotsPerEpisode,setShotsPerEpisode]=useState(6);
  const[secondsPerEpisode,setSecondsPerEpisode]=useState(60);
  const[useGpt,setUseGpt]=useState(false);
  const[backend,setBackend]=useState('local_open_video');
  const[plan,setPlan]=useState<ShortDramaPlan|null>(null);
  const[score,setScore]=useState<any>(null);
  const[assetPack,setAssetPack]=useState<any>(null);
  const[subtitleDraft,setSubtitleDraft]=useState('');
  const[dubbingDraft,setDubbingDraft]=useState<any>(null);
  const[busy,setBusy]=useState(false);
  const[err,setErr]=useState('');
  const[submitted,setSubmitted]=useState(0);

  const firstHook=useMemo(()=>{const ep:any=plan?.episodes?.[0];return ep?.hook || ep?.beat || '';},[plan]);
  const firstCliff=useMemo(()=>{const ep:any=plan?.episodes?.[0];return ep?.cliffhanger || '';},[plan]);

  async function createPlan(){
    setBusy(true);setErr('');setAssetPack(null);setSubtitleDraft('');setDubbingDraft(null);
    try{
      const data=await shortDramaApi.plan({premise,genre,visual_mode:visualMode,platform:'hongguo',episodes,shots_per_episode:shotsPerEpisode,seconds_per_episode:secondsPerEpisode,use_gpt:useGpt,fallback_to_local:true});
      setPlan(data);
      const ep:any=data.episodes?.[0];
      const s=await shortDramaApi.viralScore({hook_text:ep?.hook||ep?.beat||premise,cliffhanger_text:ep?.cliffhanger||'真相即将揭露前突然切断。',conflict_level:5,reversal_count:2,closeup_ratio:.45,subtitle_density:.65});
      setScore(s);
    }catch(e:any){setErr(e.message)}finally{setBusy(false)}
  }

  async function createProjectFromPlan(){
    if(!plan){setErr('请先生成短剧方案');return}
    setBusy(true);setErr('');
    try{
      const p=await projectApi.create({title:plan.title||'AI短剧项目',description:'Created from ShortDramaWorkspace',original_prompt:premise,storyboard:plan,generation_settings:{backend,duration:secondsPerEpisode,fps:16,aspect_ratio:'9:16',resolution:'720p',visual_mode:visualMode}} as any);
      onProject(p);
    }catch(e:any){setErr(e.message)}finally{setBusy(false)}
  }

  async function writeShotsToProject(){
    if(!project){setErr('请先创建或选择项目');return}
    if(!plan?.episodes?.length){setErr('请先生成短剧方案');return}
    setBusy(true);setErr('');
    try{
      let current:Project={...project,shots:[...project.shots]};
      for(const ep of plan.episodes as any[]){
        const shots=ep?.storyboard?.shots || ep?.shots || [];
        for(const shot of shots){
          const created=await projectApi.addShot(project.project_id,{title:`EP${ep.episode_id||1} Shot ${shot.shot_id}`,duration:shot.duration || Math.round(secondsPerEpisode/shotsPerEpisode),visual_prompt:shot.visual_prompt || shot.prompt || '',action_prompt:shot.action_prompt || shot.subtitle || '',camera_motion:shot.camera_motion || 'slow_push_in',backend,metadata:{episode_id:ep.episode_id,transition:shot.transition,audio_hint:shot.audio_hint||shot.dubbing_hint}});
          current={...current,shots:[...current.shots,created]};
        }
      }
      onProject(current);
    }catch(e:any){setErr(e.message)}finally{setBusy(false)}
  }

  async function submitBatchJobs(){
    if(!plan?.generation_jobs?.length){setErr('请先生成短剧方案');return}
    setBusy(true);setErr('');setSubmitted(0);
    try{
      let count=0;
      for(const job of plan.generation_jobs){
        await queueApi.submit({project_id:project?.project_id,shot_id:job.shot_id?String(job.shot_id):undefined,backend,input_prompt:job.prompt,input_assets:[],metadata:{source:'short_drama_workspace',duration:job.duration,camera_motion:job.camera_motion,aspect_ratio:'9:16',resolution:'720p',quality_preset:'short_drama'}});
        count+=1;setSubmitted(count);
      }
    }catch(e:any){setErr(e.message)}finally{setBusy(false)}
  }

  async function createMediaDrafts(){
    if(!plan){setErr('请先生成短剧方案');return}
    setBusy(true);setErr('');
    try{
      const [assets,subs,dubbing]=await Promise.all([
        shortDramaApi.characterAssets(plan,project?.project_id),
        shortDramaApi.subtitles(plan),
        shortDramaApi.dubbingScript(plan),
      ]);
      setAssetPack(assets);setSubtitleDraft(subs.content||'');setDubbingDraft(dubbing);
    }catch(e:any){setErr(e.message)}finally{setBusy(false)}
  }

  return <div className="card shortDrama"><div className="toolbar"><div><h2>AI短剧工作台</h2><p className="muted">红果/抖音式：题材模板 → 爽点钩子 → 分集分镜 → 角色一致性 → 本地开源视频模型</p></div><span className="pill">9:16 · {backend}</span></div>
    <label>短剧创意 / 小说片段</label><textarea value={premise} onChange={e=>setPremise(e.target.value)} />
    <div className="row four"><div><label>题材</label><select value={genre} onChange={e=>setGenre(e.target.value)}>{GENRES.map(([v,l])=><option key={v} value={v}>{l}</option>)}</select></div><div><label>视觉模式</label><select value={visualMode} onChange={e=>setVisualMode(e.target.value as any)}><option value="cinematic_realistic">拟真人电影感</option><option value="ai_manhua">AI漫剧</option><option value="hybrid_live_action">真人+AI混合</option></select></div><div><label>集数</label><input type="number" min={1} max={24} value={episodes} onChange={e=>setEpisodes(Number(e.target.value))}/></div><div><label>每集镜头</label><input type="number" min={4} max={10} value={shotsPerEpisode} onChange={e=>setShotsPerEpisode(Number(e.target.value))}/></div></div>
    <div className="row four"><div><label>每集秒数</label><input type="number" min={12} max={180} value={secondsPerEpisode} onChange={e=>setSecondsPerEpisode(Number(e.target.value))}/></div><div><label>生成后端</label><select value={backend} onChange={e=>setBackend(e.target.value)}>{VIDEO_BACKENDS.map(b=><option key={b} value={b}>{b}</option>)}</select></div><div className="check"><label><input type="checkbox" checked={useGpt} onChange={e=>setUseGpt(e.target.checked)}/> 使用 GPT 增强</label><small>可选；视频生成不依赖收费模型</small></div><div><label>当前项目</label><p className="muted">{project?.title||'未选择'}</p></div></div>
    <div className="actions"><button className="btn" onClick={createPlan} disabled={busy}>{busy?'处理中...':'生成短剧方案'}</button><button className="btn secondary" onClick={createProjectFromPlan} disabled={!plan||busy}>创建项目</button><button className="btn secondary" onClick={writeShotsToProject} disabled={!plan||!project||busy}>写入时间线</button><button className="btn secondary" onClick={createMediaDrafts} disabled={!plan||busy}>生成角色/字幕/配音草稿</button><button className="btn secondary" onClick={submitBatchJobs} disabled={!plan||busy}>批量提交队列</button></div>
    {err&&<p className="error">{err}</p>}{submitted>0&&<p className="muted">已提交 {submitted} 个镜头任务。</p>}
    {plan&&<div className="dramaResult"><div className="toolbar"><h3>{plan.title||'短剧方案'}</h3><span className="pill">{plan.provider||'local'}{plan.model?` · ${plan.model}`:''}</span></div>{plan.gpt_warning&&<p className="error">GPT未启用，已回退本地规划：{plan.gpt_warning}</p>}{score&&<div className="scoreBox"><b>爆款启发式评分：{score.viral_score}</b><small>{score.notes?.join(' ')||'结构完整，可进入分镜生成。'}</small></div>}<div className="characterGrid">{(plan.characters||[]).map((c:any,i:number)=><div className="miniCard" key={i}><b>{c.name}</b><p>{c.role}</p><small>{c.visual_anchor||c.continuity_rule}</small></div>)}</div>{assetPack&&<pre className="json">{JSON.stringify(assetPack,null,2)}</pre>}{subtitleDraft&&<pre className="json">{subtitleDraft}</pre>}{dubbingDraft&&<pre className="json">{JSON.stringify(dubbingDraft,null,2)}</pre>}<pre className="json">{plan.markdown || JSON.stringify(plan.episodes,null,2)}</pre></div>}
  </div>
}
