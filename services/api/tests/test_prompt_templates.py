from app.skills.prompt_templates import list_templates, apply_template


def test_prompt_templates_load_and_apply():
    templates = list_templates()
    assert len(templates) >= 5
    payload = apply_template(templates[0].template_id, 'tea house demo')
    assert 'tea house demo' in payload['prompt']
    assert payload['settings']['duration'] > 0
