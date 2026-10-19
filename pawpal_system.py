"""PawPal+ logic layer.

An Owner has many Pets. Each Pet has many Tasks. The Scheduler reads
Owner.get_all_tasks() and builds one daily plan across every pet.
"""

from __future__ import annotations

from dataclasses import dataclass, field

_PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}


def _clock_minutes(time: str) -> int:
    """Convert an HH:MM string into minutes after midnight."""
    hours, minutes = time.split(":")
    return int(hours) * 60 + int(minutes)


def _overlaps(first: Task, second: Task) -> bool:
    """Return whether two tasks use the same part of the day."""
    first_start = _clock_minutes(first.time)
    second_start = _clock_minutes(second.time)
    first_end = first_start + first.duration_minutes
    second_end = second_start + second.duration_minutes
    return first_start < second_end and second_start < first_end


def _matches_preference(task: Task, owner: Owner) -> bool:
    """Return whether a task matches one of the owner's preferences."""
    text = f"{task.category} {task.description}".lower()
    return any(preference.lower() in text for preference in owner.preferences)


@dataclass
class Task:
    """One pet care activity, such as a walk, feeding, or medication."""

    description: str
    time: str
    frequency: str
    duration_minutes: int
    priority: str
    category: str
    pet_name: str = ""
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def mark_incomplete(self) -> None:
        """Mark this task as not done."""
        self.completed = False


@dataclass
class Pet:
    """A pet and the care tasks that belong to it."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        task.pet_name = self.name
        self.tasks.append(task)

    def get_tasks(self) -> list[Task]:
        """Return a copy of this pet's care tasks."""
        return list(self.tasks)


@dataclass
class Owner:
    """The person planning care, including time and preferences."""

    name: str
    available_minutes: int
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet with this owner."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        """Return every task from every pet."""
        tasks: list[Task] = []
        for pet in self.pets:
            tasks.extend(pet.get_tasks())
        return tasks


class Scheduler:
    """Builds one daily plan from every pet the owner has."""

    def generate_plan(self, owner: Owner) -> list[Task]:
        """Choose tasks that fit the owner's time, priority, and preferences."""
        pending = [task for task in owner.get_all_tasks() if not task.completed]
        ranked = sorted(
            pending,
            key=lambda task: (
                _PRIORITY_RANK.get(task.priority.lower(), 1),
                0 if _matches_preference(task, owner) else 1,
                _clock_minutes(task.time),
            ),
        )

        chosen: list[Task] = []
        minutes_used = 0
        for task in ranked:
            if minutes_used + task.duration_minutes > owner.available_minutes:
                continue
            if any(_overlaps(task, other) for other in chosen):
                continue
            chosen.append(task)
            minutes_used += task.duration_minutes

        chosen.sort(key=lambda task: _clock_minutes(task.time))
        return chosen

    def explain(self, owner: Owner, plan: list[Task]) -> list[str]:
        """Explain why each task was scheduled or left out."""
        planned = {id(task) for task in plan}
        minutes_used = sum(task.duration_minutes for task in plan)
        lines = [
            f"Used {minutes_used} of {owner.available_minutes} minutes across {len(owner.pets)} pets."
        ]

        for task in plan:
            reason = f"{task.priority} priority"
            if _matches_preference(task, owner):
                reason += " and matches a preference"
            lines.append(
                f"{task.time} {task.description} ({task.pet_name}): scheduled because it is {reason}."
            )

        for task in owner.get_all_tasks():
            if id(task) in planned:
                continue
            if task.completed:
                why = "it is already complete"
            elif any(_overlaps(task, chosen) for chosen in plan):
                why = "it overlaps a higher-ranked task"
            else:
                why = "it does not fit the remaining time"
            lines.append(
                f"{task.time} {task.description} ({task.pet_name}): skipped because {why}."
            )
        return lines
