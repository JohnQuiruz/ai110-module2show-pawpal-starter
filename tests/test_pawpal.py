from pawpal_system import CareTask, Pet


def test_mark_complete_changes_status():
    task = CareTask(title="Feed", duration_minutes=5, priority="high")
    assert task.status == "pending"
    task.mark_complete()
    assert task.status == "complete"


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Buddy", species="dog")
    assert len(pet.tasks) == 0
    task = CareTask(title="Walk", duration_minutes=30, priority="medium")
    pet.add_task(task)
    assert len(pet.tasks) == 1
