from pawpal_system import Pet, Owner, ClaudeAI, Scheduler

# --- Pets ---
luna = Pet(name="Luna", species="dog")
mochi = Pet(name="Mochi", species="cat")

# --- Owners ---
# Sarah starts early and has a tight morning window.
# Key constraint: medication must come before any physical exertion.
# With only 60 available minutes and a cap of 20 mins per task, Claude must
# reason carefully — the walk and medication are both high priority but
# medication safety rules override exercise preference.
sarah = Owner(
    name="Sarah",
    pet=luna,
    preferences={
        "wake_time": "6:30 AM",
        "available_minutes": 60,
        "max_task_duration": 20,
        "notes": (
            "Luna was prescribed a heart medication this week. "
            "Vet said it must be given before any physical activity each day. "
            "Sarah prefers the walk early, but medication safety comes first."
        ),
    },
)

# James wakes up late and has a relaxed afternoon.
# Conflict: grooming and feeding are both high priority but Mochi gets
# aggressive when groomed on an empty stomach — feeding must win even
# though grooming is also marked high priority.
james = Owner(
    name="James",
    pet=mochi,
    preferences={
        "wake_time": "9:00 AM",
        "available_minutes": 90,
        "max_task_duration": 25,
        "notes": (
            "Mochi is lethargic today and has been skipping meals. "
            "Vet recommends feeding before any stimulating activity. "
            "Grooming and playtime are important but should only happen "
            "once Mochi has eaten and had time to rest."
        ),
    },
)

# --- Tasks for Luna (dog) ---
# Three high-priority tasks compete for Sarah's tight 60-minute window.
# Claude must apply the medication-before-exercise rule from the notes
# to produce a safe ordering even though the walk is listed first.
luna_tasks = [
    {"title": "Evening Brush",              "duration_minutes": 15, "priority": "low"},
    {"title": "Administer Heart Medication", "duration_minutes": 5,  "priority": "high"},
    {"title": "Breakfast Feeding",          "duration_minutes": 10, "priority": "high"},
    {"title": "Morning Walk",               "duration_minutes": 30, "priority": "high"},
]

# --- Tasks for Mochi (cat) ---
# Feeding and grooming are both high priority, but the notes warn that
# grooming on an empty stomach causes stress — Claude must schedule
# feeding first and push grooming after a rest window.
mochi_tasks = [
    {"title": "Interactive Playtime", "duration_minutes": 15, "priority": "medium"},
    {"title": "Evening Feeding",      "duration_minutes": 10, "priority": "high"},
    {"title": "Grooming Session",     "duration_minutes": 20, "priority": "high"},
    {"title": "Breakfast Feeding",    "duration_minutes": 10, "priority": "high"},
]

# --- Build schedules ---
scheduler = Scheduler(ai=ClaudeAI())

luna_schedule  = scheduler.build_plan(sarah, luna_tasks)
mochi_schedule = scheduler.build_plan(james,  mochi_tasks)

# --- Print Today's Schedule ---
print("Today's Schedule")
print("=" * 40)

print(f"\n{sarah.name}'s schedule for {luna.name} the {luna.species}:")
print(luna_schedule.explain())

# print(f"\n{james.name}'s schedule for {mochi.name} the {mochi.species}:")
# print(mochi_schedule.explain())
