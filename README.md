# ORBIT — Founder-Controlled AI Agent Platform

ORBIT is a local-first AI agent project for a Founder-controlled workspace. The repository now includes a local dashboard, Founder-root sign-in, Ollama chat, bounded developer jobs, explicit-approval terminal utilities, web research, optional browser reading, daily reports and a task/audit ledger.

**This is an active development build, not a fully autonomous PC operating system.** Remote access, full desktop control, employee accounts and true independent multi-agent coordination are not complete.

## Current features in code
- FastAPI dashboard, rotating application log and activation diagnostics for SQLite, workspace, Ollama and Playwright
- Founder account setup with PBKDF2 password hashing and 12-hour HttpOnly sessions
- SQLite conversation, task, audit and developer-job records
- Optional local Ollama chat using the configured model
- Explicitly approved Developer Agent jobs: bounded model-proposed text-file edits within workspace/, checkpoints for overwritten files and up to three test/fix passes
- Explicitly approved, allowlisted terminal command endpoint; shell=False, workspace-only working directory and timeouts
- Web search snippets with source URLs and optional Playwright HTTPS page reading with private-network URL blocking
- Browser speech input/output where supported by the browser/OS
- PDF and PPTX daily reports, scheduled at 23:55 Asia/Kolkata while ORBIT is running
- Startup marks interrupted developer jobs for review instead of silently resuming them
- Pytest tests and GitHub Actions

## Unfinished-task reminders and startup
- The dashboard checks the persistent task ledger after Founder sign-in and offers unfinished items to review or continue. It does not run a task merely because the dashboard opened.
- The reminder offers a review action that puts the saved goal back into the chat/developer fields, a separate coding action that asks for explicit confirmation, and a session-level “Remind me later” option.
- `START_ORBIT.bat` starts the installed local app without reinstalling dependencies. `ENABLE_ORBIT_STARTUP.bat` optionally adds a per-user Windows sign-in shortcut; `DISABLE_ORBIT_STARTUP.bat` removes it. These scripts must be run on the Founder's PC. They do not install or configure anything from GitHub itself.
- Local tasks require the PC to be powered on and ORBIT to be running. This is not cloud 24/7 hosting and does not yet provide phone-to-PC remote access.

## Windows quick start
1. Clone or download this repository.
2. Double-click INSTALL_AND_RUN.bat and allow dependencies to install.
3. Open http://127.0.0.1:8000.
4. Create your Founder account on first launch. Use a unique password with at least 12 characters and keep it safe.
5. For local-model chat and code generation, install Ollama separately and run: ollama pull qwen2.5:7b
6. Run tests with .venv\Scripts\python.exe -m pytest.

The app runs on the PC while its terminal window is open. Model-backed chat and developer jobs require the local model service to be running. The dashboard's System status & safety panel shows whether Ollama is reachable and whether the configured model is installed. The first install may take several minutes because dependencies and browser files are downloaded.

## Safety and limitations
- The server is configured for loopback only. Startup refuses a non-loopback host because secure remote access is not implemented.
- Do not configure router port forwarding or expose this API to the internet.
- Developer edits require explicit Founder approval and are limited to workspace text files. Review changes, test output and checkpoints before relying on them.
- Terminal tools have an allowlist and require explicit approval; they are not a general unrestricted shell.
- Web results and page contents are untrusted input and require independent source verification.
- Browser voice language availability, especially Odia, depends on the browser and operating system.
- Daily reports run only while the PC and ORBIT process are on.
- Never commit API keys, passwords, private files or personal data to GitHub.

## Still to build and verify
- Full desktop/application control with visible action approvals and emergency stop
- Secure phone-to-PC remote access over an authenticated private connection
- Employee accounts and department-level permissions
- Durable queue with retries and comprehensive crash recovery
- True multi-agent execution, dependency tracking and independent completion verification
- Complete rollback for newly created files, sandbox isolation and Windows end-to-end acceptance tests
- Verify the full installation and model workflow on the Founder's Windows PC

Check PHASE_STATUS.md for the current code-versus-verification status.
