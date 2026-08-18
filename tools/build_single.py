#!/usr/bin/env python3
"""Bundle CSS + data + engine into a single index.html that works via double-click."""
from pathlib import Path

ROOT = Path("/workspace")
css = (ROOT / "css/app.css").read_text(encoding="utf-8")
js_parts = []
for name in [
    "meta.js", "lessons.js", "days.js", "quizzes.js", "flashcards.js",
    "interview.js", "projects.js", "scenarios.js", "glossary.js", "refs.js",
    "labs.js", "career.js",
]:
    js_parts.append((ROOT / "js/data" / name).read_text(encoding="utf-8"))
js_parts.append((ROOT / "js/engine.js").read_text(encoding="utf-8"))
js = "\n".join(js_parts).replace("</", "<\\/")

html = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>PathForge — 6-Month Data Engineering + Databricks + Fabric + GenAI</title>
  <style>
__CSS__
  .boot { padding: 24px; max-width: 720px; }
  </style>
</head>
<body>
  <div class="app">
    <aside class="sidebar">
      <div class="brand">
        <h1>PathForge SSOT</h1>
        <p>Qlik → Data Engineer → Data &amp; AI Architect</p>
      </div>
      <div class="side-search"><input id="navFilter" placeholder="Filter nav..." /></div>
      <nav class="nav" id="nav"></nav>
    </aside>
    <section class="main">
      <header class="topbar">
        <input id="globalSearch" class="grow" placeholder="Search lessons, quizzes, projects, glossary, interview Qs..." />
        <button class="icon-btn" id="themeBtn" title="Toggle theme">Theme</button>
        <button class="icon-btn" id="bookmarkNav">Bookmarks</button>
        <button class="btn primary" data-go="dashboard">Dashboard</button>
      </header>
      <main class="content" id="view">
        <div class="boot card">
          <h1>Loading PathForge…</h1>
          <p>This is a single-file app. If this message remains, JavaScript is blocked. Enable JS, or save/download this file and open it locally (GitHub’s file viewer will not run the app).</p>
        </div>
      </main>
    </section>
  </div>
  <div class="modal" id="modal"><div class="box" id="modalBox"></div></div>
  <noscript><div class="boot card" style="padding:24px"><h1>JavaScript required</h1><p>PathForge is an interactive app. Enable JavaScript and reopen this file.</p></div></noscript>
  <script>
__JS__
  </script>
</body>
</html>
"""
out = ROOT / "index.html"
out.write_text(html.replace("__CSS__", css).replace("__JS__", js), encoding="utf-8")
print("wrote", out, out.stat().st_size)
