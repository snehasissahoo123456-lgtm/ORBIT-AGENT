from pathlib import Path
import asyncio
import logging
from logging.handlers import RotatingFileHandler
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from config import settings
from orbit_core import plan_goal
from memory import initialise, add_message, audit, get_messages, create_task, get_tasks, get_audit
from provider import chat
from security import workspace_path
from agents import organization, ceo_plan
from developer_engine import create_job, get_job, list_jobs, run_job
from research import research, open_page
from reporting import generate_daily_reports
from process_tools import run_command

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(level=logging.INFO, handlers=[
    logging.StreamHandler(),
    RotatingFileHandler(LOG_DIR / "orbit.log", maxBytes=2_000_000, backupCount=3, encoding="utf-8")
])
logger = logging.getLogger("orbit")
app = FastAPI(title="ORBIT Founder Agent", version="0.2.0")
STATIC = Path(__file__).parent / "static"
STATIC.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")
RUNNING_JOBS: dict[str, asyncio.Task] = {}

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)
class PlanRequest(BaseModel):
    goal: str = Field(min_length=1, max_length=8000)
class WriteRequest(BaseModel):
    path: str = Field(min_length=1, max_length=500)
    content: str = Field(max_length=100000)
class ResearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=1000)
    limit: int = Field(default=6, ge=1, le=10)
class OpenPageRequest(BaseModel):
    url: str = Field(min_length=8, max_length=2000)
class CommandRequest(BaseModel):
    command: str = Field(min_length=1, max_length=1500)
    cwd: str = Field(default=".", max_length=300)
    timeout: int = Field(default=60, ge=1, le=180)
    approved_by_founder: bool = False
class DeveloperRequest(BaseModel):
    goal: str = Field(min_length=1, max_length=8000)
    approved_by_founder: bool = False

@app.on_event("startup")
def on_startup():
    initialise()
    settings.workspace.mkdir(parents=True, exist_ok=True)
    logger.info("ORBIT started; host=%s port=%s workspace=%s", settings.orbit_host, settings.orbit_port, settings.workspace)

@app.on_event("shutdown")
async def on_shutdown():
    for job in RUNNING_JOBS.values():
        if not job.done():
            job.cancel()
    logger.info("ORBIT shutting down")

@app.get("/", response_class=HTMLResponse)
def index():
    page = STATIC / "index.html"
    return page.read_text(encoding="utf-8") if page.exists() else "<h1>ORBIT</h1><p>Dashboard missing.</p>"

@app.get("/api/health")
def health():
    return {"status":"ok","name":"ORBIT","version":"0.2.0","mode":"local-first","model":settings.ollama_model,
            "workspace":str(settings.workspace),"running_jobs":sum(not j.done() for j in RUNNING_JOBS.values())}

@app.post("/api/chat")
async def send_chat(req: ChatRequest):
    message=req.message.strip()
    if not message: raise HTTPException(422,"Message cannot be blank")
    add_message("user",message)
    answer=await chat(message)
    add_message("assistant",answer)
    audit("chat",f"user_message_length={len(message)}")
    return {"reply":answer}

@app.get("/api/messages")
def messages(): return {"messages":get_messages(50)}

@app.post("/api/tasks/plan")
def create_plan(req: PlanRequest):
    plan=plan_goal(req.goal)
    task_id=create_task(plan.goal,plan.state.value,plan.model_dump(mode="json"))
    return {"task_id":task_id,**plan.model_dump(mode="json")}

@app.get("/api/tasks")
def tasks(): return {"tasks":get_tasks()}

@app.get("/api/audit")
def audit_events(): return {"events":get_audit()}

@app.get("/api/workspace")
def list_workspace():
    root=settings.workspace; files=[]
    for p in root.rglob("*"):
        if p.is_file():
            try:
                if any(part in {".git","node_modules",".venv","venv","__pycache__",".orbit_checkpoints"} for part in p.parts): continue
                files.append({"path":p.relative_to(root).as_posix(),"size":p.stat().st_size})
            except OSError: pass
        if len(files)>=500: break
    return {"files":files}

@app.get("/api/workspace/read")
def read_workspace_file(path: str):
    try:
        p=workspace_path(path)
        if not p.is_file(): raise HTTPException(404,"File not found")
        if p.stat().st_size>200000: raise HTTPException(413,"File exceeds preview limit")
        return {"path":path,"content":p.read_text(encoding="utf-8")}
    except ValueError as exc: raise HTTPException(400,str(exc)) from exc
    except UnicodeDecodeError as exc: raise HTTPException(415,"Only UTF-8 text files can be previewed") from exc

@app.post("/api/workspace/write")
def write_workspace_file(req: WriteRequest):
    try:
        p=workspace_path(req.path)
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(req.content,encoding="utf-8")
        audit("workspace_write",req.path)
        return {"ok":True,"path":p.relative_to(settings.workspace).as_posix(),"bytes":p.stat().st_size}
    except ValueError as exc: raise HTTPException(400,str(exc)) from exc

@app.get("/api/status")
def status():
    jobs=list_jobs(10)
    return {"name":"ORBIT","stage":"local-agent-runtime","autonomous_execution":"bounded developer jobs after explicit Founder approval",
            "desktop_control":False,"browser_research":True,"voice":"browser speech APIs where supported; Odia support depends on OS/browser",
            "remote_access":False,"jobs":jobs,"tasks":get_tasks(10)}

@app.get("/api/organization")
def get_organization(): return organization()

@app.post("/api/ceo/plan")
def founder_request_to_ceo(req: PlanRequest):
    result=ceo_plan(req.goal)
    task_id=create_task(result["goal"],result["state"],result)
    audit("ceo_plan_created",f"task_id={task_id}; goal={result['goal'][:400]}")
    return {"task_id":task_id,**result}

@app.post("/api/ceo/execute")
async def ceo_execute_approved(req: DeveloperRequest):
    if not req.approved_by_founder:
        raise HTTPException(403,"Founder approval is required before CEO delegation starts code edits.")
    active=sum(not j.done() for j in RUNNING_JOBS.values())
    if active>=2:
        raise HTTPException(429,"At most two developer jobs may run at once.")
    plan=ceo_plan(req.goal)
    task_id=create_task(req.goal,"RUNNING",plan)
    job=create_job(req.goal)
    RUNNING_JOBS[job["id"]]=asyncio.create_task(run_job(job["id"]),name=f"orbit-ceo-delegated-{job[chr(105)+chr(100)]}")
    audit("ceo_delegated_to_developer",f"task_id={task_id}; job_id={job[chr(105)+chr(100)]}")
    return {"task_id":task_id,"plan":plan,"developer_job":job,"message":"CEO created an auditable plan and delegated implementation to the bounded Developer Agent."}

@app.post("/api/developer/jobs")
async def start_developer_job(req: DeveloperRequest):
    if not req.approved_by_founder:
        raise HTTPException(403,"Founder approval is required before the coding agent edits workspace files.")
    active=sum(not j.done() for j in RUNNING_JOBS.values())
    if active>=2: raise HTTPException(429,"At most two developer jobs may run at once.")
    record=create_job(req.goal)
    task=asyncio.create_task(run_job(record["id"]),name=f"orbit-developer-{record['id']}")
    RUNNING_JOBS[record["id"]]=task
    logger.info("Developer job queued: %s",record["id"])
    return {"job":record,"message":"Job started. Keep the local ORBIT process running."}

@app.get("/api/developer/jobs")
def developer_jobs(): return {"jobs":list_jobs(50)}

@app.get("/api/developer/jobs/{job_id}")
def developer_job(job_id: str):
    job=get_job(job_id)
    if not job: raise HTTPException(404,"Developer job not found")
    return job

@app.post("/api/developer/jobs/{job_id}/stop")
async def stop_developer_job(job_id: str):
    task=RUNNING_JOBS.get(job_id)
    if not task or task.done(): raise HTTPException(409,"Job is not running in this process")
    task.cancel()
    audit("developer_job_cancel_requested",f"id={job_id}")
    return {"ok":True,"job_id":job_id,"state":"STOP_REQUESTED"}

@app.post("/api/research")
async def web_research(req: ResearchRequest):
    try:
        result=await research(req.query,req.limit)
        audit("web_research",f"query={req.query[:300]}; results={len(result['results'])}")
        return result
    except Exception as exc:
        logger.exception("Research failed")
        raise HTTPException(502,f"Research provider failed: {type(exc).__name__}") from exc

@app.post("/api/browser/open")
async def browser_open(req: OpenPageRequest):
    try:
        result=await open_page(req.url)
        audit("browser_page_read",f"url={result.get('url','')[:500]}")
        return result
    except ValueError as exc: raise HTTPException(400,str(exc)) from exc
    except Exception as exc:
        logger.exception("Browser reading failed")
        raise HTTPException(502,f"Browser reading failed: {type(exc).__name__}") from exc

@app.post("/api/command/execute")
async def execute_approved_command(req: CommandRequest):
    if not req.approved_by_founder:
        raise HTTPException(403,"Explicit Founder approval is required for every terminal command.")
    try: return await run_command(req.command,req.cwd,req.timeout)
    except ValueError as exc: raise HTTPException(400,str(exc)) from exc

@app.post("/api/command/execute")
async def execute_approved_command(req: CommandRequest):
    if not req.approved_by_founder:
        raise HTTPException(403,"Explicit Founder approval is required for every terminal command.")
    try:
        return await run_command(req.command,req.cwd,req.timeout)
    except ValueError as exc:
        raise HTTPException(400,str(exc)) from exc

@app.post("/api/reports/daily")
def daily_report():
    result=generate_daily_reports()
    audit("daily_report_generated",str(result))
    return result
