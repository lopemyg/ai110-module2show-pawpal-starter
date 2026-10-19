"""PawPal+ logic layer.

An Owner has many Pets. Each Pet has many Tasks. The Scheduler reads
Owner.get_all_tasks() and builds one daily plan across every pet.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, timedelta

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
    due_date: date | None = None

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

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return tasks ordered by HH:MM time, earliest first."""
        return sorted(tasks, key=lambda task: _clock_minutes(task.time))

    def filter_tasks(
        self,
        tasks: list[Task],
        pet_name: str | None = None,
        completed: bool | None = None,
    ) -> list[Task]:
        """Keep tasks that match a pet name, a completion status, or both."""
        filtered = tasks
        if pet_name is not None:
            filtered = [
                task
                for task in filtered
                if task.pet_name.lower() == pet_name.lower()
            ]
        if completed is not None:
            filtered = [task for task in filtered if task.completed is completed]
        return filtered

    def detect_conflicts(self, tasks: list[Task]) -> list[str]:
        """Warn when two unfinished tasks share a clock time. Does not raise."""
        pending = self.filter_tasks(tasks, completed=False)
        warnings: list[str] = []
        for index, first in enumerate(pending):
            for second in pending[index + 1 :]:
                if first.time != second.time:
                    continue
                warnings.append(
                    f"Conflict at {first.time}: {first.description} ({first.pet_name}) "
                    f"and {second.description} ({second.pet_name}) "
                    "are scheduled at the same time."
                )
        return warnings

    def mark_task_complete(
        self, owner: Owner, task: Task, today: date | None = None
    ) -> Task | None:
        """Mark a task done and queue the next daily or weekly occurrence."""
        task.mark_complete()
        days = {"daily": 1, "weekly": 7}.get(task.frequency.lower())
        if days is None:
            return None

        start = task.due_date or today or date.today()
        next_task = replace(
            task,
            completed=False,
            due_date=start + timedelta(days=days),
        )
        for pet in owner.pets:
            if pet.name.lower() == task.pet_name.lower():
                pet.add_task(next_task)
                break
        return next_task

    def generate_plan(self, owner: Owner) -> list[Task]:
        """Choose tasks that fit the owner's time, priority, and preferences."""
        pending = self.filter_tasks(owner.get_all_tasks(), completed=False)
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

        return self.sort_by_time(chosen)

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
