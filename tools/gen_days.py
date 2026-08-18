#!/usr/bin/env python3
import json, sys
sys.path.insert(0, "/workspace/tools")
from jsdump import dump

days = []
plan = [
    (1, 1, 30, "Foundations", [
        "Orientation + as-is Qlik map","Python venv, pathlib, logging","Functions, APIs, JSON","Pandas landing & cleaning",
        "SQL joins/CTE review","Window functions + MERGE","ETL vs ELT vs lakehouse","CDC + SCD1/2",
        "Git + repo layout","DQ + governance","Python packaging","ApplyMap-style dicts",
        "Star schema design","Batch vs stream","File formats","Nested JSON flatten",
        "Pipeline tests","E-comm project kickoff","Weekly review 1","SQL optimization",
        "Incremental design lab","Python API pagination","Pandas vs Spark boundary","Data contracts",
        "Lineage thinking","E-comm bronze landing","E-comm silver rules","E-comm gold star",
        "Monthly exam prep","Month 1 assessment (80% gate)"]),
    (2, 31, 60, "Spark", [
        "Spark architecture","RDD vs DF","Lazy eval","DF transformations","Joins & broadcast",
        "Aggregations","Windows","UDF pitfalls","Partitions","Repartition vs coalesce",
        "Shuffle internals","Skew & AQE","Caching","Spark SQL","JDBC/IO",
        "Structured Streaming intro","Watermarks","Perf checklist","Spark UI reading","Debug OOM",
        "Rewrite Qlik transform 1","Rewrite Qlik transform 2","Streaming lab","Perf lab",
        "Weekly architecture challenge","Code lab marathon","Debug lab","Interview Spark",
        "Month 2 review","Month 2 assessment"]),
    (3, 61, 90, "Databricks", [
        "Platform walkthrough","Compute & cost","Delta ACID/time travel","MERGE/UPDATE/DELETE","Schema enforcement/evolution",
        "Medallion interactive","Auto Loader","COPY INTO","Lakeflow Connect","Declarative pipelines",
        "Lakeflow Jobs DAG","Triggers","Gold objects","UC grants","Managed vs external",
        "RLS/masks","ABAC","Git Folders","DAB variables","CLI deploy",
        "Spark UI on DBx","Liquid clustering","Predictive optimization","DQ expectations","Retail medallion project",
        "Healthcare PHI design","Jobs failure drills","Weekly review","Integration lab","Month 3 assessment"]),
    (4, 91, 120, "DBx Cert", [
        "Blueprint map section 1-2","Blueprint 3-4","Blueprint 5-7","Practice set Easy","Practice Medium",
        "Practice Hard","Scenario set","Mock exam 1","Weak domain ingest","Weak transform",
        "Weak jobs","Weak CI/CD","Weak gov","Mock exam 2","Spark UI drills",
        "Connect vs Auto Loader matrix","DAB lab","UC privilege lab","Mock exam 3","Review mistakes",
        "Interview DBx senior","Architecture lab","Bootcamp days 1-4","Bootcamp 5-8","Bootcamp 9-12",
        "Mock exam 4","Mock exam 5","Readiness score review","Light labs","Month 4 assessment"]),
    (5, 121, 150, "Fabric", [
        "Fabric + OneLake","Workspaces/domains","Lakehouse + SQL endpoint","Shortcuts","Warehouse T-SQL",
        "Dimensional load","Pipelines","Parameters/triggers","Dataflows Gen2","When not to Dataflow",
        "Mirroring","Eventstreams","Eventhouse + KQL","Windowing","Spark in Fabric",
        "Airflow","Security stack","OneLake security","Git + deploy pipes","Database projects",
        "Monitoring","Error labs","Perf lakehouse","Perf warehouse","Retail Fabric project",
        "Banking mirroring design","RTI lab","Weekly review","Integration","Month 5 assessment"]),
    (6, 151, 180, "DP-700+GenAI", [
        "DP-700 D1 drill","D2 drill","D3 drill","Practice beginner","Intermediate",
        "Advanced/expert","Scenario fabric","Mock DP 1","Weak security","Weak streaming",
        "Weak optimize","Mock DP 2","LLM/tokens","Prompt + NL2SQL","Embeddings + RAG",
        "Chunking/rerank","Tools/function calling","Agents/LangGraph","AI gov/eval","AI analytics patterns",
        "Capstone architecture","Capstone ingest","Capstone gold+semantic","Capstone agent","Mock DP 3",
        "Mock DP 4","Mock DP 5","Am I ready DP-700","Portfolio polish","Final interview simulator + freelance kit"]),
]
n = 1
for month, start, end, theme, topics in plan:
    for i, topic in enumerate(topics):
        weekend = (n % 7 in (6, 0))
        hours = 3.5 if weekend else 1.25
        days.append({
            "n": n, "month": month, "date": f"Day {n} (set your start date; default program day {n})",
            "topic": topic, "sub": theme, "read": "Official docs in Reference Library",
            "task": f"Hands-on: {topic} — code or architecture artifact in repo",
            "quiz": f"8 questions tagged {theme}", "hours": hours,
            "video": "Prefer official Academy/Microsoft Learn over random YouTube"
        })
        n += 1

weeks = []
for w in range(1, 27):
    weeks.append({
        "n": w,
        "title": ["Foundations","SQL/modeling","Git/DQ","Spark core","Spark perf","Streaming",
                  "Delta/medallion","Lakeflow","UC/CI","Cert drills","Mocks","Weak topics",
                  "Fabric core","RTI/security","Fabric ops","DP-700","GenAI","Capstone",
                  "Mocks","Portfolio","Interview","Freelance","Polish","Cert boot","Capstone AI","Close"][(w-1)%26],
        "learned": f"Week {w} objectives from the 180-day plan.",
        "remember": "Grain, incremental keys, governance, cost.",
        "code": "Complete the week's code lab + one debug item.",
        "arch": "One architecture challenge (see Architecture Lab).",
        "interview": "10 senior/architect questions from this week's topic.",
        "mini": "Ship a markdown ADR + diagram.",
        "next": "Preview next week's official docs; schedule 12-14 hours."
    })

dump("days.js", {"days": days, "weeks": weeks})
print("days", len(days))
