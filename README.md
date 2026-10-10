# ORBIT — Founder-Controlled AI Agent Platform

ORBIT is a separate, local-first agent platform. Its long-term architecture has a Founder console, a CEO coordinator, specialist Developer agents, auditable tools, a persistent task ledger, and verified project-building workflows.

## Current stage
This repository starts the implementation. The initial runnable milestone provides a local FastAPI service, browser dashboard, SQLite memory/audit log, task planning, workspace-confined file operations, and a local Ollama chat provider. This is **not yet a complete autonomous desktop operator**.

## Requirements
- Windows 11 or a recent Linux/macOS system
- Python 3.11+
- Optional: Ollama with a compatible local model for model-backed chat
- Internet only for installing packages / optional research features

## Windows quick start
1. Download or clone this repository.
2. Double-click \`INSTALL_AND_RUN.bat\`.
3. Open \`http://127.0.0.1:8000\`.
4. For local model chat, install Ollama, then run \`ollama pull qwen2.5:7b\` in a separate terminal.
5. Run tests with \`.venv\\Scripts\\python.exe -m pytest\`.

## Safety
- Server binds to loopback by default.
- File APIs are confined to the configured workspace.
- Command execution is disabled in the initial API. Do not expose ORBIT publicly or configure router port forwarding.
- Never store API keys or passwords in source control.
- Model output is untrusted input. Tool actions need explicit policy checks and verification.

## Planned stages
1. Local application shell and health checks
2. Task ledger, durable memory, approvals and audit
3. Tool registry and test/verify loop
4. CEO planner and bounded specialist agents
5. Research/browser integrations with source tracking
6. Desktop automation with visible consent and emergency stop
7. Voice in English, Hindi and Odia
8. Secure remote/mobile access, authentication, backups and recovery
9. Release packaging and repeatable end-to-end tests

A stage is complete only after its tests pass and the README documents what was actually verified.
