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
        pass


@dataclass
class ClaudeAI:

    def reason(self, owner: Owner, task: CareTask) -> tuple[str, str]:
        pass


@dataclass
class Scheduler:

    def build_plan(self, owner: Owner, tasks: list[CareTask]) -> DailySchedule:
        pass
