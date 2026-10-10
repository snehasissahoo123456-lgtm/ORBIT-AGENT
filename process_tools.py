"""Allowlisted subprocess execution. No shell and no arbitrary command strings."""
import asyncio, os, shlex, subprocess
from pathlib import Path
from config import settings
from memory import audit

ALLOWED={"python","python.exe","pytest","pytest.exe","node","node.exe","npm","npm.cmd","git","git.exe"}
BLOCKED_TOKENS={"&&","||",";","|",">","<","$(","format","shutdown","reg","diskpart","del","rmdir","rm","sudo"}

def _root():
    root=settings.workspace.resolve()
    root.mkdir(parents=True,exist_ok=True)
    return root

def validate_command(command: str) -> list[str]:
    if not command or len(command)>1500: raise ValueError("Command is empty or too long")
    if any(tok in command for tok in ("\n","\r","\x00")) or chr(96) in command: raise ValueError("Multiline or shell-substitution commands are blocked")
    parts=shlex.split(command,posix=False)
    if not parts: raise ValueError("Command is empty")
    exe=Path(parts[0].strip('"')).name.lower()
    if exe not in ALLOWED: raise ValueError(f"Executable '{exe}' is not allowlisted")
    if any(tok in command for tok in BLOCKED_TOKENS): raise ValueError("Potentially destructive or shell-composed command blocked")
    if any(p in {"-c","/c","-Command","-EncodedCommand"} for p in parts): raise ValueError("Shell interpreter arguments are blocked")
    return [parts[0].strip('"'),*[p.strip('"') for p in parts[1:]]]

async def run_command(command: str, relative_cwd: str=".", timeout: int=120) -> dict:
    args=validate_command(command); root=_root(); cwd=(root/relative_cwd).resolve()
    if cwd!=root and root not in cwd.parents: raise ValueError("Working directory must remain inside ORBIT workspace")
    if not cwd.is_dir(): raise ValueError("Working directory does not exist")
    timeout=max(1,min(int(timeout),180))
    audit("command_started",f"cwd={cwd.relative_to(root)}; executable={Path(args[0]).name}")
    def run():
        return subprocess.run(args,cwd=cwd,capture_output=True,text=True,timeout=timeout,shell=False,
                              env={**os.environ,"CI":"1"},stdin=subprocess.DEVNULL)
    try:
        result=await asyncio.to_thread(run)
        output=(result.stdout+"\n"+result.stderr)[-12000:]
        audit("command_finished",f"exit={result.returncode}; executable={Path(args[0]).name}")
        return {"command":args,"cwd":cwd.relative_to(root).as_posix(),"exit_code":result.returncode,"output":output}
    except subprocess.TimeoutExpired:
        audit("command_timeout",f"executable={Path(args[0]).name}; timeout={timeout}")
        return {"command":args,"cwd":cwd.relative_to(root).as_posix(),"exit_code":124,"output":f"Timed out after {timeout} seconds"}
