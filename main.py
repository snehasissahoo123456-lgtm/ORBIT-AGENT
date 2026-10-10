from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from config import settings
from orbit_core import plan_goal
from memory import initialise, add_message, audit, get_messages, create_task, get_tasks, get_audit
from provider import chat
from security import workspace_path
from agents import organization, ceo_plan

app = FastAPI(title="ORBIT Founder Agent", version="0.1.0")
STATIC = Path(__file__).parent / "static"
STATIC.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)


class PlanRequest(BaseModel):
    goal: str = Field(min_length=1, max_length=8000)


class WriteRequest(BaseModel):
    path: str = Field(min_length=1, max_length=500)
    content: str = Field(max_length=100000)


@app.on_event("startup")
def on_startup():
    initialise()
    settings.workspace.mkdir(parents=True, exist_ok=True)


@app.get("/", response_class=HTMLResponse)
def index():
    page = STATIC / "index.html"
    if not page.exists():
        return "<h1>ORBIT</h1><p>Dashboard file is missing.</p>"
    return page.read_text(encoding="utf-8")


@app.get("/api/health")
def health():
    return {"status": "ok", "name": "ORBIT", "version": "0.1.0",
            "mode": "local-first starter", "model": settings.ollama_model}


@app.post("/api/chat")
async def send_chat(req: ChatRequest):
    message = req.message.strip()
    if not message:
        raise HTTPException(422, "Message cannot be blank")
    add_message("user", message)
    answer = await chat(message)
    add_message("assistant", answer)
    audit("chat", f"user_message_length={len(message)}")
    return {"reply": answer}


@app.get("/api/messages")
def messages():
    return {"messages": get_messages(50)}


@app.post("/api/tasks/plan")
def create_plan(req: PlanRequest):
    plan = plan_goal(req.goal)
    task_id = create_task(plan.goal, plan.state.value, plan.model_dump(mode="json"))
    return {"task_id": task_id, **plan.model_dump(mode="json")}


@app.get("/api/tasks")
def tasks():
    return {"tasks": get_tasks()}


@app.get("/api/audit")
def audit_events():
    return {"events": get_audit()}


@app.get("/api/workspace")
def list_workspace():
    root = settings.workspace
    files = []
    for p in root.rglob("*"):
        if p.is_file():
            try:
                files.append({"path": p.relative_to(root).as_posix(), "size": p.stat().st_size})
            except OSError:
                pass
        if len(files) >= 500:
            break
    return {"files": files}


@app.get("/api/workspace/read")
def read_workspace_file(path: str):
    try:
        p = workspace_path(path)
        if not p.is_file():
            raise HTTPException(404, "File not found")
        if p.stat().st_size > 200000:
            raise HTTPException(413, "File exceeds preview limit")
        return {"path": path, "content": p.read_text(encoding="utf-8")}
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    except UnicodeDecodeError as exc:
        raise HTTPException(415, "Only UTF-8 text files can be previewed") from exc


@app.post("/api/workspace/write")
def write_workspace_file(req: WriteRequest):
    try:
        p = workspace_path(req.path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(req.content, encoding="utf-8")
        audit("workspace_write", req.path)
        return {"ok": True, "path": p.relative_to(settings.workspace).as_posix(), "bytes": p.stat().st_size}
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


@app.get("/api/status")
def status():
    return {"name": "ORBIT", "stage": "foundation", "autonomous_execution": False,
            "desktop_control": False, "browser_research": False, "voice": False,
            "remote_access": False, "tasks": get_tasks(10)}


@app.get("/api/organization")
def get_organization():
    return organization()


@app.post("/api/ceo/plan")
def founder_request_to_ceo(req: PlanRequest):
    result = ceo_plan(req.goal)
    task_id = create_task(result["goal"], result["state"], result)
    audit("ceo_plan_created", f"task_id={task_id}; goal={result['goal'][:400]}")
    return {"task_id": task_id, **result}
