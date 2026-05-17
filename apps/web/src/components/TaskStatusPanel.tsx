export function TaskStatusPanel({task}:{task:any}){return <div><h3>任务状态</h3><pre className="json">{JSON.stringify(task,null,2)}</pre></div>}
