"""Safe prompt template library for AI video production."""
from __future__ import annotations
from pydantic import BaseModel

class PromptTemplate(BaseModel):
    template_id: str
    category: str
    title: str
    description: str
    base_prompt: str
    negative_prompt: str = 'low quality, flicker, watermark, distorted image, overexposure'
    suggested_duration: float = 8
    suggested_aspect_ratio: str = '16:9'
    suggested_camera_motion: str = 'slow_push_in'
    suggested_style: str = 'cinematic realistic'
    safety_notes: str = 'Use original subjects, authorized assets and non-deceptive claims.'

TEMPLATES: list[PromptTemplate] = [
    PromptTemplate(template_id='cinematic_realistic', category='cinematic', title='Cinematic realistic short', description='Story, real space and atmosphere.', base_prompt='Create a cinematic realistic video about: {idea}. Use stable camera, rich detail, natural light and restrained pacing.'),
    PromptTemplate(template_id='product_ad', category='product', title='Premium product ad', description='Clean commercial product reveal.', base_prompt='Create a premium product video about: {idea}. Use a minimal studio background, material close-ups, soft rim light and smooth orbit camera.', suggested_camera_motion='orbit'),
    PromptTemplate(template_id='education_science', category='education', title='Education explainer', description='Course, science and project explanation.', base_prompt='Create a clear educational explainer video about: {idea}. Use layered 3D visualization, clean labels and smooth motion.'),
    PromptTemplate(template_id='chinese_tea_house', category='chinese_style', title='Traditional tea house', description='Warm classical interior scene.', base_prompt='Create an original Chinese classical tea house scene about: {idea}. Use warm lantern light, carved wood, tea steam and slow push-in camera.'),
    PromptTemplate(template_id='tech_promo', category='technology', title='Technology promo', description='AI, SaaS and platform presentation.', base_prompt='Create a professional technology promo about: {idea}. Use abstract data flow, clean interface layers, 3D grid and controlled camera movement.'),
    PromptTemplate(template_id='city_drone', category='city', title='City aerial opening', description='City and park overview.', base_prompt='Create a city aerial opening about: {idea}. Use sunrise or dusk light, high angle view, slow push-in and clear building lines.', suggested_camera_motion='drone_push_in'),
    PromptTemplate(template_id='interview', category='interview', title='Interview mood', description='Documentary and knowledge sharing.', base_prompt='Create an original interview-style video about: {idea}. Use soft side light, realistic room background and natural gestures.'),
    PromptTemplate(template_id='commerce', category='commerce', title='Commerce product demo', description='Product feature short video.', base_prompt='Create a product demo video about: {idea}. Show opening, details, usage scenario and visualized benefits without exaggerated claims.'),
    PromptTemplate(template_id='paper_project_viz', category='academic', title='Academic project visualization', description='Paper, mechanism and roadmap visualization.', base_prompt='Create an academic project visualization video about: {idea}. Use white background, clear nodes, restrained arrows and layered structure.'),
    PromptTemplate(template_id='wechat_space', category='mini_program_space', title='Mobile space showcase', description='3D space card, store or exhibition view.', base_prompt='Create a mobile-friendly space showcase about: {idea}. Use realistic walkthrough, clear navigation path and highlighted points of interest.', suggested_aspect_ratio='9:16'),
]

def list_templates(category: str | None = None) -> list[PromptTemplate]:
    return [t for t in TEMPLATES if not category or t.category == category]

def get_template(template_id: str) -> PromptTemplate:
    for t in TEMPLATES:
        if t.template_id == template_id:
            return t
    raise KeyError(f'template not found: {template_id}')

def apply_template(template_id: str, idea: str, extra: str = '') -> dict:
    t = get_template(template_id)
    prompt = t.base_prompt.replace('{idea}', idea.strip() or 'an original safe video idea')
    if extra:
        prompt = f'{prompt}\nExtra requirements: {extra}'
    return {'template': t.model_dump(), 'prompt': prompt, 'negative_prompt': t.negative_prompt, 'settings': {'duration': t.suggested_duration, 'aspect_ratio': t.suggested_aspect_ratio, 'camera_motion': t.suggested_camera_motion, 'style': t.suggested_style}}
