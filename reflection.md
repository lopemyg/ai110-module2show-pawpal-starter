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

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used the assistant to turn the UML into class skeletons, then to fill in the four classes, a terminal demo, and two tests. The most useful prompts were specific ones: which fields each class owns, and how the Scheduler should get tasks. The useful answer was to call `Owner.get_all_tasks()` and let that method walk every pet. A second prompt asked for a readable terminal schedule, which became aligned columns instead of printing Task objects.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

I did not replace the scheduling fields when completion, clock time, and frequency were added. Dropping `duration_minutes` and `priority` would have left the Scheduler unable to fit a time budget. I also did not let the Scheduler loop over one pet's tasks. It calls `owner.get_all_tasks()`, and the Owner is the only place that gathers tasks from every pet.

I checked that choice by running `python main.py`. The printed plan includes Mochi and Biscuit, lists different times, and says why the overlapping medication was skipped. I then ran `python -m pytest`. Both tests passed: `mark_complete()` flips `completed`, and adding a task increases that pet's task count.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
