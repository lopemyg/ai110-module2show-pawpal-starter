import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("One owner, every pet, one daily plan.")

# Streamlit reruns this file on every click. Create the owner only the
# first time; later runs reuse the same object from session state.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(
        name="Jordan",
        available_minutes=60,
        preferences=["walk"],
    )

owner: Owner = st.session_state.owner
scheduler = Scheduler()

notice = st.session_state.pop("notice", None)
if notice:
    st.success(notice)


def task_rows(task_list: list[Task]) -> list[dict[str, str | int]]:
    """Turn tasks into rows for a Streamlit table."""
    return [
        {
            "Time": task.time,
            "Pet": task.pet_name,
            "Task": task.description,
            "Min": task.duration_minutes,
            "Priority": task.priority,
            "Frequency": task.frequency,
            "Status": "done" if task.completed else "open",
            "Due": task.due_date.isoformat() if getattr(task, "due_date", None) else "today",
        }
        for task in task_list
    ]


st.subheader("Owner")
owner.name = st.text_input("Owner name", value=owner.name)
owner.available_minutes = int(
    st.number_input(
        "Minutes available today",
        min_value=1,
        max_value=24 * 60,
        value=int(owner.available_minutes),
    )
)
preference_text = st.text_input(
    "Preferences (comma-separated)",
    value=", ".join(owner.preferences),
)
owner.preferences = [
    part.strip() for part in preference_text.split(",") if part.strip()
]

st.divider()
st.subheader("Pets")

pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    cleaned_name = pet_name.strip()
    if not cleaned_name:
        st.warning("Enter a pet name first.")
    elif any(pet.name.lower() == cleaned_name.lower() for pet in owner.pets):
        st.warning(f"{cleaned_name} is already on this owner.")
    else:
        owner.add_pet(Pet(name=cleaned_name, species=species))
        st.session_state.notice = f"Added {cleaned_name}."
        st.rerun()

if owner.pets:
    st.table(
        [
            {
                "Pet": pet.name,
                "Species": pet.species,
                "Tasks": len(pet.get_tasks()),
            }
            for pet in owner.pets
        ]
    )
else:
    st.info("No pets yet. Add one above. It stays in memory when the page reruns.")

st.divider()
st.subheader("Tasks")

if not owner.pets:
    st.info("Add a pet before scheduling a task.")
else:
    pet_labels = [f"{pet.name} ({pet.species})" for pet in owner.pets]
    selected_index = st.selectbox(
        "Pet",
        range(len(owner.pets)),
        format_func=lambda index: pet_labels[index],
    )
    selected_pet = owner.pets[selected_index]

    task_col, time_col = st.columns(2)
    with task_col:
        description = st.text_input("Task", value="Morning walk")
    with time_col:
        task_time = st.text_input("Time (HH:MM)", value="08:00")

    duration_col, priority_col = st.columns(2)
    with duration_col:
        duration = st.number_input(
            "Duration (minutes)", min_value=1, max_value=240, value=20
        )
    with priority_col:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    category_col, frequency_col = st.columns(2)
    with category_col:
        category = st.selectbox(
            "Category",
            ["walk", "feeding", "medication", "enrichment", "grooming", "other"],
        )
    with frequency_col:
        frequency = st.selectbox("Frequency", ["once", "daily", "weekly"], index=1)

    if st.button("Add task"):
        hours, separator, minutes = task_time.partition(":")
        valid_time = (
            separator == ":"
            and hours.isdigit()
            and minutes.isdigit()
            and 0 <= int(hours) <= 23
            and 0 <= int(minutes) <= 59
            and len(minutes) == 2
        )
        if not description.strip():
            st.warning("Enter a task description.")
        elif not valid_time:
            st.warning("Use a time like 08:00.")
        else:
            selected_pet.add_task(
                Task(
                    description=description.strip(),
                    time=f"{int(hours):02d}:{minutes}",
                    frequency=frequency,
                    duration_minutes=int(duration),
                    priority=priority,
                    category=category,
                )
            )
            st.session_state.notice = (
                f"Added {description.strip()} for {selected_pet.name}."
            )
            st.rerun()

tasks = owner.get_all_tasks()
if tasks:
    warnings = scheduler.detect_conflicts(tasks)
    if warnings:
        st.caption("These open tasks share a clock time. Move one before the day starts.")
        for warning in warnings:
            st.warning(warning)
    else:
        st.success("No open tasks share a clock time.")

    pet_choices = ["All pets", *[pet.name for pet in owner.pets]]
    filter_col, status_col = st.columns(2)
    with filter_col:
        pet_choice = st.selectbox("Show pet", pet_choices)
    with status_col:
        status_choice = st.selectbox("Show status", ["All", "Open", "Done"])

    selected_pet_name = None if pet_choice == "All pets" else pet_choice
    completed_filter = {"All": None, "Open": False, "Done": True}[status_choice]
    visible = scheduler.sort_by_time(
        scheduler.filter_tasks(
            tasks,
            pet_name=selected_pet_name,
            completed=completed_filter,
        )
    )
    if visible:
        st.table(task_rows(visible))
    else:
        st.info("No tasks match that filter.")

    open_tasks = scheduler.sort_by_time(
        scheduler.filter_tasks(tasks, completed=False)
    )
    if open_tasks:
        done_index = st.selectbox(
            "Mark a task done",
            range(len(open_tasks)),
            format_func=lambda index: (
                f"{open_tasks[index].time} {open_tasks[index].description} "
                f"({open_tasks[index].pet_name})"
            ),
        )
        if st.button("Mark complete"):
            finished = open_tasks[done_index]
            follow_up = scheduler.mark_task_complete(owner, finished)
            if follow_up is not None and follow_up.due_date is not None:
                st.session_state.notice = (
                    f"Marked {finished.description} done. "
                    f"Next {finished.frequency} occurrence is due "
                    f"{follow_up.due_date.isoformat()}."
                )
            else:
                st.session_state.notice = f"Marked {finished.description} done."
            st.rerun()
elif owner.pets:
    st.info("No tasks yet. Add one above.")

st.divider()
st.subheader("Today's Schedule")

if st.button("Generate schedule"):
    st.session_state.show_plan = True

if st.session_state.get("show_plan"):
    if not tasks:
        st.info("Add at least one task before generating a schedule.")
    else:
        plan = scheduler.generate_plan(owner)
        if plan:
            st.table(task_rows(plan))
        else:
            st.warning("No tasks fit today's time and conflicts.")
        reasons = scheduler.explain(owner, plan)
        if reasons:
            st.success(reasons[0])
            for reason in reasons[1:]:
                st.write(reason)
