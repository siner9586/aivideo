"""Character profile management without face cloning."""
from app.models.schemas import CharacterProfile, SafetyReport
from app.skills.safety_guard import check_character_safety as _check

def create_character_profile(data) -> CharacterProfile:
    """Create and validate a character profile."""
    profile=CharacterProfile(**data); report=validate_character_safety(profile)
    if not report.allowed: raise ValueError('; '.join(report.reasons))
    return profile

def apply_character_to_prompt(prompt: str, character_profile: CharacterProfile) -> str:
    """Inject a fictional role card into the prompt."""
    attrs=[character_profile.visual_anchor_prompt, character_profile.hair, character_profile.clothing, character_profile.personality]
    desc=', '.join([a for a in attrs if a])
    return f"{prompt}\nCharacter consistency card: {character_profile.name}; {desc}. Do not clone or impersonate any real person."

def validate_character_safety(profile: CharacterProfile) -> SafetyReport:
    """Validate profile safety."""
    return _check(profile)
