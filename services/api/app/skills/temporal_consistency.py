"""Basic temporal consistency analysis and smoothing."""
import cv2, numpy as np
from app.models.schemas import TemporalConsistencyReport
from app.utils.video_utils import read_frames

def compute_frame_difference_metrics(frames) -> dict:
    """Compute frame difference statistics."""
    if len(frames)<2: return {'avg_frame_diff':0.0,'max_frame_diff':0.0,'std_frame_diff':0.0}
    diffs=[]
    prev=cv2.cvtColor(frames[0], cv2.COLOR_BGR2GRAY)
    for f in frames[1:]:
        cur=cv2.cvtColor(f, cv2.COLOR_BGR2GRAY); diffs.append(float(np.mean(cv2.absdiff(prev,cur)))/255.0); prev=cur
    return {'avg_frame_diff':float(np.mean(diffs)), 'max_frame_diff':float(np.max(diffs)), 'std_frame_diff':float(np.std(diffs))}

def analyze_temporal_consistency(video_path: str) -> TemporalConsistencyReport:
    """Analyze flicker and motion smoothness from frame differences."""
    frames=read_frames(video_path); m=compute_frame_difference_metrics(frames)
    flicker=min(1.0, m['std_frame_diff']*8); smooth=max(0.0,1.0-m['max_frame_diff']*2); consistency=max(0.0,(smooth+(1-flicker))/2)
    warnings=[]
    if m['max_frame_diff']>0.45: warnings.append('large frame jump detected')
    if flicker>0.5: warnings.append('possible flicker')
    return TemporalConsistencyReport(avg_frame_diff=m['avg_frame_diff'], max_frame_diff=m['max_frame_diff'], flicker_score=flicker, motion_smoothness_score=smooth, consistency_score=consistency, warnings=warnings)

def smooth_video_basic(input_path: str, output_path: str) -> str:
    """Apply simple temporal blending smoothing."""
    cap=cv2.VideoCapture(input_path); fps=cap.get(cv2.CAP_PROP_FPS) or 12; w=int(cap.get(3)); h=int(cap.get(4)); writer=cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w,h)); prev=None
    while True:
        ok, frame=cap.read()
        if not ok: break
        out=frame if prev is None else cv2.addWeighted(frame,0.75,prev,0.25,0); writer.write(out); prev=out
    cap.release(); writer.release(); return output_path
