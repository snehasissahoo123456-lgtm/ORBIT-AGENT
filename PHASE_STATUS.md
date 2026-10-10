# ORBIT implementation status

This status records code committed to the repository separately from behavior verified on the Founder's Windows PC.

## Implemented in repository code
- [x] FastAPI local application, health/status endpoints and rotating application log
- [x] Activation diagnostics for SQLite, workspace write access, Ollama connectivity/model availability and Playwright package
- [x] Founder-root account setup, password hashing and expiring HttpOnly sessions
- [x] API authentication gate after first Founder setup; public network binding refused
- [x] SQLite messages, tasks, audit events and durable developer-job records
- [x] Founder dashboard for chat, plans, CEO planner, workspace, status and job results
- [x] Optional Ollama local chat provider
- [x] Workspace-confined text-file read/write APIs
- [x] Developer job endpoint requiring explicit Founder approval
- [x] CEO can delegate an approved goal to the bounded Developer Agent
- [x] Model-proposed text-file edits with path, size and file-count limits
- [x] Checkpoints for overwritten files and a bounded three-pass test/fix loop
- [x] Test runner for recognized Python or npm projects, with captured output
- [x] Allowlisted terminal endpoint requiring explicit approval, no shell=True and a timeout
- [x] Web research snippets with source URLs
- [x] Browser reader blocks localhost/private/reserved IP targets and rechecks navigation requests
- [x] Optional Playwright page text extraction for HTTPS URLs
- [x] Daily PDF/PPTX report generation when dependencies are installed
- [x] Daily report scheduler at 23:55 Asia/Kolkata while ORBIT is running
- [x] Interrupted running/queued jobs are marked for review on restart; jobs are not silently resumed
- [x] Browser speech input/output controls where browser and OS support the selected language
- [x] Automated unit tests and GitHub Actions workflow
- [x] Regression tests for duplicate chat context, activation diagnostics, authentication gate and browser URL safety
- [x] API tests for health and approval gates

## Recently added; local verification still required
- [x] Dashboard-side unfinished-task reminder after Founder sign-in, with review, remind-later, and explicit-confirmation coding action
- [x] Windows launcher for installed runtime and opt-in per-user logon startup/disable helpers
- [ ] Test reminder behavior in the actual Windows browser, including session expiry and an empty task ledger
- [ ] Run the startup helpers on the Founder's PC and confirm Windows startup behavior

## Partial / requires verification
- [ ] Install dependencies and run the full app on the Founder's Windows PC; not accessible from this coding session
- [ ] Test model-driven file edits against a real project and review checkpoints
- [ ] Verify web search works on the user's network; snippets are leads, not verified facts
- [ ] Install Playwright Chromium and test browser extraction
- [ ] Generate and inspect PDF/PPT reports on Windows
- [ ] Verify voice input/output in English, Hindi and Odia on the target browser/OS; Odia support is not guaranteed
- [ ] Interrupted jobs are recorded but not automatically resumed after a crash
- [x] CEO execution mirrors Developer Agent terminal state into the task ledger
- [ ] CEO is still a bounded coordinator, not a true independent multi-specialist agent runtime

## Not implemented
- [ ] Full desktop control and application interaction
- [ ] Durable worker queue with retry policy; scheduled reports run only while the PC and ORBIT process are on
- [ ] Employee accounts, department-specific role management and account administration
- [ ] Secure phone-to-PC remote access
- [ ] Production-grade approvals, sandbox/container isolation and full rollback for newly created files
- [ ] Specialist agents with dependency-aware delegation and independent verification
- [ ] Comprehensive Windows end-to-end tests and packaged installer

## Safety defaults
- Keep the server bound to 127.0.0.1; never expose the development API directly to the internet.
- Developer edits require explicit approval and are confined to text files inside the workspace directory.
- Terminal commands use a narrow executable allowlist, shell=False, a workspace working directory and timeouts. Review before using with untrusted projects.
- Never commit credentials, private data or API keys.


## Latest integration note
- The local API now imports the allowlisted command runner and exposes it only behind the explicit approval field. The dashboard does not expose arbitrary command text. The latest GitHub Actions run must pass before this increment can be called CI-verified.

## Important first-run setup
- Run INSTALL_AND_RUN.bat on the Windows PC, then open the local dashboard.
- Create the Founder account on first launch with a unique password of at least 12 characters.
- Install and start Ollama separately and pull the configured model for local AI chat and coding.
- Keep the API local-only; remote control remains disabled.

## Debugging update
- The Windows launcher now checks the Python version, stops on dependency-install failures and reads the configured host/port from settings.
- The chat provider now receives persisted history before saving the current user turn, avoiding duplicate current-message context.
- Use the dashboard's System status & safety panel to inspect activation diagnostics. Ollama must be reachable and the configured model must be installed for local chat and coding.
- A green API health indicator alone does not prove that the local model is available; inspect the individual diagnostics.
