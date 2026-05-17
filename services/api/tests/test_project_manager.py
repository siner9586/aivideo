from app.projects.project_manager import ProjectManager


def test_project_manager_create_add_save_export(tmp_path):
    manager = ProjectManager(tmp_path / 'projects')
    project = manager.create_project({'title': 'Demo', 'original_prompt': 'tea house'})
    assert project.project_id
    shot = manager.add_shot(project.project_id, {'title': 'Opening', 'visual_prompt': 'warm tea house', 'duration': 2})
    assert shot.title == 'Opening'
    saved = manager.get_project(project.project_id)
    assert saved and len(saved.shots) == 1
    archive = manager.export_project(project.project_id)
    assert archive.endswith('.zip')
