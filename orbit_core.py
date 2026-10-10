from enum import StrEnum
from pydantic import BaseModel, Field


class TaskState(StrEnum):
    PLANNED = "PLANNED"
    NEEDS_APPROVAL = "NEEDS_APPROVAL"
    RUNNING = "RUNNING"
    VERIFYING = "VERIFYING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"


class PlanStep(BaseModel):
    number: int
    title: str
    description: str
    risk: str = "LOW"
    state: str = "PENDING"


class TaskPlan(BaseModel):
    goal: str
    state: TaskState = TaskState.PLANNED
    steps: list[PlanStep] = Field(default_factory=list)


def risk_for(goal: str) -> str:
    s = goal.casefold()
    if any(x in s for x in ("delete", "format", "payment", "purchase", "publish",
                             "send email", "upload private", "password", "credential",
                             "shutdown", "registry", "administrator")):
        return "HIGH"
    if any(x in s for x in ("install", "write", "modify", "edit", "execute", "run command")):
        return "MEDIUM"
    return "LOW"


def plan_goal(goal: str) -> TaskPlan:
    clean = goal.strip()
    if not clean:
        clean = "Clarify the Founder's desired outcome"
    return TaskPlan(goal=clean, steps=[
        PlanStep(number=1, title="Understand", description="Identify the outcome, constraints and success criteria."),
        PlanStep(number=2, title="Plan", description="Split the goal into small, ordered, verifiable steps."),
        PlanStep(number=3, title="Act safely", description="Use only available tools and ask for approval where required.", risk=risk_for(clean)),
        PlanStep(number=4, title="Verify", description="Inspect outputs and run relevant tests; do not assume success."),
        PlanStep(number=5, title="Report", description="Report evidence, completed work, failures and next steps."),
    ])
