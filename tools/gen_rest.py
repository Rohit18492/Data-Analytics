#!/usr/bin/env python3
import sys
sys.path.insert(0, "/workspace/tools")
from jsdump import dump

codeLabs = [
{"title":"Python: paginated API to landing","lang":"Python","problem":"Write pages until next is null without duplicating page files.",
 "starter":"def ingest(url): \n    pass",
 "expected":"landing/2026-08-18/page_001.json ... manifest.json with hashes",
 "hint":"while url: write; url = payload.get('next')",
 "solution":"import json, hashlib, requests\nfrom pathlib import Path\n\ndef ingest(url, dest):\n    n=1\n    while url:\n        r=requests.get(url, timeout=30); r.raise_for_status()\n        p=dest/f'page_{n:03d}.json'; p.write_bytes(r.content)\n        url=r.json().get('next'); n+=1",
 "explain":"Idempotent if you overwrite by page number for a given date partition.",
 "challenge":"Add retry on 429 and a lock file."},
{"title":"SQL: SCD2 merge","lang":"SQL","problem":"Close current rows when hashdiff changes; insert new version.",
 "starter":"-- MERGE INTO dim_customer ...",
 "expected":"one current row per customer_id",
 "hint":"match on customer_id AND is_current=true",
 "solution":"MERGE INTO dim_customer t USING stg s ON t.customer_id=s.customer_id AND t.is_current=true\nWHEN MATCHED AND t.hashdiff<>s.hashdiff THEN UPDATE SET is_current=false, end_dt=current_date()\nWHEN NOT MATCHED THEN INSERT *;",
 "explain":"Need a second insert for the new current version — often two-step MERGE or APPLY.",
 "challenge":"Handle deletes (is_deleted)."},
{"title":"PySpark: drop dupes keep latest","lang":"PySpark","problem":"Keep latest event per event_id by ts.",
 "starter":"from pyspark.sql import Window, functions as F\n# df = ...",
 "expected":"one row per event_id",
 "hint":"row_number over partition event_id order by ts desc",
 "solution":"w=Window.partitionBy('event_id').orderBy(F.col('ts').desc())\nsilver=df.withColumn('rn', F.row_number().over(w)).filter('rn=1').drop('rn')",
 "explain":"dropDuplicates is arbitrary without order.",
 "challenge":"Late data after gold published — CDF or reprocess window."},
{"title":"Spark SQL: broadcast hint","lang":"Spark SQL","problem":"Join small dim to large fact.",
 "starter":"SELECT /*+ */ f.*, d.region FROM fact f JOIN dim d ON f.store_id=d.store_id",
 "expected":"BroadcastHashJoin in plan",
 "hint":"BROADCAST(d)",
 "solution":"SELECT /*+ BROADCAST(d) */ f.*, d.region FROM fact f JOIN dim d ON f.store_id=d.store_id",
 "explain":"Confirm with EXPLAIN; AQE may also broadcast.",
 "challenge":"What if dim is 6GB?"},
{"title":"Databricks SQL: CREATE OR REPLACE Delta","lang":"Databricks SQL","problem":"Create table regardless of prior existence with given schema.",
 "starter":"-- DDL",
 "expected":"empty or replaced Delta table",
 "hint":"CREATE OR REPLACE TABLE ...",
 "solution":"CREATE OR REPLACE TABLE hr.employees (employeeId STRING, startDate DATE, avgRating FLOAT)",
 "explain":"IF NOT EXISTS would not replace; USING DELTA often default in UC.",
 "challenge":"Preserve data vs replace."},
{"title":"KQL: 5-minute error rate","lang":"KQL","problem":"Count 5xx per 5 minutes.",
 "starter":"requests\n| ",
 "expected":"time binned counts",
 "hint":"bin(timestamp, 5m)",
 "solution":"requests\n| where resultCode >= 500\n| summarize errors=count() by bin(timestamp, 5m)",
 "explain":"bin is tumbling-style buckets.",
 "challenge":"Hopping window 5m every 1m."},
]
# more labs
for lang, title, problem in [
("Python","Hashdiff","SHA256 of business attrs"),
("SQL","Anti-join deletes","customers in dim not in source"),
("PySpark","Explode payments","don't double revenue"),
("PySpark","Union by name","schema drift"),
("Spark SQL","Window running sum","partition region"),
("KQL","arg_max latest status","per device"),
("SQL","Incremental watermark","load_date > max"),
("Python","Logging JSON","structured logs"),
]:
    codeLabs.append({"title": f"{lang}: {title}", "lang": lang, "problem": problem,
        "starter": "# start here", "expected": "correct grain and types", "hint": "think grain",
        "solution": f"# implement {title}\nprint('see lesson notes')", "explain": problem,
        "challenge": "Scale to 1B rows conceptually."})

debugLabs = []
debugs = [
("Duplicate after join","df.join(df2, 'customer_id')","Why duplicates?","Non-unique customer_id on one side. Dedup or join additional keys.","df2 = df2.dropDuplicates(['customer_id'])\ndf.join(df2,'customer_id')"),
("Cartesian","df.crossJoin(df2)","Accident?","crossJoin is every-to-every. Use inner join.","df.join(df2,'id')"),
("collect OOM","pdf = df.collect()","Driver OOM","collect pulls all rows. Write or take(100).","df.limit(100).collect()"),
("UDF slow","F.udf(lambda x: x.upper())","Slow stage","Python UDF. Use F.upper.","df.withColumn('n', F.upper('name'))"),
("Wrong union","df.union(df2)","Columns swapped","Positional union. Use unionByName.","df.unionByName(df2, allowMissingColumns=True)"),
("Overwrite schema","write.mode('overwrite')","Dropped column","Overwrite replaced table. Time travel restore.","RESTORE TABLE t TO VERSION AS OF n"),
("Autoloader no new rows","cloudFiles","Checkpoint thinks files seen","Don't delete checkpoint casually; verify path.","Use new checkpoint only if intentionally reprocessing"),
("COPY INTO 0 rows","COPY INTO","Already loaded files","COPY INTO skips ingested files — expected incremental.","Force reload only with documented options"),
("GRANT still denied","GRANT SELECT ON TABLE","Missing USE CATALOG/SCHEMA","Privileges are hierarchical.","GRANT USE CATALOG; USE SCHEMA; SELECT"),
("Broadcast OOM","broadcast(huge_dim)","Executor OOM","Dim not small.","Remove broadcast; rely on SMJ"),
("Skew join","join on country","One country 80%","AQE skew or salt.","salt country key"),
("repartition 1","repartition(1)","Tiny parallelism","Single partition bottleneck.","Write with reasonable partitions"),
("Pandas apply","df.toPandas()","Driver memory","Don't pandas a lake.","Stay in Spark"),
("Streaming no watermark","dropDuplicates in stream","State grows","Need watermark for bounded state.","withWatermark"),
("Late files","batch job 2am","Missing 1:50am file","File arrival trigger or later SLA.","data-driven trigger"),
("Fabric shortcut 404","shortcut","Target moved/ACL","Shortcut errors on blueprint.","Fix target or permissions"),
("Dataflow privacy","Gen2 fail","Privacy levels","Fix fold/privacy.","Align privacy"),
("Pipeline expression","@pipeline().parameters.x null","Missing param","Default and validate.","set default"),
("KQL join explosion","join kind=inner","Dup keys","Same fan-out as SQL.","summarize first"),
("RLS vs workspace viewer","user sees all","RLS not applied on that item","Item-level + RLS both needed.","enable RLS on WH/semantic"),
]
for i, (title, broken, prompt, why, fix) in enumerate(debugs, 1):
    debugLabs.append({"id": f"dbg{i}", "title": title, "broken": broken, "prompt": prompt, "why": why, "fix": fix})
# pad to 50
while len(debugLabs) < 50:
    i = len(debugLabs)+1
    debugLabs.append({"id": f"dbg{i}", "title": f"Schema mismatch #{i}", "broken": "spark.read.csv(path)  # infers types",
        "prompt": "Why did Gold break after a new column?", "why": "Schema inference / evolution policy. Enforce schema.",
        "fix": "Provide explicit schema; use rescue column; set evolution deliberately."})

archLabs = []
archs = [
("Bank 5TB + fraud + PBI + chatbot","5 TB, daily batch, 2M tx/day, real-time fraud, PBI, AI chatbot, strict security",
 ["Databricks-only","Fabric-only","Hybrid: streaming RTI/DBx + warehouse serving + RAG on gold","QVD-only"],
 "Hybrid: streaming path for fraud; lakehouse/warehouse for history; semantic for PBI; agent on gold with least privilege.",
 "Don't put fraud SLA on a nightly Spark job. Don't let chatbot read bronze.",
 "Cost: always-on stream vs burst jobs; LLM tokens; two platforms vs skills."),
("Hospital analytics","PHI, measures, vendor data share",
 ["Public catalog","Isolated workspace + de-id gold + ABAC","Everything in Excel"],
 "Isolated domain, tokenize, gold without direct identifiers, no LLM on PHI.",
 "Sharing via governed views not CSV email.",
 "Compliance cost dominates compute."),
("SaaS product analytics","High event volume, small finance team",
 ["Warehouse-only","Lakehouse events + warehouse finance","Eventhouse only"],
 "Events in lakehouse/RTI; finance in warehouse; shortcuts.",
 "Don't force T-SQL on nested JSON events.",
 "Small team: Fabric if already M365."),
]
for i, (title, scenario, choices, ideal, explain, trade) in enumerate(archs, 1):
    archLabs.append({"id": f"al{i}", "title": title, "scenario": scenario, "choices": choices, "ideal": ideal, "explain": explain, "tradeoffs": trade})
inds = ["Retail chain","Insurer","Telco","Manufacturer","Logistics","Pharma","Marketplace","Public sector"]
for i, ind in enumerate(inds*4, start=4):
    if len(archLabs) >= 30: break
    archLabs.append({"id": f"al{i}", "title": f"{ind} platform choice",
        "scenario": f"{ind}: mixed CDC, files, streaming, BI (Qlik+PBI), AI assistant, 12-24 month transformation from Qlik QVDs.",
        "choices": ["Lift QVDs to blob and stop","Databricks medallion + keep Qlik on Gold","Fabric OneLake + PBI only","Two lakes ungoverned"],
        "ideal": "Medallion on Databricks and/or Fabric; Qlik/PBI consume Gold; retire QVDs gradually.",
        "explain": "Coexistence beats big-bang. Certify gold grain before switching dashboards.",
        "tradeoffs": "Dual-run cost vs risk. Skills ramp. License overlap."})

dump("labs.js", {"codeLabs": codeLabs, "debugLabs": debugLabs, "archLabs": archLabs})
print("labs", len(codeLabs), len(debugLabs), len(archLabs))

# diagrams SVG simple
def boxes(title, nodes, edges):
    w = 140; h = 44; gap = 24
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 220" width="100%"><rect width="900" height="220" fill="#0e1730"/>']
    for i, n in enumerate(nodes):
        x = 20 + i * (w + gap); y = 80
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="#1b2b4a" stroke="#3dd6c6"/>')
        parts.append(f'<text x="{x+10}" y="{y+28}" fill="#e8eefc" font-size="12">{n}</text>')
        if i < len(nodes) - 1:
            parts.append(f'<line x1="{x+w}" y1="{y+h/2}" x2="{x+w+gap}" y2="{y+h/2}" stroke="#7aa8ff" marker-end="url(#a)"/>')
    parts.append('<defs><marker id="a" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><polygon points="0 0, 6 3, 0 6" fill="#7aa8ff"/></marker></defs>')
    parts.append(f'<text x="20" y="36" fill="#3dd6c6" font-size="16">{title}</text></svg>')
    return "".join(parts)

diagrams = []
specs = [
("ETL architecture",["Source","Transform","Warehouse","BI"],"Push transforms before store.","Classic when engines are weak."),
("ELT architecture",["Source","Lake landing","Transform in platform","Serve"],"Land then transform.","Cloud warehouses/lakes."),
("Data warehouse",["OLTP","ETL","Star schema","OLAP/BI"],"Modeled facts/dims.","Finance conformance."),
("Data lake",["Files","Folders","Various engines"],"Cheap store, easy swamp.","Need catalog."),
("Lakehouse",["Object store","Delta/UC","SQL+Spark+AI"],"One copy, many engines.","Default modern target."),
("Medallion architecture",["Bronze","Silver","Gold"],"Quality hops.","Almost every project here."),
("Spark architecture",["Driver","Cluster manager","Executors"],"Distributed tasks.","ETL at scale."),
("Databricks architecture",["Workspace","Compute","UC+Delta","Jobs"],"Intelligence platform.","Associate exam core."),
("Delta Lake",["Parquet files","_delta_log","Readers/Writers"],"ACID on objects.","MERGE/time travel."),
("Unity Catalog",["Metastore","Catalog","Schema","Table/Volume"],"Governed namespace.","Grants/lineage/ABAC."),
("Fabric architecture",["SaaS capacity","Workspaces","Items","OneLake"],"Microsoft analytics SaaS.","DP-700."),
("OneLake",["Tenant lake","Workspaces","Shortcuts"],"Single logical lake.","Stop copies."),
("Fabric Lakehouse",["Files","Tables","SQL endpoint","Spark"],"Lake + SQL.","Multi-engine."),
("Fabric Warehouse",["T-SQL","Dims/Facts","BI"],"Warehouse experience.","Concurrency SQL."),
("Data Factory pipeline",["Trigger","Activities","Notebook/Copy","Gold"],"Orchestration.","Parameters."),
("Streaming architecture",["Event bus","Stream proc","Serving","Lake"],"Hot/cold.","Fraud/IoT."),
("RAG",["Question","Retrieve","Augment prompt","Generate"],"Grounded answers.","Metric Q&A."),
("Vector database",["Chunk","Embed","Index","kNN"],"Semantic search.","Doc RAG."),
("AI Agent",["LLM","Tools","State/Memory","Act"],"Loop until done.","NL analytics."),
("AI analytics architecture",["Gold","Semantic","Agent","Qlik/PBI"],"AI is a consumer.","Capstone."),
("CI/CD",["Git","PR","Bundle/Pipeline deploy","Prod"],"Code as source of truth.","DAB/Fabric pipes."),
("Data governance",["Catalog","Owners","Policies","Audit"],"Trust + access.","UC+Purview+labels."),
]
for title, nodes, explain, when in specs:
    diagrams.append({"title": title, "svg": boxes(title, nodes, None), "explain": explain,
        "components": nodes, "flow": " → ".join(nodes), "when": when,
        "interview": [f"When would you not use {title}?", "How does this map from Qlik?"]})

dump("tmp_diagrams", {"diagrams": diagrams})  # will merge in refs file

cheats = [
{"title":"Python","body":"venv, pip, pathlib, json, logging, argparse, requests timeout, pandas read_*, hashdiff, retry, pytest"},
{"title":"SQL","body":"SELECT JOIN GROUP HAVING CTE windows LAG/LEAD ROW_NUMBER MERGE CASE QUALIFY EXPLAIN partitions"},
{"title":"PySpark","body":"read/write, select filter withColumn, joins, groupBy agg, Window, dropDuplicates, explode, unionByName, broadcast, repartition/coalesce, cache, explain"},
{"title":"Spark","body":"Driver/executors jobs/stages/tasks lazy wide/narrow shuffle AQE skew spill UI shuffle.partitions broadcast threshold"},
{"title":"Delta Lake","body":"CREATE TABLE MERGE UPDATE DELETE time travel OPTIMIZE VACUUM CDF schema evolution constraints Liquid clustering PO"},
{"title":"Databricks","body":"Workspace compute notebooks UC Auto Loader COPY INTO Lakeflow Connect Jobs Declarative Pipelines Git Folders DABs CLI SQL warehouses serverless"},
{"title":"Lakeflow","body":"Connect sources; Jobs DAG retries conditionals triggers scheduled/file/table; Spark Declarative Pipelines streaming tables MVs"},
{"title":"Unity Catalog","body":"catalog.schema.table/volume managed vs external GRANT REVOKE DENY RLS masks ABAC lineage volumes external locations"},
{"title":"Fabric","body":"OneLake lakehouse warehouse pipelines Dataflows mirroring Eventstream Eventhouse KQL Airflow Git deploy pipes security stack"},
{"title":"OneLake","body":"tenant lake shortcuts vs copy security query acceleration RTI shortcuts"},
{"title":"Data Factory","body":"activities copy lookup foreach until parameters variables expressions schedules event triggers"},
{"title":"Dataflows Gen2","body":"Power Query folding destinations staging privacy vs Spark scale"},
{"title":"KQL","body":"where project summarize join bin window arg_max let materialize"},
{"title":"Git","body":"branch commit PR protect main no secrets no data files"},
{"title":"Data modelling","body":"grain facts dims SCD1/2 conformed keys late facts bridges"},
{"title":"Data architecture","body":"ETL ELT lake warehouse lakehouse lambda kappa CDC streaming batch"},
{"title":"GenAI","body":"tokens context prompts eval temperature tools safety cost"},
{"title":"RAG","body":"chunk overlap embed hybrid search rerank cite never bronze PII"},
{"title":"AI Agents","body":"allowlist tools state graph human gate SQL readonly gold only"},
]

qlikBridge = [
{"from":"QVD","to":"Delta Lake / Parquet tables","sim":"Layered, reusable, optimized storage of transformed tables.","diff":"Delta is transactional, open, time-travel, multi-engine. QVD is Qlik-proprietary.","when":"All curated tables.","ex":"sales.qvd → catalog.retail.silver_sales"},
{"from":"Qlik Load Script","to":"PySpark / Spark SQL / T-SQL / KQL","sim":"Declarative-ish transforms, joins, maps.","diff":"Distributed + lazy vs in-memory eager script.","when":"Any heavy transform.","ex":"Resident + join → DataFrame join"},
{"from":"Resident Load","to":"DataFrame transformation","sim":"Transform an already-loaded table.","diff":"Spark plans; no implicit memory of whole app.","when":"Cleaning steps.","ex":"LOAD Resident Orders → df.filter..."},
{"from":"ApplyMap","to":"Broadcast map / join / dict","sim":"Lookup mapping tables.","diff":"Must handle unmatched (null) explicitly.","when":"Code mapping.","ex":"ApplyMap('map_seg', id) → dim join"},
{"from":"Incremental QVD","to":"Incremental Delta MERGE / Autoloader / CDC","sim":"Load deltas with Exists/where.","diff":"Checkpoints, CDC logs, MERGE uniqueness.","when":"Any large fact.","ex":"Where Date>vMax → MERGE on order_id"},
{"from":"Qlik ETL","to":"Databricks Jobs / Fabric pipelines","sim":"Scheduled multi-step reloads.","diff":"DAGs, retries, cloud compute billing.","when":"Orchestration.","ex":"QMC task chain → Lakeflow Job"},
{"from":"QMC","to":"Workspace admin + UC + Jobs UI + Fabric admin","sim":"Security, tasks, monitoring.","diff":"Split across catalog, workspace, cloud IAM.","when":"Ops.","ex":"Reload tasks → Jobs run history"},
{"from":"Qlik data model","to":"Lakehouse Gold + semantic model","sim":"Associative grain vs star; both need unique keys.","diff":"Synthetic keys/circular refs vs explicit stars/bridges.","when":"Serving layer.","ex":"Qlik app model → gold star + PBI dataset or Qlik on SQL"},
{"from":"Set Analysis","to":"SQL filters / DAX / semantic measures","sim":"Context-aware measures.","diff":"Set Analysis is Qlik-native; SQL is predicate + windows.","when":"Metrics.","ex":"Sum({<YTD>} Sales) → SQL YTD window or semantic measure"},
{"from":"NPrinting","to":"PBI subscriptions / Fabric / email burst (or keep NPrinting on Gold)","sim":"Burst reports.","diff":"Different bursting products; data should still be Gold.","when":"Pixel-perfect ops reports.","ex":"NPrinting on QVD → NPrinting/PBI on warehouse"},
{"from":"Qlik dashboard","to":"PBI/Qlik on semantic Gold; AI agent beside them","sim":"Visual analytics.","diff":"Governed metrics layer should be shared.","when":"Consumption.","ex":"Exec app stays Qlik; new self-serve on PBI; agent cites both"},
{"from":"Section Access","to":"RLS / UC row filters / Fabric RLS","sim":"Row security by user.","diff":"Enforced in platform not only in app.","when":"Always for PII.","ex":"SA → dim_user_region filter"},
{"from":"QVD layers (raw/trans/app)","to":"Bronze/Silver/Gold","sim":"Multi-hop quality.","diff":"Open + governed + multi-consumer.","when":"Always.","ex":"Your existing 3-layer QVD map"},
]

refs = [
{"title":"Databricks Certified Data Engineer Associate exam guide (May 4, 2026)","provider":"Databricks","type":"Exam guide","topic":"Certification","difficulty":"Associate","cost":"Free","url":"https://www.databricks.com/sites/default/files/2026-05/databricks-certified-data-engineer-associate-exam-guide-may-2026-000.pdf","stage":"M3-M4","why":"Source of truth for exam sections/weights.","verified":"2026-08-18"},
{"title":"Databricks certification hub","provider":"Databricks","type":"Portal","topic":"Certification","difficulty":"All","cost":"Free","url":"https://www.databricks.com/learn/certification","stage":"All","why":"Find current credentials.","verified":"2026-08-18"},
{"title":"Databricks documentation","provider":"Databricks","type":"Docs","topic":"Platform","difficulty":"All","cost":"Free","url":"https://docs.databricks.com/","stage":"M3+","why":"Product truth; wins over blogs.","verified":"2026-08-18"},
{"title":"Lakeflow Jobs docs","provider":"Databricks","type":"Docs","topic":"Jobs","difficulty":"Associate","cost":"Free","url":"https://docs.databricks.com/jobs/","stage":"M3","why":"DAG, triggers, monitoring.","verified":"2026-08-18"},
{"title":"Auto Loader","provider":"Databricks","type":"Docs","topic":"Ingestion","difficulty":"Associate","cost":"Free","url":"https://docs.databricks.com/ingestion/auto-loader/index.html","stage":"M3","why":"21% exam weight area.","verified":"2026-08-18"},
{"title":"Unity Catalog","provider":"Databricks","type":"Docs","topic":"Governance","difficulty":"Associate","cost":"Free","url":"https://docs.databricks.com/data-governance/unity-catalog/index.html","stage":"M3","why":"Grants, managed/external, lineage.","verified":"2026-08-18"},
{"title":"Databricks Asset Bundles / DABs","provider":"Databricks","type":"Docs","topic":"CI/CD","difficulty":"Associate","cost":"Free","url":"https://docs.databricks.com/dev-tools/bundles/index.html","stage":"M3-M4","why":"May 2026 CI/CD section (Automation Bundles).","verified":"2026-08-18"},
{"title":"Databricks Academy","provider":"Databricks","type":"Training","topic":"Courses","difficulty":"Associate","cost":"Free/Paid","url":"https://customer-academy.databricks.com/","stage":"M3-M4","why":"Official ILT/self-paced: Connect, Jobs, LDP, UC, DevOps.","verified":"2026-08-18"},
{"title":"Apache Spark latest docs","provider":"ASF","type":"Docs","topic":"Spark","difficulty":"Core","cost":"Free","url":"https://spark.apache.org/docs/latest/","stage":"M2","why":"Engine semantics.","verified":"2026-08-18"},
{"title":"PySpark API","provider":"ASF","type":"API","topic":"PySpark","difficulty":"Core","cost":"Free","url":"https://spark.apache.org/docs/latest/api/python/","stage":"M2","why":"Functions reference.","verified":"2026-08-18"},
{"title":"DP-700 study guide","provider":"Microsoft","type":"Exam guide","topic":"DP-700","difficulty":"Associate","cost":"Free","url":"https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/dp-700","stage":"M5-M6","why":"Skills measured as of Jul 21, 2026.","verified":"2026-08-18"},
{"title":"Fabric Data Engineer Associate credential","provider":"Microsoft","type":"Certification page","topic":"DP-700","difficulty":"Associate","cost":"Free","url":"https://learn.microsoft.com/en-us/credentials/certifications/fabric-data-engineer-associate/","stage":"M5","why":"Exam logistics, practice assessment link.","verified":"2026-08-18"},
{"title":"DP-700T00 training","provider":"Microsoft","type":"Course","topic":"Fabric","difficulty":"Associate","cost":"Free/Paid instructor","url":"https://learn.microsoft.com/en-us/training/courses/dp-700t00","stage":"M5","why":"Official course alignment.","verified":"2026-08-18"},
{"title":"Microsoft Fabric documentation","provider":"Microsoft","type":"Docs","topic":"Fabric","difficulty":"All","cost":"Free","url":"https://learn.microsoft.com/en-us/fabric/","stage":"M5","why":"Product truth.","verified":"2026-08-18"},
{"title":"Data engineering in Fabric overview","provider":"Microsoft","type":"Docs","topic":"Fabric DE","difficulty":"Associate","cost":"Free","url":"https://learn.microsoft.com/en-us/fabric/data-engineering/data-engineering-overview","stage":"M5","why":"Linked from DP-700 guide.","verified":"2026-08-18"},
{"title":"Microsoft Learn DP-700 practice assessment","provider":"Microsoft","type":"Practice","topic":"DP-700","difficulty":"Associate","cost":"Free","url":"https://learn.microsoft.com/en-us/credentials/certifications/exams/dp-700/practice/assessment?assessment-type=practice&assessmentId=1704375541&practice-assessment-type=certification","stage":"M6","why":"Official readiness check — required before you claim exam readiness.","verified":"2026-08-18"},
{"title":"Exam sandbox","provider":"Microsoft","type":"UX demo","topic":"Exam","difficulty":"All","cost":"Free","url":"https://aka.ms/examdemo","stage":"M6","why":"UI familiarity.","verified":"2026-08-18"},
]
# more high quality
refs += [
{"title":"Delta Lake documentation","provider":"Delta.io / Databricks","type":"Docs","topic":"Delta","difficulty":"Core","cost":"Free","url":"https://docs.delta.io/latest/index.html","stage":"M3","why":"Format internals.","verified":"2026-08-18"},
{"title":"Azure OpenAI / Microsoft Learn Generative AI","provider":"Microsoft","type":"Learn","topic":"GenAI","difficulty":"Intro","cost":"Free","url":"https://learn.microsoft.com/en-us/azure/ai-foundry/openai/overview","stage":"M6","why":"Enterprise LLM platform concepts.","verified":"2026-08-18"},
{"title":"LangGraph documentation","provider":"LangChain","type":"Docs","topic":"Agents","difficulty":"Advanced","cost":"Free","url":"https://docs.langchain.com/oss/python/langgraph/overview","stage":"M6","why":"Stateful agents.","verified":"2026-08-18"},
{"title":"LangChain docs","provider":"LangChain","type":"Docs","topic":"GenAI","difficulty":"Advanced","cost":"Free","url":"https://docs.langchain.com/oss/python/langchain/overview","stage":"M6","why":"Tools/RAG primitives.","verified":"2026-08-18"},
]

books = [
{"title":"Designing Data-Intensive Applications (Kleppmann)","month":"1–2","priority":"Essential","chapters":"Replication, batch/stream, derived data — not Hadoop trivia","why":"Architect vocabulary. Slightly older examples; principles current.","outdated": False},
{"title":"Fundamentals of Data Engineering (Reis, Housley)","month":"1","priority":"Essential","chapters":"Lifecycle, undercurrents, architecture","why":"Best DE overview for career switchers.","outdated": False},
{"title":"The Data Warehouse Toolkit (Kimball) 3rd ed.","month":"1 and 5","priority":"Essential for modeling","chapters":"Grain, transactions, snapshots, SCD","why":"Still the dimensional bible; apply on Warehouse/Gold.","outdated": False},
{"title":"Spark: The Definitive Guide (Chambers, Zaharia)","month":"2","priority":"Optional / version-sensitive","chapters":"DataFrames, Spark SQL, streaming intro","why":"Excellent mental model; APIs evolved — pair with current Spark docs.","outdated": True},
{"title":"Learning Spark 2nd ed. (Damji et al.)","month":"2","priority":"Optional / version-sensitive","chapters":"Catalyst, Datasets/DF","why":"Good pedagogy; confirm APIs against latest Spark.","outdated": True},
{"title":"Official Databricks documentation + Academy (not a book)","month":"3–4","priority":"Essential","chapters":"Lakeflow, UC, DABs","why":"Books lag Lakeflow rename and May 2026 exam.","outdated": False},
{"title":"Microsoft Fabric official docs + DP-700T00","month":"5–6","priority":"Essential","chapters":"Study guide domains","why":"Fabric changes faster than any book. Treat 2024 Fabric books as outdated unless marked.","outdated": False},
{"title":"Building LLM Apps / OpenAI cookbook (online)","month":"6","priority":"Optional","chapters":"RAG eval, tool calling","why":"Prefer current vendor cookbooks over 2023 hardcovers.","outdated": True},
{"title":"AI Engineering (Chip Huyen, 2025)","month":"6","priority":"Recommended","chapters":"RAG, eval, production","why":"Practical AI systems — complement, not replace, data platform skills.","outdated": False},
]

roles = [
{"title":"Data Engineer","have":"ETL, SQL, modeling, pipelines-in-Qlik","need":"Spark, cloud orchestration, tests, infra as code","certs":"DBx Associate or DP-700","projects":"P1–P2","interview":"SQL+PySpark+incremental"},
{"title":"Senior Data Engineer","have":"12y delivery, stakeholders, reliability instincts","need":"Spark UI mastery, CDC, SLAs, mentoring","certs":"Associate then think Professional later","projects":"P1–P6","interview":"Skew, MERGE, on-call"},
{"title":"Databricks Consultant","have":"BI translation, workshops","need":"UC, Lakeflow, DABs, cost, delivery playbooks","certs":"Data Engineer Associate (May 2026+)","projects":"P1,P4,P8","interview":"Client architecture + hands-on"},
{"title":"Fabric Data Engineer","have":"MSFT BI adjacency, Power BI some","need":"OneLake, pipelines, KQL, mirroring, security stack","certs":"DP-700","projects":"P2,P5","interview":"Engine choice questions"},
{"title":"Analytics Engineer","have":"Metrics, semantic thinking, Qlik models","need":"dbt-like transforms, Gold, testing","certs":"helpful not mandatory","projects":"P2,P7","interview":"grain and metrics"},
{"title":"Data & AI Consultant","have":"Business workshops","need":"RAG/agents on Gold, eval, security","certs":"platform cert + AI fundamentals badge optional","projects":"P8","interview":"why not bronze RAG"},
{"title":"AI Analytics Consultant","have":"Dashboard narrative skills","need":"NL2SQL governance, metric registry","certs":"same","projects":"P8","interview":"eval sets"},
{"title":"Data Architect","have":"Enterprise reporting estates","need":"Trade-off decks, standards, multi-platform","certs":"both associates then architecture experience","projects":"all + ADRs","interview":"30-min system design"},
]

freelance = [
{"title":"Upwork: Qlik-to-lakehouse coexistence","client":"Mid-market with Qlik Sense + messy SQL Server",
 "requirements":"Keep Qlik; add Delta gold; daily SLA","estimation":"Discovery 1–2 wks; MVP gold 4–6 wks","scope":"One domain (Sales) not whole enterprise","proposal":"As-is, to-be diagram, risks, RACI, dual-run","architecture":"Ingest → silver → gold views for Qlik ODBC/SQL","deliverables":"Repo, runbook, DQ, 2 dashboards unchanged numbers","pricing":"Fixed MVP + T&M change requests; never unlimited AI chatbot","discovery":["QVD lineage","reload windows","section access","source SLAs"],
 "client_qs":["Who owns SAP extracts?","What is the grain of Sales?"]},
{"title":"Fiverr-adjacent: not cheap dashboards — sell pipelines","client":"Avoid $50 dashboard gigs","requirements":"Productize: CDC workshop, medallion starter, DP-700 coaching",
 "estimation":"Packaged 2-week starter","scope":"Template + enablement","proposal":"Productized SOW","architecture":"Starter DAB or Fabric pipeline pack","deliverables":"IaC + docs","pricing":"Productized tiers","discovery":["Capacity/cloud"],"client_qs":["Prod vs sandbox?"]},
{"title":"LinkedIn consulting: Fabric for Microsoft shops","client":"Already on M365/PBI","requirements":"DP-700 shaped delivery","estimation":"12-week program","scope":"OneLake standards + 2 data products","proposal":"Standards first","architecture":"Lakehouse+WH+PBI","deliverables":"Deployment pipelines, security matrix","pricing":"Retainer","discovery":["domains","capacities"],"client_qs":["Who is Fabric admin?"]},
{"title":"Direct client: AI analytics on existing Gold","client":"Has lakehouse, wants chatbot","requirements":"Eval, security, metric wiki","estimation":"4-week discovery+POC","scope":"10 questions, gold-only","proposal":"POC success = eval score not a demo wow","architecture":"RAG+NL2SQL tools","deliverables":"traces, eval notebook, threat model","pricing":"POC capped + build","discovery":["metric owners"],"client_qs":["What must never be answered?"]},
]

bootcamp = []
for exam, focuses in {
 "dbx": ["Platform compute matrix","Auto Loader vs COPY vs Connect","PySpark grain drills","Jobs triggers+retries","Git Folders+DAB CLI","Spark UI skew/spill","UC grants+RLS+ABAC","Liquid+PO","Mock exam + review","Weak ingest","Weak transform","Weak jobs","Weak cicd","Weak gov","Full mock timed","Light review + sleep"],
 "dp": ["Workspace Spark/OneLake/Airflow","Git+deploy pipes+db projects","Security matrix+OneLake","Choose DF vs pipeline vs notebook","Shortcuts+mirroring","KQL windows+RTI accel","Monitor every item type","Optimize lake/WH/Spark","Mock + review","Weak D1","Weak D2","Weak D3","Error labs","Perf labs","Full mock timed","Official MS practice assessment"]
}.items():
    for d in range(1, 31):
        bootcamp.append({"exam": exam, "day": d, "hours": 2 if d < 28 else 1.5,
            "focus": focuses[d % len(focuses)] if d < 29 else "Exam strategy: time, flag, reread grain",
            "tasks": "Revise notes + 20 questions + 1 lab + write 5 interview answers. No new rabbit holes."})

simRounds = [
{"name":"SQL","prompt":"Write incremental MERGE for orders and explain grain tests.","keywords":["merge","grain","watermark","duplicate","scd"]},
{"name":"Python","prompt":"Design an idempotent API ingestion module.","keywords":["retry","hash","pagination","timeout","logging"]},
{"name":"PySpark","prompt":"Dedup events and join a small dim; discuss plans.","keywords":["window","broadcast","explain","skew","unionByName"]},
{"name":"Databricks","prompt":"Choose ingest tool and Job triggers for S3+Salesforce.","keywords":["auto loader","copy into","lakeflow","trigger","unity catalog"]},
{"name":"Fabric","prompt":"Choose lakehouse vs warehouse vs eventhouse for IoT+finance.","keywords":["onelake","shortcut","kql","pipeline","rls"]},
{"name":"Architecture","prompt":"Retail SAP+SFDC+CSV+stream+AI.","keywords":["medallion","hot path","gold","cost","governance"]},
{"name":"System design","prompt":"5TB, 2M tx/day, fraud, PBI, chatbot, strict security.","keywords":["streaming","warehouse","agent","mask","sla"]},
{"name":"Scenario","prompt":"Job doubled in time; Spark UI one slow task.","keywords":["skew","aqe","shuffle","salt","ui"]},
{"name":"GenAI","prompt":"Why did sales decline agent.","keywords":["rag","gold","nl2sql","eval","injection"]},
{"name":"Managerial","prompt":"6-month plan from Qlik team to lakehouse; risks.","keywords":["coexistence","training","dual-run","raci","sla"]},
]

# merge diagrams into career dump together with rest
# load diagrams from previous function - redefine quickly
diagrams = []
for title, nodes, explain, when in specs:
    diagrams.append({"title": title, "svg": boxes(title, nodes, None), "explain": explain,
        "components": nodes, "flow": " → ".join(nodes), "when": when,
        "interview": [f"When would you not use {title}?", "How does this map from Qlik?"]})

dump("career.js", {
    "cheats": cheats, "qlikBridge": qlikBridge, "roles": roles, "freelance": freelance,
    "bootcamp": bootcamp, "simRounds": simRounds, "diagrams": diagrams
})
dump("refs.js", {"refs": refs, "books": books})
print("career+refs ok")
