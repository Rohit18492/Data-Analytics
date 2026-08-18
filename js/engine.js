(function () {
  const KEY = "pathforge_ssot_v1";
  const DE = (window.DE = window.DE || {});
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const esc = (t) => String(t ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const md = (t) => esc(t).replace(/\n/g, "<br>");

  function loadState() {
    try { return Object.assign(defaultState(), JSON.parse(localStorage.getItem(KEY) || "{}")); }
    catch { return defaultState(); }
  }
  function defaultState() {
    return {
      theme: "dark", hours: 0, lastStudy: null, streak: 0, startDate: new Date().toISOString().slice(0, 10),
      completed: {}, inProgress: {}, notes: {}, bookmarks: [], quizLog: [], mockLog: [],
      knownCards: {}, cardQueue: {}, dayDone: {}, dayNotes: {}, dayHours: {},
      projects: {}, monthly: {}, sr: {}, interviewScores: {}, currentMonthGate: {}
    };
  }
  let S = loadState();
  function save() { localStorage.setItem(KEY, JSON.stringify(S)); }

  function bumpStreak() {
    const today = new Date().toISOString().slice(0, 10);
    if (S.lastStudy === today) return;
    const y = new Date(); y.setDate(y.getDate() - 1);
    const ymd = y.toISOString().slice(0, 10);
    S.streak = S.lastStudy === ymd ? (S.streak || 0) + 1 : 1;
    S.lastStudy = today;
    save();
  }

  const NAV = [
    { id: "dashboard", label: "Dashboard", group: "Home" },
    { id: "roadmap", label: "6-Month Roadmap", group: "Home" },
    { id: "month-1", label: "Month 1 — Foundations", group: "Curriculum" },
    { id: "month-2", label: "Month 2 — PySpark & Spark", group: "Curriculum" },
    { id: "month-3", label: "Month 3 — Databricks", group: "Curriculum" },
    { id: "month-4", label: "Month 4 — Databricks Cert", group: "Curriculum" },
    { id: "month-5", label: "Month 5 — Microsoft Fabric", group: "Curriculum" },
    { id: "month-6", label: "Month 6 — DP-700 Cert", group: "Curriculum" },
    { id: "genai", label: "GenAI Preview", group: "Curriculum" },
    { id: "qlik", label: "Qlik → Modern DE Bridge", group: "Curriculum" },
    { id: "projects", label: "Projects", group: "Practice" },
    { id: "capstone", label: "Final Capstone", group: "Practice" },
    { id: "quizzes", label: "Quizzes", group: "Practice" },
    { id: "flashcards", label: "Flashcards", group: "Practice" },
    { id: "codelabs", label: "Code Labs", group: "Practice" },
    { id: "debug", label: "Debugging Lab", group: "Practice" },
    { id: "archlab", label: "Architecture Lab", group: "Practice" },
    { id: "scenarios", label: "Enterprise Scenarios", group: "Practice" },
    { id: "interview", label: "Interview Questions", group: "Career" },
    { id: "simulator", label: "Interview Simulator", group: "Career" },
    { id: "career", label: "Career / Job Readiness", group: "Career" },
    { id: "freelance", label: "Freelancing / Consulting", group: "Career" },
    { id: "cheats", label: "Cheat Sheets", group: "Reference" },
    { id: "diagrams", label: "Architecture Diagrams", group: "Reference" },
    { id: "library", label: "Reference Library", group: "Reference" },
    { id: "books", label: "Books", group: "Reference" },
    { id: "glossary", label: "Glossary", group: "Reference" },
    { id: "certs", label: "Certification Tracker", group: "Tracking" },
    { id: "changelog", label: "Certification Change Log", group: "Tracking" },
    { id: "progress", label: "Progress Tracker", group: "Tracking" },
    { id: "plan", label: "180-Day Study Plan", group: "Tracking" },
    { id: "weekly", label: "Weekly Review", group: "Tracking" },
    { id: "monthly", label: "Monthly Assessments", group: "Tracking" },
    { id: "bootcamp", label: "30-Day Exam Bootcamp", group: "Tracking" },
    { id: "bookmarks", label: "My Bookmarks", group: "Tracking" }
  ];

  function renderNav() {
    const q = ($("#navFilter").value || "").toLowerCase();
    let html = "";
    let g = "";
    NAV.forEach((n) => {
      if (q && !n.label.toLowerCase().includes(q)) return;
      if (n.group !== g) { g = n.group; html += `<div class="sec">${esc(g)}</div>`; }
      html += `<button data-go="${n.id}"><span class="label">${esc(n.label)}</span></button>`;
    });
    $("#nav").innerHTML = html;
  }

  function go(id, extra) {
    location.hash = extra ? `#${id}/${extra}` : `#${id}`;
  }
  function route() {
    const raw = (location.hash || "#dashboard").slice(1);
    const [id, extra] = raw.split("/");
    $$("#nav button").forEach((b) => b.classList.toggle("active", b.dataset.go === id));
    const view = $("#view");
    const map = {
      dashboard: viewDashboard, roadmap: viewRoadmap, qlik: viewQlik, projects: viewProjects,
      capstone: viewCapstone, quizzes: viewQuizzes, flashcards: viewFlash, interview: viewInterview,
      cheats: viewCheats, diagrams: viewDiagrams, library: viewLibrary, books: viewBooks,
      glossary: viewGlossary, certs: viewCerts, changelog: viewChangelog, progress: viewProgress,
      plan: viewPlan, weekly: viewWeekly, monthly: viewMonthly, genai: () => viewMonth(7),
      bookmarks: viewBookmarks, career: viewCareer, freelance: viewFreelance, simulator: viewSimulator,
      bootcamp: viewBootcamp, codelabs: viewCodeLabs, debug: viewDebug, archlab: viewArch, scenarios: viewScenarios
    };
    if (id === "lesson") return viewLesson(extra, view);
    if (id && id.startsWith("month-")) return viewMonth(Number(id.split("-")[1]), view);
    (map[id] || viewDashboard)(view, extra);
  }

  function lessons() { return DE.lessons || []; }
  function quizzes() { return DE.quizzes || []; }
  function cards() { return DE.flashcards || []; }
  function days() { return DE.days || []; }

  function readiness() {
    const L = lessons();
    const done = L.filter((l) => S.completed[l.id]).length;
    const knowledge = L.length ? done / L.length : 0;
    const proj = Object.values(S.projects).filter((p) => p === "done").length;
    const projT = (DE.projects || []).length || 1;
    const hands = Math.min(1, (S.hours / 280) * 0.5 + (proj / projT) * 0.5);
    const qLog = S.quizLog.slice(-40);
    const quizP = qLog.length ? qLog.reduce((a, b) => a + b.pct, 0) / qLog.length / 100 : 0;
    const mocks = S.mockLog;
    const mockP = mocks.length ? mocks.reduce((a, b) => a + b.pct, 0) / mocks.length / 100 : 0;
    const score = knowledge * 0.25 + hands * 0.25 + quizP * 0.2 + mockP * 0.2 + (proj / projT) * 0.1;
    const pct = Math.round(score * 100);
    let band = "Not Ready", color = "exp";
    if (pct >= 95) { band = "Highly Ready"; color = "easy"; }
    else if (pct >= 85) { band = "Ready"; color = "easy"; }
    else if (pct >= 75) { band = "Almost Ready"; color = "med"; }
    else if (pct >= 60) { band = "Needs Improvement"; color = "adv"; }
    return { pct, band, color, knowledge, hands, quizP, mockP, proj: proj / projT, done, remaining: L.length - done };
  }

  function recNext() {
    const L = lessons().sort((a, b) => a.day - b.day);
    return L.find((l) => !S.completed[l.id]) || L[0];
  }

  function todayRevision() {
    const now = Date.now();
    const out = [];
    Object.entries(S.sr).forEach(([id, rec]) => {
      if (rec.next && rec.next <= now) out.push(id);
    });
    return out.slice(0, 8).map((id) => lessons().find((l) => l.id === id)).filter(Boolean);
  }

  function kpi(title, val, sub) {
    return `<div class="card"><div class="muted">${title}</div><h2>${val}</h2><div class="muted">${sub || ""}</div></div>`;
  }

  function viewDashboard(view) {
    const r = readiness();
    const next = recNext();
    const rev = todayRevision();
    const week = Math.min(26, Math.floor((Object.keys(S.completed).length / Math.max(1, lessons().length)) * 26) + 1);
    const month = Math.min(6, Math.ceil(week / 4.34));
    view.innerHTML = `
      <div class="disclaimer"><strong>Certification notice:</strong> This artifact is a structured preparation system designed around the official May 4, 2026 Databricks Data Engineer Associate exam guide and the DP-700 skills measured as of July 21, 2026. Completing it does <em>not</em> guarantee certification. Validate readiness with official practice assessments and hands-on platform work.</div>
      <h1>Dashboard</h1>
      <p class="muted">Senior Data &amp; AI Analytics path for an experienced Qlik/BI engineer. Last verified sources: 18 Aug 2026.</p>
      <div class="grid kpis">
        ${kpi("Overall progress", r.pct + "%", r.band)}
        ${kpi("Current month / week", "M" + month + " · W" + week, next ? next.title : "")}
        ${kpi("Topics", r.done + " done", r.remaining + " remaining")}
        ${kpi("Study streak", (S.streak || 0) + " days", (S.hours || 0).toFixed(1) + " hours logged")}
      </div>
      <div class="grid cards-2" style="margin-top:14px">
        <div class="card">
          <h3>Certification readiness</h3>
          <div class="progress"><span style="width:${r.pct}%"></span></div>
          <p class="muted">Knowledge ${Math.round(r.knowledge*100)}% · Hands-on ${Math.round(r.hands*100)}% · Quizzes ${Math.round(r.quizP*100)}% · Mocks ${Math.round(r.mockP*100)}% · Projects ${Math.round(r.proj*100)}%</p>
          <p class="${r.color}"><strong>${r.band}</strong> (${r.pct}%)</p>
          <p>🔴 0–59 Not Ready · 🟠 60–74 Needs Improvement · 🟡 75–84 Almost Ready · 🟢 85–94 Ready · 🔵 95+ Highly Ready</p>
        </div>
        <div class="card">
          <h3>Recommended next lesson</h3>
          ${next ? `<h2>${esc(next.title)}</h2><p class="muted">Month ${next.month} · ${esc(next.topic)}</p><button class="btn primary" data-go="lesson/${next.id}">Open lesson</button>` : "All lessons complete."}
          <h3 style="margin-top:16px">Today's Revision (spaced repetition)</h3>
          ${rev.length ? rev.map((l) => `<div><a href="#lesson/${l.id}">${esc(l.title)}</a></div>`).join("") : `<p class="muted">Complete a lesson to schedule 1/3/7/14/30-day reviews.</p>`}
        </div>
      </div>
      <div class="card" style="margin-top:14px">
        <h3>Log study time</h3>
        <div class="flex">
          <button class="btn" data-hours="1">+1h</button>
          <button class="btn" data-hours="1.5">+1.5h</button>
          <button class="btn" data-hours="3">+3h weekend</button>
          <span class="muted">Target 12–14h/week</span>
        </div>
      </div>`;
    view.querySelectorAll("[data-hours]").forEach((b) => b.onclick = () => { S.hours += Number(b.dataset.hours); bumpStreak(); save(); route(); });
  }

  function viewRoadmap(view) {
    view.innerHTML = `<h1>6-Month Roadmap</h1>
      <p>Transition: Qlik/BI Developer → Modern Data Engineer → Databricks + Fabric Specialist → AI-Powered Analytics Consultant → Data &amp; AI Architect.</p>
      ${(DE.roadmap || []).map((m) => `<div class="acc open"><button>${esc(m.title)}</button><div class="body"><p>${esc(m.goal)}</p><ul>${m.outcomes.map((o) => `<li>${esc(o)}</li>`).join("")}</ul></div></div>`).join("")}`;
  }

  function viewMonth(n, view) {
    const ls = lessons().filter((l) => l.month === n);
    const done = ls.filter((l) => S.completed[l.id]).length;
    const gate = n <= 6 ? (S.monthly[n] || 0) : 100;
    view.innerHTML = `<h1>Month ${n === 7 ? "GenAI Layer" : n}</h1>
      <p class="muted">${done}/${ls.length} lessons · Monthly assessment ${gate}% ${n<=6 ? "(80% required to mark month complete)" : ""}</p>
      <div class="progress"><span style="width:${ls.length? (done/ls.length*100):0}%"></span></div>
      ${ls.map((l) => `<div class="card" style="margin-top:10px"><div class="flex"><span class="chip">${esc(l.topic)}</span><span class="badge">${S.completed[l.id]?"Done":"Not started"}</span></div><h3>${esc(l.title)}</h3><p class="muted">${esc(l.summary||"")}</p><button class="btn primary" data-go="lesson/${l.id}">Learn</button></div>`).join("")}`;
  }

  function scheduleSR(id) {
    const intervals = [1, 3, 7, 14, 30].map((d) => d * 86400000);
    const rec = S.sr[id] || { i: 0 };
    rec.i = Math.min(rec.i + 1, intervals.length - 1);
    rec.next = Date.now() + intervals[rec.i];
    S.sr[id] = rec;
  }

  function viewLesson(id, view) {
    const l = lessons().find((x) => x.id === id);
    if (!l) { view.innerHTML = "Lesson not found"; return; }
    S.inProgress[id] = true; save(); bumpStreak();
    const bookmarked = S.bookmarks.some((b) => b.id === id);
    view.innerHTML = `<div class="lesson">
      <div class="flex"><span class="chip">Month ${l.month}</span><span class="chip">${esc(l.topic)}</span><span class="badge">${esc(l.difficulty||"Intermediate")}</span></div>
      <h1>${esc(l.title)}</h1>
      <p class="muted">Learning mode: Learn → Understand → Apply → Test → Build → Interview → Review → Master</p>
      <div class="tabs" id="ltabs">
        ${["Learn","Understand","Apply","Test","Build","Interview","Review","Master","Notes"].map((t,i)=>`<button data-t="${i}" class="${i===0?"on":""}">${t}</button>`).join("")}
      </div>
      <div id="lbody"></div>
      <div class="flex" style="margin-top:12px">
        <button class="btn primary" id="completeBtn">Mark complete</button>
        <button class="btn" id="bm">${bookmarked?"Remove bookmark":"Bookmark"}</button>
      </div>
    </div>`;
    const panes = [
      `<div class="levels">
        <div class="level"><strong>Level 1 — Simple</strong><p>${md(l.simple)}</p></div>
        <div class="level"><strong>Level 2 — Professional</strong><p>${md(l.professional)}</p></div>
        <div class="level"><strong>Level 3 — Architect</strong><p>${md(l.architect)}</p></div>
        ${l.qlik ? `<div class="level"><strong>Qlik bridge</strong><p>${md(l.qlik)}</p></div>` : ""}
        <p><strong>Business use:</strong> ${md(l.business||"")}</p>
        <p><strong>Common mistakes:</strong></p><ul>${(l.mistakes||[]).map(m=>`<li>${esc(m)}</li>`).join("")}</ul>
      </div>`,
      `${l.code ? `<pre>${esc(l.code)}</pre><p class="muted">Expected output</p><pre>${esc(l.output||"")}</pre>` : `<p>${md(l.understand||l.simple)}</p>`}`,
      `<p>${md(l.exercise||"")}</p><p>${md(l.handsOn||"")}</p>`,
      quizBlock(l.quizTag || l.topic, 6),
      `<p>${md(l.miniProject||"Complete the related industry project module.")}</p>`,
      interviewBlock(l.interviewTag || l.topic, 5),
      `<pre>${esc(l.cheatsheet||"See Cheat Sheets section.")}</pre>`,
      `<p>${md(l.master||l.scenario||"")}</p>`,
      `<textarea class="note" id="note">${esc(S.notes[id]||"")}</textarea><button class="btn primary" id="saveNote">Save notes</button>`
    ];
    const body = $("#lbody");
    const show = (i) => { body.innerHTML = panes[i]; if (i===3) bindQuiz(body); if (i===8) $("#saveNote").onclick = () => { S.notes[id]=$("#note").value; save(); }; };
    show(0);
    $$("#ltabs button").forEach((b) => b.onclick = () => { $$("#ltabs button").forEach(x=>x.classList.remove("on")); b.classList.add("on"); show(+b.dataset.t); });
    $("#completeBtn").onclick = () => { S.completed[id]=true; scheduleSR(id); save(); route(); };
    $("#bm").onclick = () => toggleBm({type:"lesson", id, title:l.title});
  }

  function toggleBm(item) {
    const i = S.bookmarks.findIndex((b) => b.id === item.id && b.type === item.type);
    if (i >= 0) S.bookmarks.splice(i, 1); else S.bookmarks.push(item);
    save(); route();
  }

  function quizBlock(tag, n) {
    const qs = quizzes().filter((q) => (q.tags||[]).some((t) => String(t).toLowerCase().includes(String(tag).toLowerCase())) || (q.topic||"").toLowerCase().includes(String(tag).toLowerCase())).slice(0, n);
    const pick = qs.length ? qs : quizzes().slice(0, n);
    return `<div class="quiz-set">${pick.map((q,i)=>renderQ(q,i)).join("")}<button class="btn primary" data-grade>Grade</button><div class="result"></div></div>`;
  }
  function renderQ(q, i) {
    const opts = (q.options || []).map((o, idx) => `<button class="q-opt" data-i="${idx}">${esc(typeof o === "string" ? o : o.text)}</button>`).join("");
    return `<div class="card qcard" data-id="${esc(q.id)}" data-ans="${q.answer}" data-type="${q.type||"mcq"}" style="margin:8px 0">
      <div class="flex"><span class="badge ${diffClass(q.difficulty)}">${esc(q.difficulty||"Medium")}</span><span class="chip">${esc(q.topic||"")}</span></div>
      <p><strong>Q${i+1}.</strong> ${esc(q.stem)}</p>
      ${q.code?`<pre>${esc(q.code)}</pre>`:""}
      ${opts}
    </div>`;
  }
  function diffClass(d) {
    const x = String(d||"").toLowerCase();
    if (x.includes("easy")||x.includes("beginner")||x.includes("junior")) return "easy";
    if (x.includes("expert")||x.includes("architect")) return "exp";
    if (x.includes("adv")||x.includes("hard")||x.includes("senior")) return "adv";
    return "med";
  }
  function bindQuiz(root) {
    $$(".qcard", root).forEach((card) => {
      $$(".q-opt", card).forEach((b) => b.onclick = () => {
        if (card.dataset.type === "multi") b.classList.toggle("picked");
        else { $$(".q-opt", card).forEach(x=>x.classList.remove("picked")); b.classList.add("picked"); }
        b.style.outline = "2px solid var(--accent)";
      });
    });
    const grade = $("[data-grade]", root);
    if (!grade) return;
    grade.onclick = () => {
      let ok = 0, n = 0;
      $$(".qcard", root).forEach((card) => {
        n++;
        const ans = String(card.dataset.ans).split(",").map(Number);
        const picked = $$(".q-opt", card).map((b,i)=>b.classList.contains("picked")?i:-1).filter(i=>i>=0);
        const good = picked.length === ans.length && picked.every((p,i)=>ans.includes(p));
        if (good) ok++;
        $$(".q-opt", card).forEach((b,i) => {
          if (ans.includes(i)) b.classList.add("correct");
          if (b.classList.contains("picked") && !ans.includes(i)) b.classList.add("wrong");
        });
        const q = quizzes().find((x) => x.id === card.dataset.id);
        if (q) {
          const exp = document.createElement("div");
          exp.innerHTML = `<p><strong>${good?"Correct":"Incorrect"}.</strong> ${esc(q.explain||"")}</p>
            ${(q.whyWrong||[]).map((w)=>`<p class="muted">${esc(w)}</p>`).join("")}
            <p class="muted">Related: ${esc(q.topic||"")} · ${q.ref?`<a href="${esc(q.ref)}" target="_blank" rel="noopener">Reference</a>`:""}</p>`;
          card.appendChild(exp);
        }
      });
      const pct = n ? Math.round(ok / n * 100) : 0;
      S.quizLog.push({ ts: Date.now(), ok, n, pct, tag: "lesson" });
      save();
      $(".result", root).textContent = `Score ${ok}/${n} (${pct}%)`;
    };
  }

  function interviewBlock(tag, n) {
    const qs = (DE.interview || []).filter((q) => (q.tags||[]).join(" ").toLowerCase().includes(String(tag).toLowerCase()) || (q.topic||"").toLowerCase().includes(String(tag).toLowerCase())).slice(0, n);
    const pick = qs.length ? qs : (DE.interview || []).slice(0, n);
    return pick.map((q) => `<div class="acc"><button>${esc(q.q)} · ${esc(q.level||"Senior")}</button><div class="body">
      <p><strong>Short:</strong> ${esc(q.short)}</p>
      <p><strong>Detailed:</strong> ${esc(q.long)}</p>
      <p><strong>Real-world:</strong> ${esc(q.example||"")}</p>
      <p><strong>Follow-ups:</strong> ${(q.followups||[]).map(esc).join(" · ")}</p>
      <p><strong>Mistakes:</strong> ${(q.mistakes||[]).map(esc).join("; ")}</p>
    </div></div>`).join("");
  }

  function viewQuizzes(view, extra) {
    const banks = [
      { id: "dbx", label: "Databricks practice (500+)" },
      { id: "dp700", label: "DP-700 practice (500+)" },
      { id: "core", label: "Foundations / Spark / GenAI" },
      { id: "mock-dbx", label: "Databricks mock exams (5)" },
      { id: "mock-dp", label: "DP-700 mock exams (5)" }
    ];
    if (extra && extra.startsWith("mock")) return runMock(view, extra);
    if (extra) return runBank(view, extra);
    view.innerHTML = `<h1>Quiz Engine</h1>
      <p class="muted">Original practice items aligned to official objectives. Not real exam questions.</p>
      ${banks.map(b=>`<div class="card" style="margin:8px 0"><h3>${esc(b.label)}</h3><button class="btn primary" data-go="quizzes/${b.id}">Start</button></div>`).join("")}`;
  }

  function runBank(view, bank) {
    const qs = shuffle(quizzes().filter((q) => q.bank === bank)).slice(0, 20);
    view.innerHTML = `<h1>Practice · ${esc(bank)}</h1><p class="muted">20-question session (full bank remains available; repeat for new draws).</p>
      <div class="quiz-set">${qs.map((q,i)=>renderQ(q,i)).join("")}<button class="btn primary" data-grade>Grade</button><div class="result"></div></div>`;
    bindQuiz(view);
  }

  function runMock(view, extra) {
    const isDbx = extra.includes("dbx");
    const bank = isDbx ? "dbx" : "dp700";
    const n = isDbx ? 45 : 50;
    const all = quizzes().filter((q) => q.bank === bank);
    const qs = shuffle(all).slice(0, n);
    view.innerHTML = `<h1>${isDbx?"Databricks":"DP-700"} mock exam</h1>
      <p>${n} questions · ${isDbx?"90":"100"} minutes recommended · randomized</p>
      <div class="quiz-set">${qs.map((q,i)=>renderQ(q,i)).join("")}<button class="btn primary" data-grade>Submit mock</button><div class="result"></div></div>`;
    const grade = $("[data-grade]", view);
    bindQuiz(view);
    const orig = grade.onclick;
    grade.onclick = () => {
      orig();
      const text = $(".result", view).textContent;
      const m = /Score (\d+)\/(\d+) \((\d+)%\)/.exec(text||"");
      if (m) {
        const pct = +m[3];
        const domains = {};
        $$(".qcard", view).forEach((c) => {
          const q = quizzes().find((x) => x.id === c.dataset.id);
          if (!q) return;
          domains[q.domain||"General"] = domains[q.domain||"General"] || {ok:0,n:0};
          domains[q.domain||"General"].n++;
        });
        S.mockLog.push({ ts: Date.now(), bank, pct, n: +m[2], ok: +m[1], domains });
        save();
        const weak = Object.entries(domainBreakdown(view)).sort((a,b)=>a[1]-b[1]).slice(0,5);
        $(".result", view).innerHTML += `<div class="card"><h3>Readiness</h3><p>${pct>=85?"Pass-leaning practice score":"Below target — revise weak domains"}</p>
          <p>Weak areas: ${weak.map(([k,v])=>`${esc(k)} ${v}%`).join(", ")||"n/a"}</p></div>`;
      }
    };
  }
  function domainBreakdown(root) {
    const d = {};
    $$(".qcard", root).forEach((card) => {
      const q = quizzes().find((x) => x.id === card.dataset.id);
      if (!q) return;
      const k = q.domain || "General";
      d[k] = d[k] || {ok:0,n:0};
      d[k].n++;
      const ans = String(card.dataset.ans).split(",").map(Number);
      const picked = $$(".q-opt", card).map((b,i)=>b.classList.contains("picked")?i:-1).filter(i=>i>=0);
      if (picked.length === ans.length && picked.every((p)=>ans.includes(p))) d[k].ok++;
    });
    const out = {};
    Object.entries(d).forEach(([k,v]) => out[k] = Math.round(v.ok/v.n*100));
    return out;
  }
  function shuffle(a) { return a.map((x) => [Math.random(), x]).sort((a,b)=>a[0]-b[0]).map(x=>x[1]); }

  function viewFlash(view) {
    const list = cards();
    let i = Number(sessionStorage.getItem("fc_i") || 0) % Math.max(1, list.length);
    const draw = () => {
      const c = list[i];
      if (!c) { view.innerHTML = "No cards"; return; }
      view.innerHTML = `<h1>Flashcards</h1><p class="muted">${i+1}/${list.length} · Known ${Object.keys(S.knownCards).length}</p>
        <div class="card flash" id="fc">${esc(c.front)}</div>
        <div class="flex" style="margin-top:10px">
          <button class="btn" id="flip">Flip</button>
          <button class="btn primary" id="know">Know it</button>
          <button class="btn" id="again">Review again</button>
          <button class="btn" id="next">Next</button>
        </div>`;
      let front = true;
      $("#flip").onclick = $("#fc").onclick = () => { front = !front; $("#fc").textContent = front ? c.front : c.back; };
      $("#know").onclick = () => { S.knownCards[c.id]=true; save(); i=(i+1)%list.length; sessionStorage.setItem("fc_i", i); draw(); };
      $("#again").onclick = $("#next").onclick = () => { i=(i+1)%list.length; sessionStorage.setItem("fc_i", i); draw(); };
    };
    draw();
  }

  function viewProjects(view) {
    view.innerHTML = `<h1>Industry Projects</h1>${(DE.projects||[]).map(p=>`
      <div class="acc"><button>${esc(p.title)} · ${esc(S.projects[p.id]||"not started")}</button>
      <div class="body">${projectHtml(p)}
        <div class="flex"><button class="btn" data-p="${p.id}" data-s="doing">In progress</button>
        <button class="btn primary" data-p="${p.id}" data-s="done">Complete</button></div>
      </div></div>`).join("")}`;
    view.querySelectorAll("[data-p]").forEach((b) => b.onclick = () => { S.projects[b.dataset.p]=b.dataset.s; save(); route(); });
    bindAcc(view);
  }
  function projectHtml(p) {
    const keys = ["problem","requirements","technical","dataset","dictionary","sources","architecture","ingestion","transform","model","quality","security","governance","monitor","perf","output","testing","docs","interview","github"];
    return keys.filter(k=>p[k]).map(k=>`<h4>${esc(k)}</h4><p>${md(typeof p[k]==="string"?p[k]:JSON.stringify(p[k],null,2))}</p>`).join("");
  }
  function viewCapstone(view) {
    const p = (DE.projects||[]).find(x=>x.capstone) || DE.capstone;
    view.innerHTML = `<h1>Capstone: AI-Powered Enterprise Analytics Platform</h1>${p?projectHtml(p):""}`;
  }

  function viewInterview(view) {
    const cats = [...new Set((DE.interview||[]).map(q=>q.topic))];
    view.innerHTML = `<h1>Interview Bank (${(DE.interview||[]).length})</h1>
      <p>Senior and Architect emphasis for 12+ years experience.</p>
      <select id="ic">${cats.map(c=>`<option>${esc(c)}</option>`).join("")}</select>
      <div id="ilist"></div>`;
    const draw = () => {
      const c = $("#ic").value;
      $("#ilist").innerHTML = interviewBlock(c, 40) || "";
      bindAcc(view);
    };
    $("#ic").onchange = draw; draw();
  }

  function viewCheats(view) {
    view.innerHTML = `<h1>Cheat Sheets</h1><p class="muted">Print via browser (Ctrl+P).</p>${(DE.cheats||[]).map(c=>`
      <div class="acc"><button>${esc(c.title)}</button><div class="body"><pre>${esc(c.body)}</pre></div></div>`).join("")}`;
    bindAcc(view);
  }
  function viewDiagrams(view) {
    view.innerHTML = `<h1>Architecture Diagrams</h1>${(DE.diagrams||[]).map(d=>`
      <div class="card" style="margin:10px 0"><h3>${esc(d.title)}</h3>
      <div class="svg-box">${d.svg}</div>
      <p>${esc(d.explain)}</p>
      <p><strong>Components:</strong> ${esc((d.components||[]).join(", "))}</p>
      <p><strong>Data flow:</strong> ${esc(d.flow||"")}</p>
      <p><strong>When to use:</strong> ${esc(d.when||"")}</p>
      <p><strong>Interview:</strong> ${(d.interview||[]).map(esc).join(" · ")}</p></div>`).join("")}`;
  }
  function viewLibrary(view) {
    view.innerHTML = `<h1>Reference Library</h1>
      <table class="table"><thead><tr><th>Title</th><th>Provider</th><th>Type</th><th>Stage</th><th>Cost</th><th>Verified</th></tr></thead><tbody>
      ${(DE.refs||[]).map(r=>`<tr><td><a href="${esc(r.url)}" target="_blank" rel="noopener">${esc(r.title)}</a><div class="muted">${esc(r.why||"")}</div></td>
      <td>${esc(r.provider)}</td><td>${esc(r.type)}</td><td>${esc(r.stage)}</td><td>${esc(r.cost)}</td><td>${esc(r.verified)}</td></tr>`).join("")}
      </tbody></table>`;
  }
  function viewBooks(view) {
    view.innerHTML = `<h1>Books</h1>${(DE.books||[]).map(b=>`<div class="card" style="margin:8px 0">
      <h3>${esc(b.title)}</h3><p>${esc(b.why)}</p><p>Month ${b.month} · ${esc(b.priority)} · Chapters: ${esc(b.chapters||"")}</p>
      ${b.outdated?`<p class="exp">Mark as version-sensitive / potentially dated.</p>`:""}</div>`).join("")}`;
  }
  function viewGlossary(view) {
    view.innerHTML = `<h1>Glossary (${(DE.glossary||[]).length})</h1>
      <input id="gq" placeholder="Search terms..." /><div id="glist"></div>`;
    const draw = () => {
      const q = ($("#gq").value||"").toLowerCase();
      $("#glist").innerHTML = (DE.glossary||[]).filter(g=>!q || g.term.toLowerCase().includes(q) || g.simple.toLowerCase().includes(q)).slice(0,80).map(g=>`
        <div class="acc"><button>${esc(g.term)}</button><div class="body">
          <p><strong>Simple:</strong> ${esc(g.simple)}</p>
          <p><strong>Technical:</strong> ${esc(g.technical)}</p>
          <p><strong>Example:</strong> ${esc(g.example)}</p>
          <p><strong>Related:</strong> ${esc((g.related||[]).join(", "))}</p>
        </div></div>`).join("");
      bindAcc(view);
    };
    $("#gq").oninput = draw; draw();
  }
  function viewCerts(view) {
    const r = readiness();
    view.innerHTML = `<h1>Certification Tracker</h1>
      <div class="disclaimer">This system maps official objectives. It is not an official practice exam and does not guarantee a pass.</div>
      <div class="grid cards-2">
        <div class="card"><h3>Databricks Data Engineer Associate</h3>
          <p>Exam version: on/after 4 May 2026 · 45 scored items · 90 minutes · USD 200</p>
          <p>Readiness: ${r.pct}%</p>
          ${(DE.dbxBlueprint||[]).map(s=>`<div><strong>${esc(s.name)} (${s.weight})</strong><div class="muted">${esc(s.objectives.join(" | "))}</div></div>`).join("")}
        </div>
        <div class="card"><h3>DP-700 Fabric Data Engineer Associate</h3>
          <p>Skills measured as of 21 Jul 2026 · ~100 minutes · pass score 700</p>
          ${(DE.dp700Blueprint||[]).map(s=>`<div><strong>${esc(s.name)} (${s.weight})</strong><div class="muted">${esc(s.objectives.join(" | "))}</div></div>`).join("")}
        </div>
      </div>
      <h3>Am I Ready for DP-700?</h3>
      <p>${r.pct>=85?"Practice metrics suggest you may schedule official Microsoft practice assessment next.":"Keep drilling weak domains, complete Fabric projects, and retake mocks."}</p>`;
  }
  function viewChangelog(view) {
    view.innerHTML = `<h1>Certification Change Log</h1>${(DE.changelog||[]).map(c=>`
      <div class="card" style="margin:8px 0"><strong>${esc(c.date)}</strong> · ${esc(c.exam)}<p>${esc(c.change)}</p><p class="muted">Impact: ${esc(c.impact)}</p></div>`).join("")}`;
  }
  function viewProgress(view) {
    const L = lessons();
    view.innerHTML = `<h1>Progress Tracker</h1>
      <table class="table"><tr><th>Lesson</th><th>Status</th><th>Month</th></tr>
      ${L.map(l=>`<tr><td>${esc(l.title)}</td><td>${S.completed[l.id]?"Completed":S.inProgress[l.id]?"In progress":"Not started"}</td><td>${l.month}</td></tr>`).join("")}</table>`;
  }
  function viewPlan(view) {
    view.innerHTML = `<h1>180-Day Study Plan</h1>
      <p>Weekdays 1–1.5h · Weekends 3–4h · 12–14h/week</p>
      ${(days()||[]).map(d=>`
        <div class="day-row">
          <div>Day ${d.n}</div>
          <div><strong>${esc(d.topic)}</strong><div class="muted">${esc(d.sub)} · ${esc(d.task)} · Quiz ${esc(d.quiz||"")} · ${d.hours}h</div>
            <input placeholder="Notes" data-dn="${d.n}" value="${esc(S.dayNotes[d.n]||"")}" />
          </div>
          <div>${esc(d.read||"")}</div>
          <input type="checkbox" data-dd="${d.n}" ${S.dayDone[d.n]?"checked":""} />
        </div>`).join("")}`;
    view.querySelectorAll("[data-dd]").forEach(c=>c.onchange=()=>{S.dayDone[c.dataset.dd]=c.checked; save();});
    view.querySelectorAll("[data-dn]").forEach(c=>c.onchange=()=>{S.dayNotes[c.dataset.dn]=c.value; save();});
  }
  function viewWeekly(view) {
    view.innerHTML = `<h1>Weekly Reviews</h1>${(DE.weeks||[]).map(w=>`
      <div class="acc"><button>Week ${w.n} · ${esc(w.title)}</button><div class="body">
        <p><strong>Learned:</strong> ${esc(w.learned)}</p>
        <p><strong>Remember:</strong> ${esc(w.remember)}</p>
        <p><strong>Coding:</strong> ${esc(w.code)}</p>
        <p><strong>Architecture:</strong> ${esc(w.arch)}</p>
        <p><strong>Interview:</strong> ${esc(w.interview)}</p>
        <p><strong>Mini-project:</strong> ${esc(w.mini)}</p>
        <p><strong>Next week:</strong> ${esc(w.next)}</p>
      </div></div>`).join("")}`;
    bindAcc(view);
  }
  function viewMonthly(view) {
    view.innerHTML = `<h1>Monthly Assessments</h1>
      <p>A month cannot be marked complete below 80%.</p>
      ${[1,2,3,4,5,6].map(m=>`<div class="card" style="margin:8px 0"><h3>Month ${m} exam (50 questions)</h3>
        <p>Best score: ${S.monthly[m]||0}%</p>
        <button class="btn primary" data-m="${m}">Start</button></div>`).join("")}
      <div id="mex"></div>`;
    view.querySelectorAll("[data-m]").forEach(b=>b.onclick=()=>{
      const m = +b.dataset.m;
      const qs = shuffle(quizzes().filter(q=>q.month===m)).slice(0,50);
      const box = $("#mex");
      box.innerHTML = `<h3>Month ${m}</h3><div class="quiz-set">${qs.map((q,i)=>renderQ(q,i)).join("")}<button class="btn primary" data-grade>Submit</button><div class="result"></div></div>`;
      bindQuiz(box);
      const g = $("[data-grade]", box);
      const old = g.onclick;
      g.onclick = () => {
        old();
        const mct = /Score \d+\/\d+ \((\d+)%\)/.exec($(".result", box).textContent||"");
        if (mct) {
          const pct = +mct[1];
          S.monthly[m] = Math.max(S.monthly[m]||0, pct);
          if (pct < 80) $(".result", box).innerHTML += `<p class="exp">Score below 80%. Month remains incomplete. Revise weak topics and retake.</p>`;
          else $(".result", box).innerHTML += `<p class="easy">Month ${m} assessment passed (≥80%).</p>`;
          save();
        }
      };
    });
  }
  function viewQlik(view) {
    view.innerHTML = `<h1>From Qlik Developer to Modern Data Engineer</h1>
      <table class="table"><tr><th>Existing skill</th><th>Modern equivalent</th><th>Similarity</th><th>Difference</th><th>When to use</th><th>Example</th></tr>
      ${(DE.qlikBridge||[]).map(r=>`<tr><td>${esc(r.from)}</td><td>${esc(r.to)}</td><td>${esc(r.sim)}</td><td>${esc(r.diff)}</td><td>${esc(r.when)}</td><td>${esc(r.ex)}</td></tr>`).join("")}
      </table>`;
  }
  function viewCareer(view) {
    view.innerHTML = `<h1>Job Readiness</h1>${(DE.roles||[]).map(r=>`<div class="card" style="margin:8px 0">
      <h3>${esc(r.title)}</h3>
      <p><strong>You already have:</strong> ${esc(r.have)}</p>
      <p><strong>Need:</strong> ${esc(r.need)}</p>
      <p><strong>Certs:</strong> ${esc(r.certs)}</p>
      <p><strong>Projects:</strong> ${esc(r.projects)}</p>
      <p><strong>Interview:</strong> ${esc(r.interview)}</p></div>`).join("")}`;
  }
  function viewFreelance(view) {
    view.innerHTML = `<h1>Freelancing &amp; Consulting</h1>${(DE.freelance||[]).map(f=>`
      <div class="acc"><button>${esc(f.title)}</button><div class="body">
        ${Object.entries(f).filter(([k])=>k!=="title").map(([k,v])=>`<p><strong>${esc(k)}:</strong> ${esc(typeof v==="string"?v:JSON.stringify(v))}</p>`).join("")}
      </div></div>`).join("")}`;
    bindAcc(view);
  }
  function viewSimulator(view) {
    const rounds = DE.simRounds || [];
    view.innerHTML = `<h1>Senior Data Engineer Interview Simulator</h1>
      ${rounds.map((r,i)=>`<div class="card" style="margin:8px 0"><h3>Round ${i+1}: ${esc(r.name)}</h3>
        <p>${esc(r.prompt)}</p>
        <textarea class="note" id="ans${i}"></textarea>
        <button class="btn primary" data-r="${i}">Self-score</button>
        <div id="sc${i}"></div></div>`).join("")}`;
    view.querySelectorAll("[data-r]").forEach(b=>b.onclick=()=>{
      const i = +b.dataset.r;
      const text = $("#ans"+i).value.trim();
      const r = rounds[i];
      const scores = rubric(text, r);
      S.interviewScores[i] = scores;
      save();
      $("#sc"+i).innerHTML = Object.entries(scores).map(([k,v])=>`<span class="chip">${esc(k)}: ${v}/10</span>`).join(" ");
    });
  }
  function rubric(text, r) {
    const t = text.toLowerCase();
    const hit = (kws) => Math.min(10, 3 + kws.filter(k=>t.includes(k)).length * 1.4);
    return {
      "Technical accuracy": hit(r.keywords||[]),
      "Depth": Math.min(10, Math.round(text.length/80)),
      "Architecture thinking": hit(["trade-off","scale","cost","security","governance","latency"]),
      "Communication": text.length>120?8:4,
      "Business understanding": hit(["kpi","revenue","risk","customer","sla","compliance"])
    };
  }
  function viewBootcamp(view) {
    view.innerHTML = `<h1>30-Day Certification Bootcamp</h1>
      <div class="tabs"><button class="on" data-b="dbx">Databricks</button><button data-b="dp">DP-700</button></div>
      <div id="bc"></div>`;
    const draw = (k) => {
      $("#bc").innerHTML = (DE.bootcamp||[]).filter(d=>d.exam===k).map(d=>`
        <div class="day-row"><div>Day ${d.day}</div><div><strong>${esc(d.focus)}</strong><div class="muted">${esc(d.tasks)}</div></div><div>${d.hours}h</div><div></div></div>`).join("");
    };
    draw("dbx");
    $$(".tabs button", view).forEach(b=>b.onclick=()=>{$$(".tabs button", view).forEach(x=>x.classList.remove("on")); b.classList.add("on"); draw(b.dataset.b);});
  }
  function viewCodeLabs(view) {
    view.innerHTML = `<h1>Code Labs</h1>${(DE.codeLabs||[]).map(c=>`
      <div class="acc"><button>${esc(c.title)} · ${esc(c.lang)}</button><div class="body">
        <p>${esc(c.problem)}</p><pre>${esc(c.starter)}</pre>
        <p><strong>Expected:</strong> ${esc(c.expected)}</p>
        <p><strong>Hint:</strong> ${esc(c.hint)}</p>
        <details><summary>Solution</summary><pre>${esc(c.solution)}</pre><p>${esc(c.explain)}</p></details>
        <p><strong>Challenge:</strong> ${esc(c.challenge)}</p>
      </div></div>`).join("")}`;
    bindAcc(view);
  }
  function viewDebug(view) {
    view.innerHTML = `<h1>Debugging Lab (${(DE.debugLabs||[]).length})</h1>${(DE.debugLabs||[]).map(d=>`
      <div class="acc"><button>${esc(d.title)}</button><div class="body">
        <pre>${esc(d.broken)}</pre>
        <p>${esc(d.prompt)}</p>
        <details><summary>Diagnosis</summary><p>${esc(d.why)}</p><pre>${esc(d.fix)}</pre></details>
      </div></div>`).join("")}`;
    bindAcc(view);
  }
  function viewArch(view) {
    view.innerHTML = `<h1>Architecture Decision Lab (${(DE.archLabs||[]).length})</h1>${(DE.archLabs||[]).map(a=>`
      <div class="card" style="margin:10px 0"><h3>${esc(a.title)}</h3>
        <p>${esc(a.scenario)}</p>
        <p>Choose stack:</p>
        ${(a.choices||[]).map((c,i)=>`<button class="q-opt" data-a="${a.id}" data-i="${i}">${esc(c)}</button>`).join("")}
        <div id="ar${a.id}"></div>
      </div>`).join("")}`;
    view.querySelectorAll("[data-a]").forEach(b=>b.onclick=()=>{
      const a = (DE.archLabs||[]).find(x=>x.id===b.dataset.a);
      $(`#ar${a.id}`).innerHTML = `<p><strong>Ideal:</strong> ${esc(a.ideal)}</p><p>${esc(a.explain)}</p><p><strong>Trade-offs:</strong> ${esc(a.tradeoffs)}</p>`;
    });
  }
  function viewScenarios(view) {
    view.innerHTML = `<h1>Enterprise Scenarios (${(DE.scenarios||[]).length})</h1>${(DE.scenarios||[]).map(s=>`
      <div class="acc"><button>${esc(s.industry)} · ${esc(s.title)}</button><div class="body">
        <p>${esc(s.story)}</p><p><strong>Need:</strong> ${esc(s.need)}</p>
        <p><strong>Question:</strong> ${esc(s.ask)}</p>
        <details><summary>Recommended architecture</summary>
          <p>${esc(s.why)}</p><p>Alternatives: ${esc(s.alts)}</p>
          <p>Trade-offs: ${esc(s.tradeoffs)}</p>
          <p>Cost: ${esc(s.cost)} · Perf: ${esc(s.perf)} · Security: ${esc(s.sec)} · Governance: ${esc(s.gov)} · Scale: ${esc(s.scale)}</p>
        </details>
      </div></div>`).join("")}`;
    bindAcc(view);
  }
  function viewBookmarks(view) {
    view.innerHTML = `<h1>My Bookmarks</h1>${S.bookmarks.map(b=>`<div class="search-hit" data-go="${b.type==="lesson"?"lesson/"+b.id:b.id}">${esc(b.title)}</div>`).join("") || "<p>None yet.</p>"}`;
  }

  function bindAcc(root) {
    $$(".acc > button", root).forEach((b) => b.onclick = () => b.parentElement.classList.toggle("open"));
  }

  function searchAll(q) {
    q = q.toLowerCase();
    if (q.length < 2) return [];
    const hits = [];
    lessons().forEach(l => { if ((l.title+l.topic+(l.simple||"")).toLowerCase().includes(q)) hits.push({go:`lesson/${l.id}`, title:`Lesson: ${l.title}`}); });
    quizzes().slice(0,800).forEach(x => { if ((x.stem+x.topic).toLowerCase().includes(q)) hits.push({go:`quizzes/${x.bank||"core"}`, title:`Quiz: ${x.stem.slice(0,80)}`}); });
    (DE.projects||[]).forEach(p => { if ((p.title+(p.problem||"")).toLowerCase().includes(q)) hits.push({go:"projects", title:`Project: ${p.title}`}); });
    (DE.interview||[]).forEach(i => { if ((i.q+i.topic).toLowerCase().includes(q)) hits.push({go:"interview", title:`Interview: ${i.q}`}); });
    (DE.glossary||[]).forEach(g => { if (g.term.toLowerCase().includes(q)) hits.push({go:"glossary", title:`Glossary: ${g.term}`}); });
    (DE.cheats||[]).forEach(c => { if (c.title.toLowerCase().includes(q)) hits.push({go:"cheats", title:`Cheat sheet: ${c.title}`}); });
    (DE.diagrams||[]).forEach(d => { if (d.title.toLowerCase().includes(q)) hits.push({go:"diagrams", title:`Diagram: ${d.title}`}); });
    (DE.refs||[]).forEach(r => { if (r.title.toLowerCase().includes(q)) hits.push({go:"library", title:`Ref: ${r.title}`}); });
    return hits.slice(0, 40);
  }

  document.body.addEventListener("click", (e) => {
    const t = e.target.closest("[data-go]");
    if (t && t.dataset.go) { e.preventDefault(); go(t.dataset.go); }
  });
  $("#navFilter").oninput = renderNav;
  $("#themeBtn").onclick = () => {
    S.theme = S.theme === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = S.theme === "light" ? "light" : "";
    save();
  };
  document.documentElement.dataset.theme = S.theme === "light" ? "light" : "";
  $("#globalSearch").oninput = () => {
    const hits = searchAll($("#globalSearch").value);
    if (!$("#globalSearch").value) return;
    const modal = $("#modal"); const box = $("#modalBox");
    box.innerHTML = `<h3>Search</h3>${hits.map(h=>`<div class="search-hit" data-go="${h.go}">${esc(h.title)}</div>`).join("")||"<p>No hits</p>"}`;
    modal.classList.add("on");
    modal.onclick = (e) => { if (e.target === modal) modal.classList.remove("on"); };
  };
  $("#bookmarkNav").onclick = () => go("bookmarks");
  window.addEventListener("hashchange", route);
  renderNav();
  route();
})();
