"""Camera motion parsing and mock transform mapping."""
from app.models.schemas import CameraMotionSpec

MOTION_MAP = {
    '缓慢推进':'slow_push_in','推进':'slow_push_in','push in':'slow_push_in','zoom in':'slow_push_in','拉远':'pull_back','pull back':'pull_back','zoom out':'pull_back',
    '左摇':'pan_left','pan left':'pan_left','右摇':'pan_right','pan right':'pan_right','上摇':'tilt_up','tilt up':'tilt_up','下摇':'tilt_down','tilt down':'tilt_down',
    '环绕':'orbit','orbit':'orbit','手持':'handheld','handheld':'handheld','航拍':'drone','drone':'drone','特写':'close_up','close up':'close_up','远景':'wide_shot','wide':'wide_shot'
}

def parse_camera_motion(text: str) -> CameraMotionSpec:
    """Map natural language camera words into a structured spec."""
    t = (text or '').lower()
    for key, val in MOTION_MAP.items():
        if key.lower() in t:
            return CameraMotionSpec(motion_type=val, intensity=0.45, direction=val)
    return CameraMotionSpec(motion_type='static', intensity=0.1)

def camera_motion_to_prompt(spec: CameraMotionSpec) -> str:
    """Convert camera motion spec to generation prompt text."""
    return f"camera motion: {spec.motion_type}, smooth cinematic movement, intensity {spec.intensity:.2f}"

def camera_motion_to_transform_params(spec: CameraMotionSpec) -> dict:
    """Return OpenCV transform parameters for the mock backend."""
    return {'motion_type': spec.motion_type, 'intensity': spec.intensity, 'dx': 28 if 'right' in spec.motion_type else -28 if 'left' in spec.motion_type else 0, 'dy': -20 if 'up' in spec.motion_type else 20 if 'down' in spec.motion_type else 0, 'zoom_delta': 0.08 if spec.motion_type in {'slow_push_in','close_up'} else -0.06 if spec.motion_type=='pull_back' else 0.0}
