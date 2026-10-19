# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

The first diagram had four classes and two ownership links. An Owner has many Pets. Each Pet has many Tasks. A Scheduler reads the owner and orders tasks into a daily plan. I kept preferences, time slots, and the written explanation off as their own classes so the draft stayed small.

- **Owner** holds the person's name, how many minutes they have, and their preferences. It registers pets and can collect every task those pets need.
- **Pet** holds a name, a species, and that pet's care tasks. It adds a task and returns its own list.
- **Task** is one activity: a title, a duration, a priority, and a category such as a walk, a feeding, or medication.
- **Scheduler** has no data of its own. `generate_plan` chooses and orders tasks using the owner's time and preferences. `explain` states why those tasks were chosen.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes. Reviewing the empty skeleton showed two gaps, both fixed before any scheduling logic was written.

`get_all_tasks` flattens every pet's tasks into one list. A Task that only stores title, duration, priority, and category no longer says which pet it is for, so the plan could not tell a walk for one pet from a walk for another. I added `pet_name` on Task so that link survives once tasks leave the pet.

`explain` originally took only the chosen task list. That list does not include the time budget, the preferences, or the tasks that were left out, so the method could not say why a task made the plan. I changed it to `explain(owner, plan)` so the explanation can use the owner's constraints. I did not add a separate Plan class. A fifth type could store skipped tasks, but the draft is meant to stay on these four classes until the scheduler is implemented.

While implementing the scheduler, Task also gained a clock `time`, a `frequency`, a `completed` flag, and `mark_complete()`. The demo needs tasks at different times, and the tests need a completion status. I kept `duration_minutes` and `priority` so the plan can still fit a time budget. The description field replaced the earlier `title` name.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

`generate_plan` considers four constraints. The minute budget comes first: a task is skipped when it does not fit the time still left. Priority comes next, with high before medium before low. A preference match, such as the word "walk" in the category or description, breaks a tie between equal priorities. Start time is the last tiebreak, and the printed plan is sorted by time after the choices are made.

The budget mattered most because a busy owner cannot do every task. Priority mattered next so a walk or medication beats optional grooming. Preferences are a nudge, not a rule, because a preferred low-priority task should not push out a high-priority one.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

`detect_conflicts` compares the clock time only. A walk at 08:00 and medication at 08:00 produce a warning, even when they belong to different pets. A task at 08:10 that runs during the walk does not, because the time strings are not equal.

That tradeoff fits this app. The owner needs a plain alert when two jobs are booked for the same minute, and an exact match is easy to read. Checking every overlapping minute would catch more clashes, but it is harder to follow. The plan builder already skips duration overlaps when it chooses the day, so the warning can stay a notice instead of stopping the program.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used the assistant in separate phases: a class diagram, skeletons, the four classes, the scheduling methods, the tests, and then the Streamlit page. The most effective help was agent editing across `pawpal_system.py`, `main.py`, and `tests/test_pawpal.py` together, plus narrow questions such as how the Scheduler should get every pet's tasks, how a lambda sorts `"HH:MM"`, and how `timedelta` makes tomorrow. Those prompts stayed on one decision.

Keeping each phase in its own chat helped. The design chat did not get mixed with test failures, and the test chat did not rewrite the UI. I could check one claim at a time: first that `get_all_tasks()` gathers every pet, then that sorting and conflicts print from `main.py`, then that `pytest` stays green.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

I did not sort times with `key=lambda task: task.time`. That version is shorter, but the string `"10:00"` sorts before `"9:00"`. I kept `key=lambda task: _clock_minutes(task.time)` so an unpadded hour still lands in clock order. I also kept `duration_minutes` and `priority` when completion and frequency were added, and I did not let the Scheduler read a single pet. It calls `owner.get_all_tasks()`.

I checked the sort with a test that starts from `16:00`, `07:30`, and `9:00` and expects `07:30`, `9:00`, `16:00`. I checked the multi-pet path by running `python main.py`: the plan includes Mochi and Biscuit and explains the skipped 08:00 medication. `python -m pytest` then passed the full suite.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I tested marking a task complete, adding a task to a pet, chronological sorting, a daily task that creates tomorrow's copy, a one-time task that does not recur, a warning for two tasks at the same clock time, a pet with no tasks, and a plan that keeps both pets in time order.

Those checks matter because they are the behaviors an owner relies on. A wrong sort hides the morning feeding. A missing recurrence drops a daily medication. A silent conflict double-books 08:00. An empty pet must not crash the plan.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I would give the scheduler 4 out of 5. The eight tests passed, and `main.py` shows the same sorting, conflict, and recurrence behavior. I would next test a weekly task due seven days later, a duration overlap that starts at a different minute, and the Streamlit clicks for filter, warning, and mark complete.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I am most satisfied that one Owner method, `get_all_tasks()`, is the only door into every pet. The Scheduler can sort, filter, warn, and plan without reaching into a single pet's list. That kept the four-class design small while the algorithms grew.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I would make the conflict warning mention duration overlaps, not only an exact clock time. A walk from 08:00 to 08:25 and medication at 08:10 should be visible in the same warning the owner sees. I would also let the page edit a task instead of only adding and completing one.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

The useful role is lead architect, not typist. The assistant drafted classes, tests, and UI quickly, but I had to decide the boundaries: four classes, the Owner owns the pet list, and a warning must not crash the plan. Separate chats kept each phase checkable. I trusted a suggestion only after `main.py` or `pytest` showed it.
