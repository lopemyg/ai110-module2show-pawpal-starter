"""Initial checks for task completion and adding a task to a pet."""

from pawpal_system import Pet, Task


def test_mark_complete_changes_status():
    """mark_complete() sets the task's completed flag."""
    task = Task(
        description="Morning walk",
        time="08:00",
        frequency="daily",
        duration_minutes=20,
        priority="high",
        category="walk",
    )

    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    """Adding a task increases the number of tasks stored on the pet."""
    pet = Pet(name="Mochi", species="cat")
    task = Task(
        description="Breakfast",
        time="07:30",
        frequency="daily",
        duration_minutes=10,
        priority="high",
        category="feeding",
    )

    assert len(pet.get_tasks()) == 0
    pet.add_task(task)
    assert len(pet.get_tasks()) == 1
