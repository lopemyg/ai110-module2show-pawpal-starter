"""Checks for tasks, sorting, recurrence, conflicts, and an empty pet."""

from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


def make_task(
    description: str,
    time: str,
    frequency: str = "daily",
    duration_minutes: int = 10,
    priority: str = "medium",
    category: str = "other",
    pet_name: str = "",
) -> Task:
    """Build a task without repeating every field in each test."""
    return Task(
        description=description,
        time=time,
        frequency=frequency,
        duration_minutes=duration_minutes,
        priority=priority,
        category=category,
        pet_name=pet_name,
    )


def test_mark_complete_changes_status():
    """mark_complete() sets the task's completed flag."""
    task = make_task("Morning walk", "08:00", priority="high", category="walk")

    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    """Adding a task increases the number of tasks stored on the pet."""
    pet = Pet(name="Mochi", species="cat")
    task = make_task("Breakfast", "07:30", priority="high", category="feeding")

    assert len(pet.get_tasks()) == 0
    pet.add_task(task)
    assert len(pet.get_tasks()) == 1


def test_sort_by_time_returns_chronological_order():
    """Tasks come back earliest-first, including an unpadded hour."""
    scheduler = Scheduler()
    tasks = [
        make_task("Playtime", "16:00", pet_name="Biscuit"),
        make_task("Breakfast", "07:30", pet_name="Mochi"),
        make_task("Walk", "9:00", pet_name="Mochi"),
    ]

    ordered = scheduler.sort_by_time(tasks)

    assert [task.time for task in ordered] == ["07:30", "9:00", "16:00"]
    assert tasks[0].description == "Playtime"


def test_daily_completion_creates_task_for_next_day():
    """A finished daily task stays done and a copy is due the next day."""
    owner = Owner(name="Jordan", available_minutes=60)
    pet = Pet(name="Mochi", species="cat")
    owner.add_pet(pet)
    breakfast = make_task("Breakfast", "07:30", frequency="daily")
    pet.add_task(breakfast)
    today = date(2026, 10, 18)

    next_breakfast = Scheduler().mark_task_complete(owner, breakfast, today=today)

    assert breakfast.completed is True
    assert next_breakfast is not None
    assert next_breakfast.completed is False
    assert next_breakfast.due_date == date(2026, 10, 19)
    assert next_breakfast.time == "07:30"
    assert len(pet.get_tasks()) == 2


def test_one_time_task_does_not_recur():
    """Marking a one-time task complete does not create another task."""
    owner = Owner(name="Jordan", available_minutes=60)
    pet = Pet(name="Mochi", species="cat")
    owner.add_pet(pet)
    visit = make_task("Vet visit", "15:00", frequency="once")
    pet.add_task(visit)

    follow_up = Scheduler().mark_task_complete(owner, visit, today=date(2026, 10, 18))

    assert visit.completed is True
    assert follow_up is None
    assert len(pet.get_tasks()) == 1


def test_detect_conflicts_flags_duplicate_times():
    """Two open tasks at the same clock time produce a warning."""
    tasks = [
        make_task("Morning walk", "08:00", pet_name="Mochi"),
        make_task("Ear medication", "08:00", pet_name="Biscuit"),
        make_task("Playtime", "16:00", pet_name="Biscuit"),
    ]

    warnings = Scheduler().detect_conflicts(tasks)

    assert len(warnings) == 1
    assert "08:00" in warnings[0]
    assert "Morning walk" in warnings[0]
    assert "Ear medication" in warnings[0]


def test_pet_with_no_tasks_has_an_empty_plan():
    """A pet with no tasks does not crash the plan or the conflict check."""
    owner = Owner(name="Jordan", available_minutes=30)
    owner.add_pet(Pet(name="Mochi", species="cat"))
    scheduler = Scheduler()

    assert owner.get_all_tasks() == []
    assert scheduler.generate_plan(owner) == []
    assert scheduler.detect_conflicts(owner.get_all_tasks()) == []


def test_generate_plan_keeps_tasks_from_every_pet_in_time_order():
    """A normal day includes each pet and prints the tasks from earliest to latest."""
    owner = Owner(name="Jordan", available_minutes=40, preferences=["walk"])
    mochi = Pet(name="Mochi", species="cat")
    biscuit = Pet(name="Biscuit", species="dog")
    owner.add_pet(mochi)
    owner.add_pet(biscuit)
    biscuit.add_task(make_task("Playtime", "16:00", duration_minutes=5, category="enrichment"))
    mochi.add_task(
        make_task("Breakfast", "07:30", duration_minutes=10, priority="high", category="feeding")
    )

    plan = Scheduler().generate_plan(owner)

    assert [task.time for task in plan] == ["07:30", "16:00"]
    assert {task.pet_name for task in plan} == {"Mochi", "Biscuit"}
