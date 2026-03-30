import json
import anthropic
from dataclasses import dataclass, field


@dataclass
class Pet:
    name: str
    species: str


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


@dataclass
class ScheduledTask:
    task: CareTask
    start_time: str
    reason: str


@dataclass
class DailySchedule:
    tasks: list[ScheduledTask] = field(default_factory=list)

    def explain(self) -> str:
        lines = ["Daily Care Schedule", "=" * 20]
        for st in self.tasks:
            lines.append(f"{st.start_time} — {st.task.title} ({st.task.duration_minutes} mins, {st.task.priority} priority)")
            lines.append(f"  Reason: {st.reason}")
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
            max_tokens=1024,
            thinking={"type": "adaptive"},
            messages=[{"role": "user", "content": prompt}]
        )

        text = next(block.text for block in response.content if block.type == "text")
        return json.loads(text)


@dataclass
class Scheduler:
    ai: ClaudeAI

    def build_plan(self, owner: Owner, task_dicts: list[dict]) -> DailySchedule:
        tasks = [CareTask(**d) for d in task_dicts]
        results = self.ai.reason(owner, tasks)

        task_map = {t.title: t for t in tasks}
        scheduled = [
            ScheduledTask(
                task=task_map[r["title"]],
                start_time=r["start_time"],
                reason=r["reason"]
            )
            for r in results
        ]

        return DailySchedule(tasks=scheduled)
