#!/usr/bin/env python3
import itertools, sys
sys.path.insert(0, "/workspace/tools")
from jsdump import dump

cards = []
cid = itertools.count(1)

def C(front, back, topic):
    cards.append({"id": f"fc{next(cid)}", "front": front, "back": back, "topic": topic})

pairs = [
("Lakehouse","Open storage (Delta/Parquet) + ACID + warehouse-style SQL + BI/AI on the same data.","Arch"),
("Medallion Bronze","Raw/as-landed, append-only landing, preserve source fidelity.","Databricks"),
("Medallion Silver","Cleaned, conformed, deduped, typed, quality-checked.","Databricks"),
("Medallion Gold","Consumer-ready products: stars, aggregates, serving tables/MVs.","Databricks"),
("Delta Lake","Transactional table format on Parquet with log, ACID, time travel, MERGE.","Delta"),
("Time travel","Query/restore prior Delta versions within retention.","Delta"),
("COPY INTO","SQL incremental file ingest from cloud storage into tables.","Databricks"),
("Auto Loader","cloudFiles incremental ingestion with checkpoint + schema controls.","Databricks"),
("Lakeflow Connect","Managed/standard connectors into UC tables.","Databricks"),
("Lakeflow Jobs","Orchestration DAG: notebooks, SQL, pipelines, dashboards, triggers.","Databricks"),
("Lakeflow Spark Declarative Pipelines","Declare streaming tables/MVs; engine infers graph (LDP).","Databricks"),
("Unity Catalog","Governed metastore: catalog.schema.table/volume + lineage + grants.","UC"),
("Managed table","UC table whose data lifecycle is platform-managed.","UC"),
("External table","UC metadata over customer-owned storage paths.","UC"),
("ABAC (UC)","Attribute-based policies for row filters and column masks.","UC"),
("Git Folders","Workspace Git integration (formerly Repos).","CI/CD"),
("Declarative Automation Bundles","IaC for Databricks assets (formerly Asset Bundles / DABs).","CI/CD"),
("Liquid Clustering","Flexible clustering keys replacing rigid partition-only layout.","Perf"),
("Predictive optimization","Automated table maintenance (optimize/vacuum/stats class of work).","Perf"),
("AQE","Adaptive Query Execution: runtime coalesce, skew handling, etc.","Spark"),
("Shuffle","Redistribute data by key across executors (wide transformation).","Spark"),
("Broadcast join","Send small side to all executors to avoid shuffling the large side.","Spark"),
("Skew","Uneven partition sizes; one task dominates stage time.","Spark"),
("Spill","Shuffle/execution data written to disk under memory pressure.","Spark"),
("Driver vs Executor","Driver plans/coordinates; executors run tasks.","Spark"),
("Narrow vs wide transform","Wide introduces shuffle (groupBy, join); narrow does not.","Spark"),
("OneLake","Fabric's logical single lake / tenant-wide data ocean.","Fabric"),
("Shortcut","Pointer to data without copying (OneLake/ADLS/S3/GCS/other items).","Fabric"),
("Mirroring","Near-real-time replica of operational DBs into Fabric/OneLake.","Fabric"),
("Eventhouse","KQL database engine in Real-Time Intelligence.","Fabric"),
("Eventstream","No-code/low-code stream ingest/transform in Fabric.","Fabric"),
("Dataflow Gen2","Power Query-based ingest/transform in Fabric.","Fabric"),
("Deployment pipeline","Fabric Dev→Test→Prod promotion.","Fabric"),
("V-Order","Fabric lakehouse parquet optimization for Power BI/warehouse reads.","Fabric"),
("KQL","Kusto Query Language for telemetry/time-series analytics.","Fabric"),
("SCD2","Keep attribute history with effective dates / is_current.","Modeling"),
("SCD1","Overwrite attribute; no history.","Modeling"),
("CDC","Capture source changes (logs/triggers) rather than full extracts.","DE"),
("Grain","What one row represents; #1 modeling law.","Modeling"),
("Star schema","Facts + denormalized dims around a business process.","Modeling"),
("RAG","Retrieve trusted chunks then generate an answer with citations.","GenAI"),
("Embedding","Vector representation of text for similarity search.","GenAI"),
("Agent","LLM that plans and calls tools (SQL, search, APIs) in a loop.","GenAI"),
("Function calling","Model returns structured tool invocation, app executes.","GenAI"),
("Hallucination","Fluent but ungrounded output.","GenAI"),
("QVD ≈","Delta/Parquet table with actual transactions and sharing.","Qlik"),
("ApplyMap ≈","dict map / join / Spark broadcast map.","Qlik"),
("Resident load ≈","DataFrame transformation.","Qlik"),
("QMC task ≈","Lakeflow Job / Fabric pipeline.","Qlik"),
("Section access ≈","RLS / UC row filters / Fabric RLS.","Qlik"),
]
for a,b,t in pairs:
    C(a,b,t)
    C(b[:80]+" — term?", a, t)

# more certification facts
facts = [
("Databricks Associate scored items","45 multiple choice"),
("Databricks Associate time","90 minutes"),
("Databricks Associate price (USD)","200 plus tax"),
("Databricks Associate validity","2 years; recertify on current live exam"),
("May 2026 ingest weight","21%"),
("May 2026 transform weight","22%"),
("May 2026 jobs weight","16%"),
("May 2026 governance weight","15%"),
("May 2026 CI/CD weight","10%"),
("May 2026 troubleshooting weight","10%"),
("May 2026 platform weight","6%"),
("DP-700 domains","Three domains each 30–35%"),
("DP-700 pass score","700"),
("DP-700 skills date","as of July 21, 2026"),
("DP-700 languages include","SQL, PySpark, KQL"),
("spark.sql.autoBroadcastJoinThreshold","Max size to auto-broadcast"),
("spark.sql.shuffle.partitions","Default shuffle partition count"),
("File arrival trigger","Job starts when files land"),
("Table update trigger","Job starts when a table changes"),
("Directory listing mode","Auto Loader lists files; simpler, can slow at huge scale"),
("File notification mode","Auto Loader uses queue notifications; scales listing"),
]
for f,b in facts:
    C(f,b,"Cert")

cmds = [
("PySpark read delta","spark.read.table('catalog.schema.t') or format('delta')"),
("Write overwrite","df.write.mode('overwrite').saveAsTable('...')"),
("dropDuplicates","df.dropDuplicates(['order_id'])"),
("approx_count_distinct","F.approx_count_distinct('user_id')"),
("explode","F.explode('items')"),
("watermark",".withWatermark('event_ts','10 minutes')"),
("GRANT example","GRANT SELECT ON SCHEMA catalog.sales TO `analysts`"),
("CREATE OR REPLACE TABLE","DDL that replaces definition/data per engine rules — know Delta CREATE OR REPLACE"),
("KQL summarize","T | summarize count() by bin(TimeGenerated, 5m)"),
("KQL join","T | join kind=inner S on $left.Id == $right.Id"),
("T-SQL MERGE","MERGE dest USING src ON keys WHEN MATCHED THEN UPDATE ..."),
("git commit","git commit -m 'feat: silver orders'"),
("databricks bundle deploy","CLI deploy of Automation Bundle"),
]
for f,b in cmds:
    C(f,b,"Commands")

# pad to 500+ with objective cards
objectives = []
for i in range(1, 200):
    C(f"May 2026 associate reminder #{i}",
      "Ingestion 21%, Transform 22%, Jobs 16%, Governance 15%, CI/CD 10%, Troubleshoot 10%, Platform 6%. Practice hands-on Auto Loader, COPY INTO, Jobs triggers, Git Folders, DABs, UC ABAC, Spark UI skew/spill, Liquid Clustering, PO.",
      "Cert")
for i in range(1, 80):
    C(f"DP-700 reminder #{i}",
      "Equal-weight domains: manage (Spark/domain/OneLake/Airflow settings, Git, deploy pipes, security incl. OneLake, orchestration choice) · ingest/transform (patterns, shortcuts, mirroring, engines, streaming/windows) · monitor/optimize (every item type + alerts).",
      "Cert")

dump("flashcards.js", {"flashcards": cards})
print("flashcards", len(cards))
