"""Terminal demo for the PawPal+ scheduler."""

from pawpal_system import Owner, Pet, Scheduler, Task


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
    """Build a two-pet day and print the schedule."""
    owner = Owner(
        name="Jordan",
        available_minutes=40,
        preferences=["walk"],
    )
    mochi = Pet(name="Mochi", species="cat")
    biscuit = Pet(name="Biscuit", species="dog")
    owner.add_pet(mochi)
    owner.add_pet(biscuit)

    mochi.add_task(
        Task(
            description="Breakfast",
            time="07:30",
            frequency="daily",
            duration_minutes=10,
            priority="high",
            category="feeding",
        )
    )
    mochi.add_task(
        Task(
            description="Morning walk",
            time="08:00",
            frequency="daily",
            duration_minutes=25,
            priority="high",
            category="walk",
        )
    )
    biscuit.add_task(
        Task(
            description="Ear medication",
            time="08:10",
            frequency="daily",
            duration_minutes=10,
            priority="high",
            category="medication",
        )
    )
    biscuit.add_task(
        Task(
            description="Playtime",
            time="16:00",
            frequency="daily",
            duration_minutes=5,
            priority="medium",
            category="enrichment",
        )
    )

    scheduler = Scheduler()
    plan = scheduler.generate_plan(owner)
    print(format_schedule(owner, plan, scheduler.explain(owner, plan)))


if __name__ == "__main__":
    main()
