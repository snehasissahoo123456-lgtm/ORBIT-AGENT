(() => {
  "use strict";
  const STORAGE_KEY = "orbit-followup-snoozed-v1";
  const snoozed = () => {
    try { return new Set(JSON.parse(sessionStorage.getItem(STORAGE_KEY) || "[]").map(String)); }
    catch (_) { return new Set(); }
  };
  const saveSnoozed = set => {
    try { sessionStorage.setItem(STORAGE_KEY, JSON.stringify([...set].slice(-200))); } catch (_) {}
  };
  let panel;
  let busy = false;

  function ensurePanel() {
    if (panel && panel.isConnected) return panel;
    panel = document.createElement("section");
    panel.id = "orbit-followup-prompt";
    panel.setAttribute("role", "region");
    panel.setAttribute("aria-label", "Unfinished task reminders");
    panel.style.cssText = "position:fixed;right:18px;bottom:18px;z-index:900;max-width:min(480px,calc(100vw - 36px));max-height:70vh;overflow:auto;background:#101a2b;color:#edf4ff;border:1px solid #5686c8;border-radius:16px;padding:16px;box-shadow:0 16px 55px #0009;font:14px/1.5 system-ui,sans-serif;display:none";
    document.body.appendChild(panel);
    return panel;
  }

  function button(label, handler, primary = false) {
    const b = document.createElement("button");
    b.type = "button";
    b.textContent = label;
    b.style.cssText = "margin:7px 7px 0 0;padding:8px 11px;border-radius:8px;border:1px solid #38557a;cursor:pointer;color:#fff;background:" + (primary ? "#386fe0" : "#1b2b43");
    b.addEventListener("click", handler);
    return b;
  }

  function prepareTask(task) {
    const goal = String(task.goal || "").trim();
    const message = document.getElementById("message");
    const devGoal = document.getElementById("devGoal");
    if (message) message.value = goal;
    if (devGoal) devGoal.value = goal;
    const target = message || devGoal;
    if (target) {
      target.scrollIntoView({ behavior: "smooth", block: "center" });
      target.focus({ preventScroll: true });
    }
    const box = ensurePanel();
    box.style.display = "none";
    box.replaceChildren();
  }

  async function startApprovedCoding(task) {
    const goal = String(task.goal || "").trim();
    const ok = window.confirm("Founder approval required\n\nORBIT will send this goal to the Developer Agent. It may create or edit text files inside workspace/ and run the detected test suite. Review the goal before approving.\n\nContinue?");
    if (!ok) return;
    const box = ensurePanel();
    box.replaceChildren();
    const status = document.createElement("p");
    status.textContent = "Submitting the approved task… Keep ORBIT running.";
    box.appendChild(status);
    box.style.display = "block";
    try {
      const response = await fetch("/api/ceo/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ goal, approved_by_founder: true })
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.detail || "The task could not be started.");
      const muted = snoozed();
      muted.add(String(task.id));
      saveSnoozed(muted);
      status.textContent = "Task submitted. New task #" + data.task_id + " · Developer job " + (data.developer_job && data.developer_job.id ? data.developer_job.id : "created") + ". Check Agent jobs for verified results.";
      box.appendChild(button("Close", () => { box.style.display = "none"; box.replaceChildren(); }));
      if (typeof window.refresh === "function") await window.refresh();
    } catch (error) {
      status.textContent = "ORBIT could not start this task: " + (error && error.message ? error.message : "Unexpected issue") + ". Your original task remains in the ledger; no completion is claimed.";
      box.appendChild(button("Review task", () => prepareTask(task), true));
      box.appendChild(button("Close", () => { box.style.display = "none"; box.replaceChildren(); }));
    }
  }

  async function checkTasks() {
    if (busy || document.hidden) return;
    busy = true;
    try {
      const response = await fetch("/api/tasks", { headers: { "Accept": "application/json" } });
      if (!response.ok) return;
      const data = await response.json();
      const muted = snoozed();
      const pending = (Array.isArray(data.tasks) ? data.tasks : []).filter(task => {
        const state = String(task.state || "").toUpperCase();
        return task.id != null && task.goal && !["COMPLETED", "RUNNING", "DEFERRED"].includes(state) && !muted.has(String(task.id));
      }).slice(0, 5);
      const box = ensurePanel();
      if (!pending.length) {
        box.style.display = "none";
        box.replaceChildren();
        return;
      }
      box.replaceChildren();
      const title = document.createElement("h3");
      title.textContent = "Founder follow-up";
      title.style.cssText = "margin:0 0 6px;font-size:16px;color:#c8dcff";
      box.appendChild(title);
      const intro = document.createElement("p");
      intro.textContent = "ORBIT found unfinished work saved in its task ledger. Would you like to continue one now? Nothing will run until you choose an action.";
      intro.style.margin = "0 0 10px";
      box.appendChild(intro);
      pending.forEach(task => {
        const item = document.createElement("div");
        item.style.cssText = "padding:10px 0;border-top:1px solid #263a56";
        const heading = document.createElement("strong");
        heading.textContent = "#" + task.id + " · " + String(task.state || "PENDING");
        const description = document.createElement("p");
        description.textContent = String(task.goal).slice(0, 500);
        description.style.cssText = "margin:4px 0;color:#c5d4e9;overflow-wrap:anywhere";
        item.append(heading, description);
        item.appendChild(button("Review & continue", () => prepareTask(task), true));
        item.appendChild(button("Start coding with approval", () => startApprovedCoding(task)));
        item.appendChild(button("Remind me later", () => {
          const next = snoozed(); next.add(String(task.id)); saveSnoozed(next); checkTasks();
        }));
        box.appendChild(item);
      });
      box.style.display = "block";
    } catch (_) {
      // A temporary network/session issue should not create a disruptive browser alert.
    } finally {
      busy = false;
    }
  }

  window.addEventListener("load", () => {
    setTimeout(checkTasks, 1800);
    setInterval(checkTasks, 20000);
  });
  document.addEventListener("visibilitychange", () => { if (!document.hidden) checkTasks(); });
})();