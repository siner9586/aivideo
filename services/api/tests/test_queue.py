from app.queue.job_queue import JobQueue
from app.queue.task_store import TaskStore


def test_queue_submit_query_retry_cancel(tmp_path):
    store = TaskStore(tmp_path / 'tasks.jsonl')
    q = JobQueue(store)
    task = q.submit_task('p1', 's1', 'mock', 'demo prompt', [], {'duration': 1})
    assert task.status == 'pending'
    assert q.get_task(task.task_id).input_prompt == 'demo prompt'
    store.update_task(task.task_id, status='failed', error_message='boom')
    retried = q.retry_task(task.task_id)
    assert retried.status == 'pending'
    cancelled = q.cancel_task(task.task_id)
    assert cancelled.status == 'cancelled'
