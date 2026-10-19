# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Implementation summary

PawPal+ keeps care data on three dataclasses and plans the day with one scheduler.

- **Task** is one activity: a description, a clock time, a duration, a priority, a category, a frequency (`once`, `daily`, or `weekly`), and a completed flag. `mark_complete()` flips that flag.
- **Pet** stores a name, a species, and its own task list.
- **Owner** stores the time budget and preferences, and holds every pet. `get_all_tasks()` is the only method that gathers tasks from all pets into one list.
- **Scheduler** never reads a single pet on its own. `generate_plan(owner)` calls `owner.get_all_tasks()`, skips finished tasks, and keeps tasks that fit the minute budget without overlapping a higher-ranked task. Ranking uses priority, then a preference match, then start time. The printed plan is sorted by time. `explain(owner, plan)` states why each task was scheduled or skipped.

Run `python main.py` to see a two-pet day. Run `python -m pytest` for the completion and task-count checks.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Output from `python main.py`:

```
Today's Schedule for Jordan
Time available: 40 minutes

Time    Pet         Task                  Min  Priority  Frequency
----------------------------------------------------------------
07:30   Mochi       Breakfast              10  high      daily
08:00   Mochi       Morning walk           25  high      daily
16:00   Biscuit     Playtime                5  medium    daily

Why this plan:
  Used 40 of 40 minutes across 2 pets.
  07:30 Breakfast (Mochi): scheduled because it is high priority.
  08:00 Morning walk (Mochi): scheduled because it is high priority and matches a preference.
  16:00 Playtime (Biscuit): scheduled because it is medium priority.
  08:10 Ear medication (Biscuit): skipped because it overlaps a higher-ranked task.
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output from `python -m pytest`:

```
tests/test_pawpal.py ..                                                  [100%]

============================== 2 passed in 0.02s ===============================
```

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.generate_plan` | Chooses by priority, then preference match, then start time. The printed plan is ordered by time. |
| Filtering | `Scheduler.generate_plan` | Skips completed tasks and any task that does not fit the remaining minutes. |
| Conflict handling | `Scheduler.generate_plan` | Skips a task whose start time and duration overlap a task already chosen. |
| Recurring tasks | `Task.frequency` | Stores `once`, `daily`, or `weekly`. The plan does not yet create the next occurrence. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
