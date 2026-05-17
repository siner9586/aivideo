"""Keyframe validation and mock interpolation."""
from pathlib import Path
import cv2
from app.models.schemas import KeyframeValidationReport, KeyframeSpec
from app.utils.image_utils import image_info, is_allowed_image

def validate_keyframes(paths: list[str]) -> KeyframeValidationReport:
    """Validate keyframe file existence, format and dimensions."""
    files=[]; warnings=[]; valid=True
    for p in paths:
        if not p: continue
        if not Path(p).exists() or not is_allowed_image(p): valid=False; warnings.append(f'invalid keyframe: {p}'); continue
        files.append(image_info(p))
    return KeyframeValidationReport(valid=valid, warnings=warnings, files=files)

def build_keyframe_conditioning(first_frame, last_frame, references) -> KeyframeSpec:
    """Build conditioning spec for I2V backends."""
    paths=[x for x in [first_frame,last_frame,*references] if x]; report=validate_keyframes(paths)
    if not report.valid: raise ValueError('; '.join(report.warnings))
    return KeyframeSpec(first_frame=first_frame, last_frame=last_frame, references=references or [])

def interpolate_keyframes_mock(first_frame, last_frame, output_path, duration, fps) -> str:
    """Create a linear blend transition between first and last frames."""
    a=cv2.imread(first_frame); b=cv2.imread(last_frame)
    if a is None or b is None: raise ValueError('invalid keyframe')
    h,w=a.shape[:2]; b=cv2.resize(b,(w,h)); writer=cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w,h))
    total=int(duration*fps)
    for i in range(total):
        t=i/max(total-1,1); writer.write(cv2.addWeighted(a,1-t,b,t,0))
    writer.release(); return output_path
