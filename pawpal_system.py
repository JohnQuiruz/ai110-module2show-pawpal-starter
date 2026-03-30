import json
import anthropic
from dataclasses import dataclass, field


@dataclass
class Pet:
    name: str
    species: str
    tasks: list = field(default_factory=list)

    def add_task(self, task) -> None:
        self.tasks.append(task)


@dataclass
class Owner:
    name: str
    pet: Pet
    preferences: dict


@dataclass
class CareTask:
    title: str
    duration_minutes: int
    priority: str
    status: str = "pending"

    def mark_complete(self) -> None:
        self.status = "complete"


@dataclass
class ScheduledTask:
    task: CareTask
    start_time: str
    reason: str


@dataclass
class DailySchedule:
    tasks: list[ScheduledTask] = field(default_factory=list)
    available_minutes: int = 0
    warnings: list[str] = field(default_factory=list)

    def explain(self) -> str:
        lines = ["Daily Care Schedule", "=" * 20]
        for st in self.tasks:
            lines.append(f"{st.start_time} — {st.task.title} ({st.task.duration_minutes} mins, {st.task.priority} priority)")
            lines.append(f"  Reason: {st.reason}")
        used = sum(st.task.duration_minutes for st in self.tasks)
        lines.append(f"\n⏱ Total: {used} min used of {self.available_minutes} available")
        if self.warnings:
            lines.append("")
            lines.extend(self.warnings)
        return "\n".join(lines)


@dataclass
class ClaudeAI:

    def reason(self, owner: Owner, tasks: list[CareTask]) -> list[dict]:
        client = anthropic.Anthropic()

        task_list = "\n".join(
            f"- {t.title} ({t.duration_minutes} mins, priority: {t.priority})"
            for t in tasks
        )

        prompt = f"""You are a pet care scheduling assistant.

Owner: {owner.name}
Owner preferences: {owner.preferences}
Pet: {owner.pet.name} ({owner.pet.species})

Tasks to schedule:
{task_list}

Using the owner's preferences and the pet's needs, assign a start time for each task today.
Factor in task priorities and preferences to determine the safest and most logical order.

Respond with only a JSON array where each object has this exact format:
{{"title": "<task title>", "start_time": "<time like 8:00 AM>", "reason": "<explanation>"}}"""

        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=4096,
            thinking={"type": "adaptive"},
            messages=[{"role": "user", "content": prompt}]
        )

        text = next(block.text for block in response.content if block.type == "text")
        text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip() # remove unnecessary markdown formatting if present
        return json.loads(text)


@dataclass
class Scheduler:
    ai: ClaudeAI

    def build_plan(self, owner: Owner, task_dicts: list[dict]) -> DailySchedule:
        available_minutes = owner.preferences.get("available_minutes", 0)
        max_task_duration = owner.preferences.get("max_task_duration", float("inf"))

        tasks = []
        warnings = []
        for d in task_dicts:
            if d["duration_minutes"] > max_task_duration:
                warnings.append(f"⚠ '{d['title']}' skipped — {d['duration_minutes']} min exceeds max task duration of {max_task_duration} min")
            else:
                tasks.append(CareTask(**d))

        results = self.ai.reason(owner, tasks)

        task_map = {t.title: t for t in tasks}
        scheduled = []
        minutes_used = 0
        for r in results:
            task = task_map[r["title"]]
            if minutes_used + task.duration_minutes > available_minutes:
                warnings.append(f"⚠ '{task.title}' skipped — adding {task.duration_minutes} min would exceed {available_minutes} min budget")
                continue
            scheduled.append(ScheduledTask(
                task=task,
                start_time=r["start_time"],
                reason=r["reason"]
            ))
            minutes_used += task.duration_minutes

        return DailySchedule(tasks=scheduled, available_minutes=available_minutes, warnings=warnings)
