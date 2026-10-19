"""Terminal demo for the PawPal+ scheduler."""

from pawpal_system import Owner, Pet, Scheduler, Task


def format_task_line(task: Task) -> str:
    """Format one task as a single readable line."""
    due = task.due_date.isoformat() if task.due_date else "today"
    status = "done" if task.completed else "open"
    return (
        f"  {task.time}  {task.pet_name:<10} {task.description:<18} "
        f"{status:<5} due {due}"
    )


def format_schedule(owner: Owner, plan: list[Task], reasons: list[str]) -> str:
    """Format a daily plan as aligned columns instead of object text."""
    lines = [
        f"Today's Schedule for {owner.name}",
        f"Time available: {owner.available_minutes} minutes",
        "",
        f"{'Time':<8}{'Pet':<12}{'Task':<20}{'Min':>5}  {'Priority':<10}{'Frequency'}",
        "-" * 64,
    ]
    if not plan:
        lines.append("No tasks fit today's constraints.")
    for task in plan:
        lines.append(
            f"{task.time:<8}{task.pet_name:<12}{task.description:<20}"
            f"{task.duration_minutes:>5}  {task.priority:<10}{task.frequency}"
        )
    lines.append("")
    lines.append("Why this plan:")
    lines.extend(f"  {reason}" for reason in reasons)
    return "\n".join(lines)


def main() -> None:
    """Show sorting, filtering, conflicts, and the next daily occurrence."""
    owner = Owner(
        name="Jordan",
        available_minutes=40,
        preferences=["walk"],
    )
    mochi = Pet(name="Mochi", species="cat")
    biscuit = Pet(name="Biscuit", species="dog")
    owner.add_pet(mochi)
    owner.add_pet(biscuit)

    # Entered out of clock order, with two tasks sharing 08:00.
    entered: list[Task] = []

    def add(pet: Pet, task: Task) -> None:
        pet.add_task(task)
        entered.append(task)

    add(
        biscuit,
        Task(
            description="Playtime",
            time="16:00",
            frequency="daily",
            duration_minutes=5,
            priority="medium",
            category="enrichment",
        ),
    )
    add(
        mochi,
        Task(
            description="Breakfast",
            time="07:30",
            frequency="daily",
            duration_minutes=10,
            priority="high",
            category="feeding",
        ),
    )
    add(
        mochi,
        Task(
            description="Morning walk",
            time="08:00",
            frequency="daily",
            duration_minutes=25,
            priority="high",
            category="walk",
        ),
    )
    add(
        biscuit,
        Task(
            description="Ear medication",
            time="08:00",
            frequency="daily",
            duration_minutes=10,
            priority="high",
            category="medication",
        ),
    )

    scheduler = Scheduler()

    print("Entered order:")
    for task in entered:
        print(format_task_line(task))

    print("\nSorted by time:")
    for task in scheduler.sort_by_time(entered):
        print(format_task_line(task))

    print("\nOpen tasks for Mochi:")
    mochi_open = scheduler.filter_tasks(entered, pet_name="Mochi", completed=False)
    for task in scheduler.sort_by_time(mochi_open):
        print(format_task_line(task))

    print("\nConflict warnings:")
    warnings = scheduler.detect_conflicts(entered)
    if warnings:
        for warning in warnings:
            print(f"  {warning}")
    else:
        print("  None")

    print()
    plan = scheduler.generate_plan(owner)
    print(format_schedule(owner, plan, scheduler.explain(owner, plan)))

    breakfast = mochi.get_tasks()[0]
    next_breakfast = scheduler.mark_task_complete(owner, breakfast)
    print("\nAfter marking Breakfast complete:")
    print(format_task_line(breakfast))
    if next_breakfast is not None:
        print(f"  Next daily occurrence:{format_task_line(next_breakfast)}")


if __name__ == "__main__":
    main()
