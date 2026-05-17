"""Safety guard for prompts, characters and generation requests."""
from __future__ import annotations
from typing import Any
from app.models.schemas import SafetyReport, CharacterProfile

BLOCK = ['色情深伪','未授权换脸','non-consensual','porn deepfake','child sexual','恐怖主义','terrorist']
HIGH = ['冒充','impersonate','诈骗','fraud','政治误导','medical cure','guaranteed return','明星脸','celebrity clone','版权角色','disney','marvel']
VIOLENCE = ['血腥','gore','extreme violence']

def check_prompt_safety(prompt: str) -> SafetyReport:
    """Check prompt with simple policy keyword rules."""
    t=(prompt or '').lower(); reasons=[]
    if any(k.lower() in t for k in BLOCK):
        return SafetyReport(risk_level='blocked', allowed=False, reasons=['blocked non-consensual sexual/deepfake or extremist content'], safe_alternative=rewrite_to_safe_prompt(prompt))
    if any(k.lower() in t for k in HIGH+VIOLENCE):
        reasons.append('high-risk impersonation, misleading, copyright, medical/financial or violent content')
        return SafetyReport(risk_level='high', allowed=True, reasons=reasons, safe_alternative=rewrite_to_safe_prompt(prompt))
    return SafetyReport(risk_level='low', allowed=True)

def check_character_safety(profile: CharacterProfile) -> SafetyReport:
    """Check role card safety. Does not allow unauthorized face cloning."""
    text=' '.join(str(v or '') for v in profile.model_dump().values())
    report=check_prompt_safety(text)
    if profile.reference_image_path and any(k in text.lower() for k in ['celebrity','明星','公众人物']):
        return SafetyReport(risk_level='blocked', allowed=False, reasons=['public figure cloning is blocked'])
    return report

def check_generation_request(request: Any) -> SafetyReport:
    """Check a generation request object."""
    return check_prompt_safety(getattr(request, 'prompt', str(request)))

def rewrite_to_safe_prompt(prompt: str) -> str:
    """Rewrite prompt toward safe fictional and authorized content."""
    return 'Create an original fictional, consent-based, non-deceptive video concept with no real-person impersonation, explicit sexual deepfake, misleading claims, or copyrighted character replication.'
