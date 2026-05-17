export function VideoPreview({url}:{url?:string}){return <div><h3>视频预览</h3>{url?<video src={url} controls/>:<p>生成后在此预览。</p>}</div>}
