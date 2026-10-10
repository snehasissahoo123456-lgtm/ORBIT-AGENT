from dataclasses import dataclass, asdict
from orbit_core import plan_goal


@dataclass(frozen=True)
class AgentRole:
    id: str
    name: str
    responsibility: str
    status: str
    authority: str


ROLES = [
    AgentRole("founder", "Founder", "Sets goals, controls permissions, reviews reports and approves sensitive actions.",
              "PRIMARY_OPERATOR", "Full control"),
    AgentRole("ceo", "CEO Coordinator", "Clarifies goals, creates plans, assigns work packages, tracks blockers and reports progress.",
              "PLANNING_ONLY", "Can plan and assign; cannot bypass approvals"),
    AgentRole("developer", "Developer Agent", "Prepares implementation tasks, test plans, change summaries and verification checklists.",
              "PLANNING_ONLY", "Cannot execute arbitrary commands in this stage"),
    AgentRole("research", "Research Agent", "Future role for sourced web research and evidence summaries.",
              "NOT_IMPLEMENTED", "No web access in this stage"),
    AgentRole("qa", "QA Agent", "Defines test cases and reviews test evidence.",
              "PLANNING_ONLY", "Cannot claim tests passed without output"),
]


def organization():
    return {"founder_is_root": True, "roles": [asdict(role) for role in ROLES]}


def ceo_plan(goal: str):
    base = plan_goal(goal)
    return {
        "coordinator": "CEO",
        "goal": base.goal,
        "state": "PLANNED",
        "assignments": [
            {"agent": "CEO", "work": "Clarify acceptance criteria and sequence work", "state": "PLANNED"},
            {"agent": "Developer", "work": "Prepare a minimal implementation and change list", "state": "PLANNED"},
            {"agent": "QA", "work": "Define checks and inspect evidence", "state": "PLANNED"},
            {"agent": "CEO", "work": "Report outcomes and unresolved blockers to Founder", "state": "PLANNED"},
        ],
        "steps": [step.model_dump(mode="json") for step in base.steps],
        "limitations": "This endpoint creates an auditable plan only. It does not start background agents or execute code."
    }
