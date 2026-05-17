"""Multi-shot storyboard planner."""
from app.models.schemas import VideoPromptSpec, Storyboard, StoryboardShot, GenerationJob
from app.skills.prompt_parser import build_generation_prompt

CAMERAS = ['wide establishing shot','medium shot','close-up','detail insert','slow push-in','reaction shot','final wide shot']
TRANSITIONS = ['cut','soft dissolve','match cut','cut','fade']

def plan_storyboard(spec: VideoPromptSpec, num_shots: int | None = None) -> Storyboard:
    """Split a video spec into 3-8 coherent shots."""
    n = num_shots or (3 if spec.duration <= 8 else 5)
    n = max(1, min(8, n))
    if n == 1:
        durations = [spec.duration]
    else:
        base = spec.duration / n; durations = [round(base,2)] * n; durations[-1] = round(spec.duration - sum(durations[:-1]),2)
    base_prompt = build_generation_prompt(spec)
    shots=[]
    for i in range(n):
        shots.append(StoryboardShot(shot_id=i+1, duration=durations[i], camera_angle=CAMERAS[i % len(CAMERAS)], camera_motion=spec.camera if i==0 else ['static','slow_push_in','pan_right','pull_back'][i%4], visual_prompt=f"Shot {i+1}: {base_prompt}", action_prompt=f"Continue the scene with controlled action and consistent subject; emphasize {spec.mood}.", transition=TRANSITIONS[i % len(TRANSITIONS)], audio_hint='low cinematic ambience', consistency_notes=f"Keep {spec.subject}, {spec.style}, {spec.lighting} consistent across shots."))
    sb = Storyboard(total_duration=sum(s.duration for s in shots), shots=shots)
    sb.markdown = storyboard_to_markdown(sb)
    return sb

def storyboard_to_markdown(storyboard: Storyboard) -> str:
    """Render storyboard as Markdown."""
    lines=[f"# {storyboard.title}", f"Total duration: {storyboard.total_duration:.1f}s"]
    for s in storyboard.shots:
        lines.append(f"\n## Shot {s.shot_id} · {s.duration:.1f}s\n- Camera: {s.camera_angle} / {s.camera_motion}\n- Visual: {s.visual_prompt}\n- Action: {s.action_prompt}\n- Transition: {s.transition}\n- Consistency: {s.consistency_notes}")
    return '\n'.join(lines)

def storyboard_to_generation_jobs(storyboard: Storyboard) -> list[GenerationJob]:
    """Convert storyboard shots into generation jobs."""
    return [GenerationJob(shot_id=s.shot_id, prompt=f"{s.visual_prompt}. {s.action_prompt}", duration=s.duration, camera_motion=s.camera_motion) for s in storyboard.shots]
