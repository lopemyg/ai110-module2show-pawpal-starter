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

Run `python main.py` to see a two-pet day. Run `python -m pytest` for the test suite.

## Features

- **Sorting by time.** `Scheduler.sort_by_time()` orders tasks by clock time. A task entered at 16:00 still appears after a 07:30 feeding in the table and in the daily plan.
- **Filtering by pet or status.** `Scheduler.filter_tasks()` can show one pet, only open tasks, or only finished tasks.
- **Conflict warnings.** `Scheduler.detect_conflicts()` returns a message when two open tasks share a clock time, including tasks for different pets. The app shows that message in a warning and still builds the plan.
- **Daily and weekly recurrence.** `Scheduler.mark_task_complete()` marks a task done. A daily task is copied for the next day, and a weekly task is copied for seven days later. A one-time task is not copied.
- **A plan that explains itself.** `Scheduler.generate_plan()` reads `Owner.get_all_tasks()`, prefers high-priority tasks and the owner's preferences, and skips work that does not fit the minute budget or overlaps a task already chosen. `explain()` says why each task was kept or left out.

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
Entered order:
  16:00  Biscuit    Playtime           open  due today
  07:30  Mochi      Breakfast          open  due today
  08:00  Mochi      Morning walk       open  due today
  08:00  Biscuit    Ear medication     open  due today

Sorted by time:
  07:30  Mochi      Breakfast          open  due today
  08:00  Mochi      Morning walk       open  due today
  08:00  Biscuit    Ear medication     open  due today
  16:00  Biscuit    Playtime           open  due today

Open tasks for Mochi:
  07:30  Mochi      Breakfast          open  due today
  08:00  Mochi      Morning walk       open  due today

Conflict warnings:
  Conflict at 08:00: Morning walk (Mochi) and Ear medication (Biscuit) are scheduled at the same time.

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
  08:00 Ear medication (Biscuit): skipped because it overlaps a higher-ranked task.

After marking Breakfast complete:
  07:30  Mochi      Breakfast          done  due today
  Next daily occurrence:  07:30  Mochi      Breakfast          open  due 2026-10-19
```

## Testing PawPal+

Run the suite from the project root:

```bash
python -m pytest
```

The tests cover marking a task complete, adding a task to a pet, chronological sorting (including an unpadded hour), a daily task that creates tomorrow's copy, a one-time task that does not recur, a warning when two tasks share a clock time, a pet with no tasks, and a plan that keeps both pets in time order.

**Confidence level: ★★★★☆ (4/5).** Those paths passed. The suite does not yet check a weekly recurrence or a duration overlap that starts at a different minute, so those stay outside this score.

```
============================= test session starts ==============================
platform darwin -- Python 3.13.0, pytest-8.3.3, pluggy-1.6.0
rootdir: /Users/agustinlopez/ai110-module2show-pawpal-starter
collected 8 items

tests/test_pawpal.py ........                                            [100%]

============================== 8 passed in 0.02s ===============================
```

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | `sorted()` with `key=lambda task: _clock_minutes(task.time)` orders zero-padded or unpadded `HH:MM` strings from earliest to latest. `generate_plan` uses this for the printed day. |
| Filtering | `Scheduler.filter_tasks()` | Keeps tasks for one pet name, one completion status, or both. `generate_plan` uses it to drop completed tasks before ranking. |
| Conflict handling | `Scheduler.detect_conflicts()` | Returns a warning when two unfinished tasks share the same clock time, including across pets. It does not raise. Duration overlap is still skipped inside `generate_plan`. |
| Recurring tasks | `Scheduler.mark_task_complete()` | Marks the task done. A daily task gets a new open copy due tomorrow (`timedelta(days=1)`). A weekly task is due in 7 days. A one-time task is not copied. |

## Demo Walkthrough

1. Start the app with `streamlit run app.py`. Set the owner name, the minutes available today, and a preference such as `walk`.
2. Add two pets, for example Mochi the cat and Biscuit the dog. Each click calls `Owner.add_pet()`, and both pets stay in memory when the page reruns.
3. Add care tasks for those pets. Include two at the same time, such as an 08:00 walk for Mochi and 08:00 medication for Biscuit. You can enter a 16:00 task first.
4. The task table is ordered by `sort_by_time()`. The pet and status filters call `filter_tasks()`. A warning names the shared time and both tasks so you can move one. The plan still generates.
5. Click **Generate schedule**. The plan lists the tasks that fit the time budget, earliest first, and explains why the other 08:00 task was skipped.
6. Choose a daily task and click **Mark complete**. That task stays done, and a new open copy appears with tomorrow's due date.

Sample CLI output from `python main.py`:

```
Entered order:
  16:00  Biscuit    Playtime           open  due today
  07:30  Mochi      Breakfast          open  due today
  08:00  Mochi      Morning walk       open  due today
  08:00  Biscuit    Ear medication     open  due today

Sorted by time:
  07:30  Mochi      Breakfast          open  due today
  08:00  Mochi      Morning walk       open  due today
  08:00  Biscuit    Ear medication     open  due today
  16:00  Biscuit    Playtime           open  due today

Open tasks for Mochi:
  07:30  Mochi      Breakfast          open  due today
  08:00  Mochi      Morning walk       open  due today

Conflict warnings:
  Conflict at 08:00: Morning walk (Mochi) and Ear medication (Biscuit) are scheduled at the same time.

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
  08:00 Ear medication (Biscuit): skipped because it overlaps a higher-ranked task.

After marking Breakfast complete:
  07:30  Mochi      Breakfast          done  due today
  Next daily occurrence:  07:30  Mochi      Breakfast          open  due 2026-10-19
```
