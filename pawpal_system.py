"""PawPal+ logic layer.

Class skeletons translated from diagrams/uml_draft.mmd.
Scheduling behavior is intentionally not implemented yet.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Task:
    """One pet care activity, such as a walk, feeding, or medication."""

    title: str
    duration_minutes: int
    priority: str
    category: str
    pet_name: str


@dataclass
class Pet:
    """A pet and the care tasks that belong to it."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        pass

    def get_tasks(self) -> list[Task]:
        """Return this pet's care tasks."""
        pass


@dataclass
class Owner:
    """The person planning care, including time and preferences."""

    name: str
    available_minutes: int
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet with this owner."""
        pass

    def get_all_tasks(self) -> list[Task]:
        """Collect care tasks across every pet."""
        pass


class Scheduler:
    """Builds a daily plan from an owner's constraints and tasks."""

    def generate_plan(self, owner: Owner) -> list[Task]:
        """Choose and order tasks that fit the owner's time and preferences."""
        pass

    def explain(self, owner: Owner, plan: list[Task]) -> list[str]:
        """Explain why each planned task was chosen.

        The owner is included so a later implementation can cite the time
        budget and preferences, which are not stored on the task list.
        """
        pass
