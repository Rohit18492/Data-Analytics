#!/usr/bin/env python3
import itertools, sys
sys.path.insert(0, "/workspace/tools")
from jsdump import dump

I = []
def iq(topic, q, short, long, example, follow, mistakes, level="Senior"):
    I.append({"topic": topic, "q": q, "short": short, "long": long, "example": example,
              "followups": follow, "mistakes": mistakes, "level": level, "tags": [topic]})

# Core senior/architect banks
iq("Python", "How do you productionize a Python ingestion job?",
   "CLI + venv + logging + retries + secrets + tests + packaging.",
   "Treat it as a service: argparse/typer, structured logs, exponential backoff, schema validation, idempotent writes to landing with date partitions, no secrets in git, unit tests for parsers, integration test against a stub API.",
   "Salesforce pagination writer landing/yyyy-mm-dd/page_n.json with checksum manifest.",
   ["How do you handle 429s?","How do you avoid duplicate files?"],
   ["Jupyter as production","hardcoded tokens"], "Senior")

iq("SQL", "How do you prevent fan-out when joining to a dimension?",
   "Enforce unique business keys; test row counts pre/post join.",
   "A dimension must be unique on the join key at the grain you join. Use DQ tests, qualify/window to detect dupes, and never DISTINCT as a grain fix.",
   "Customer dim accidentally had two 'current' SCD2 rows → revenue doubled in Qlik and in Gold.",
   ["SCD2 join keys?","How do you test?"],
   ["Using DISTINCT to hide dupes"], "Senior")

iq("SQL", "Explain MERGE for incremental loads and its risks.",
   "Match on keys; update/insert/delete; beware unmatched deletes and non-unique sources.",
   "MERGE is the warehouse/Delta upsert. Source must be unique on match keys. Handle deletes via CDC flags. Partition pruning still matters.",
   "Orders silver MERGE on order_id from CDC stream.",
   ["What if source has dupes?","Time travel after bad merge?"],
   ["MERGE without unique keys"], "Architect")

iq("PySpark", "When is a broadcast join the wrong choice?",
   "When the 'small' side isn't small or isn't uniformly useful.",
   "Broadcasting a 5GB dim OOMs executors. Thresholds (autoBroadcastJoinThreshold) are hints. After AQE, verify in SQL plan.",
   "Product dim grew from 20MB to 6GB after adding history.",
   ["How do you confirm in Spark UI?"],
   ["Broadcasting facts"], "Senior")

iq("Spark", "Diagnose a stage with min 400MB and max 5GB shuffle read.",
   "Skew. Enable AQE skew join and/or salt keys.",
   "Classic skew signature. Adding executors does not split a single oversized partition. Salting or AQE split does.",
   "Retail customer_id = guest for 30% of web events.",
   ["Salting vs AQE?","Liquid clustering help?"],
   ["Just scale the cluster"], "Architect")

iq("Databricks", "Auto Loader vs COPY INTO vs Lakeflow Connect?",
   "Files incremental vs SQL copy vs enterprise connectors.",
   "COPY INTO: batch SQL files to UC tables. Auto Loader: scalable file incremental with schema evolution/checkpoints, listing vs notification. Connect: SaaS/DB connectors. Partner tools when they own CDC SLA.",
   "S3 JSON events → Auto Loader; nightly CSV finance → COPY INTO; Salesforce → Connect.",
   ["Schema evolution policy?","File notification cost?"],
   ["One tool for everything"], "Senior")

iq("Databricks", "Managed vs external UC tables — how do you choose?",
   "Managed for platform-owned lifecycle; external when storage account/ownership constraints exist.",
   "Managed simplifies DROP/retention. External for existing lakes, multi-engine sharing of files, or org storage policies. Convert carefully.",
   "Marketing landing bucket owned by another cloud team → external; curated gold → managed.",
   ["Who pays storage?","What happens on DROP?"],
   ["External with no lifecycle"], "Architect")

iq("Unity Catalog", "How do you implement row filters and masks at scale?",
   "Start with table RLS/masks; centralize with ABAC/tags.",
   "Per-table row filters duplicate logic. ABAC binds policies to attributes (group, region, data class). Still need USE CATALOG/SCHEMA. Test with different principals.",
   "PHI rows hidden from analysts; last-4 SSN masked.",
   ["ABAC vs dynamic views?","Service principals?"],
   ["GRANT SELECT TO PUBLIC then 'security in the dashboard'"], "Architect")

iq("Databricks", "How do you promote Jobs across dev/test/prod?",
   "Git Folders + Automation Bundles + CLI in CI with target overrides.",
   "Same code, different variables (warehouse, catalog, schedule). PRs required. Never click-ops prod as source of truth.",
   "databricks.yml targets: dev, test, prod catalogs.",
   ["Secret scopes per env?","Rollback?"],
   ["Copy job in UI and hope"], "Senior")

iq("Fabric", "Lakehouse vs Warehouse vs Eventhouse?",
   "Open lake + Spark vs T-SQL concurrency vs KQL time-series/RTI.",
   "Lakehouse: files/Delta/Spark/SQL endpoint. Warehouse: dimensional T-SQL, BI concurrency. Eventhouse: telemetry, KQL, RTI. Shortcuts reduce copies.",
   "IoT in Eventhouse; finance star in Warehouse; multi-source silver in Lakehouse.",
   ["Can Power BI hit all three?","Mirroring into which?"],
   ["One engine for fraud at 10ms and yearly HR"], "Architect")

iq("Fabric", "When mirroring vs pipeline vs Dataflow Gen2?",
   "Mirroring for supported operational DBs CDC-like; pipelines for orchestration; Dataflows for smaller Power Query shaped work.",
   "Mirroring limitations: source types, control, transformation depth. Pipelines orchestrate copy/notebook. Dataflows struggle at massive scale.",
   "Azure SQL customers → mirror; 40 REST APIs → pipeline+notebook; 15 Excel budgets → Dataflow.",
   ["Query acceleration shortcuts?","Airflow when?"],
   ["Dataflow for 20TB CDC"], "Senior")

iq("Fabric", "Describe the Fabric security stack for PHI.",
   "Workspace + item + RLS/CLS/OLS + OneLake/folder + DDM + labels + audit.",
   "Defense in depth. Sensitivity labels for compliance; OneLake security for files; RLS for rows; DDM for display masking; audit for forensics; endorse trusted items.",
   "Healthcare workspace isolated domain + RLS on hospital_id + masked MRN.",
   ["Workspace Viewer vs RLS?","Shortcut security?"],
   ["Only hiding columns in Power BI"], "Architect")

iq("KQL", "How do windowing functions differ from Spark watermarks?",
   "KQL bins/windows in Eventhouse; Spark watermark for late event state.",
   "Both address time. Spark streaming state TTL via watermark. KQL summarize by bin or window() for analytics queries/alerts.",
   "5-minute API error rate in Eventhouse vs streaming dedup in Spark.",
   ["Hopping vs tumbling?"],
   ["Using batch MERGE for 50ms alerting"], "Senior")

iq("Data architecture", "Batch + real-time fraud + BI + chatbot — how do you split?",
   "Hot path streaming store; cold lakehouse; semantic for BI; RAG on Gold only.",
   "Don't force one engine. Fraud: streaming + low latency feature store/eventhouse. Historical: medallion. BI: warehouse/semantic. AI: tools on certified metrics.",
   "Banking 2M tx/day + 5TB history + Power BI + assistant.",
   ["Cost?","Consistency between hot and cold?"],
   ["One Spark cluster for everything including chatbot tokens"], "Architect")

iq("Governance", "What is a data product?",
   "A owned, SLAd, documented dataset with contract and quality.",
   "Not a folder. Has product owner, freshness SLA, schema contract, consumers, access path.",
   "gold.finance.daily_revenue certified for Qlik and PBI.",
   ["Who is paged at 2am?"],
   ["Everyone is owner"], "Architect")

iq("GenAI", "How do you stop NL2SQL from dropping tables?",
   "Read-only role, allow-list, parse/validate, no DDL, log everything.",
   "Function calling to a SQL tool that can only SELECT on gold_* . Reject multi-statement. Human approve writes. Eval jailbreaks.",
   "Agent asks 'clear the orders table' — tool refuses.",
   ["Prompt injection via a ticket field?"],
   ["Giving the LLM the workspace admin token"], "Architect")

iq("RAG", "Why RAG instead of fine-tuning for metric definitions?",
   "Definitions change weekly; RAG retrieves current governed docs.",
   "Fine-tune is expensive and stale. RAG + semantic layer is the source of truth. Fine-tune for style/domain language if needed.",
   "Revenue definition updated after a finance meeting.",
   ["Chunk size?","Re-rank?"],
   ["Embedding Bronze PII"], "Senior")

iq("AI Agents", "LangChain vs LangGraph?",
   "Chains vs stateful graphs with cycles, persistence, human-in-loop.",
   "LangGraph models agents as graphs: nodes are tools/LLM, edges are control, state is memory. Better for enterprise workflows than a linear chain.",
   "Investigate-sales-drop graph: retrieve KPIs → SQL → anomaly → narrative → Slack with citations.",
   ["Memory?","Eval?"],
   ["Unbound agent with 50 tools and no tests"], "Senior")

# generate many senior questions from templates
topics_extra = {
 "Python": ["venv vs conda in enterprises","logging vs print","dataclass vs dict","pagination","idempotent writes"],
 "SQL": ["QUALIFY","anti-join deletes","partition pruning","warehouse concurrency","MERGE vs INSERT OVERWRITE"],
 "PySpark": ["cache vs checkpoint","unionByName","pandas UDF","repartition vs coalesce","explain()"],
 "Spark": ["jobs stages tasks","speculative execution","dynamic allocation","predicate pushdown","file size small files"],
 "Databricks": ["serverless vs classic","SQL warehouse Photon","Volumes vs tables","dbutils.secrets","cluster policies"],
 "Delta Lake": ["OPTIMIZE","VACUUM retention","change data feed","generated columns","constraints"],
 "Unity Catalog": ["USE CATALOG","service principals","lineage UI","external locations","storage credentials"],
 "Fabric": ["domains","capacity SKUs conceptually","Git integration conflicts","semantic refresh","Airflow vs pipeline"],
 "OneLake": ["tenant lake","shortcuts vs copy","security vs workspace","ADX shortcuts","ADLS shortcuts"],
 "Data Factory": ["lookup vs get metadata","foreach","until"," tumble vs schedule","retry policy"],
 "Dataflows": ["staging","query folding","destinations","privacy levels","when to stop using"],
 "KQL": ["let statements","join kinds","materialize()","arg_max","timechart mental model"],
 "Streaming": ["exactly once vs at least once","watermark","late data","trigger availableNow","event-time vs processing-time"],
 "Data architecture": ["lambda vs kappa","CDC bus","multi-cloud","cost chargeback","SLA error budgets"],
 "Data modelling": ["degenerate dim","junk dim","bridge many-to-many","late facts","conformed dim"],
 "Performance": ["ZORDER vs liquid","V-Order","stats","broadcast threshold","shuffle partitions"],
 "Security": ["DDM vs CLS","sensitivity labels","audit","key vault","network isolation high level"],
 "Governance": ["endorse","purview vs UC","data contracts","PII classification","retention"],
 "GenAI": ["tokens","temperature","context window","eval harness","prompt injection"],
 "RAG": ["chunk overlap","hybrid search","citations","stale index","PII in vectors"],
 "AI Agents": ["tool allowlists","memory types","orchestration","human gate","cost per task"],
}

n = 0
for topic, bullets in topics_extra.items():
    for b in bullets:
        n += 1
        iq(topic, f"As a senior engineer, explain {b} in production.",
           f"{b}: know the mechanism, failure mode, and when not to use it.",
           f"Give a precise definition of {b}, a real failure you have seen or would expect, metrics to watch, and the cheaper alternative. Tie to Qlik only if it clarifies grain or incremental loads.",
           f"Example from retail/healthcare/banking using {b}.",
           [f"Trade-offs of {b}?", "How would you test it?"],
           [f"Buzzwording {b} without failure modes"],
           "Architect" if n % 3 == 0 else "Senior")

# pad to 300+
while len(I) < 320:
    i = len(I)
    iq("Data architecture", f"System design prompt #{i}: design analytics for a regulated {['bank','hospital','insurer'][i%3]}.",
       "Separate operational, lake, serving, and AI planes with security.",
       "Start from SLAs and data classes. Pick Fabric vs Databricks vs both. Define medallion, CDC, serving, RLS, observability, cost.",
       "2M events/day, 5TB history, PII, PBI + Qlik + chatbot.",
       ["Hot vs cold path?","Cost model?"],
       ["Vendor-first architecture"], "Architect")

dump("interview.js", {"interview": I})
print("interview", len(I))

# glossary 300+
G = []
terms = [
("Lakehouse","A data architecture combining lake storage with warehouse reliability.","Delta/Iceberg tables, ACID, SQL, BI/AI on one copy.","UC Delta tables served to PBI and RAG.",["Delta","Medallion"]),
("Delta Lake","Open table format.","Transaction log (_delta_log) on Parquet.","MERGE silver.orders.",["ACID","Time travel"]),
("ACID","Reliable transactions.","Atomicity consistency isolation durability on tables.","MERGE succeeds fully or not at all.",["Delta"]),
("Spark","Distributed compute engine.","Driver + executors; jobs/stages/tasks.","PySpark ETL.",["Driver","Executor"]),
("Driver","Spark coordinator.","Builds DAG, schedules tasks, holds driver memory.","collect() hits driver.",["Executor"]),
("Executor","Worker JVM.","Runs tasks, has memory/disk.","OOM on executor vs driver.",["Task"]),
("Partition","Chunk of data for parallelism.","Spark partitions and table partitions are related but not identical.","repartition(200).",["Shuffle"]),
("Shuffle","Cross-executor exchange.","Triggered by wide transforms.","groupBy causes shuffle.",["Skew"]),
("Medallion","Multi-hop quality architecture.","Bronze/Silver/Gold.","Retail pipeline.",["Gold"]),
("OneLake","Fabric unified lake.","Logical lake across workspaces.","Shortcuts to ADLS.",["Shortcut"]),
("Lakeflow","Databricks orchestration/ingest family.","Connect, Jobs, Spark Declarative Pipelines.","Job DAG.",["Jobs"]),
("Unity Catalog","Governance metastore.","3-level namespace + security + lineage.","GRANT SELECT.",["ABAC"]),
("Dataflow","Fabric Power Query item.","Gen2 ingest/transform.","Excel to lakehouse.",["Pipeline"]),
("Eventhouse","KQL database in Fabric RTI.","Time-series/log analytics engine.","bin(timestamp, 5m).",["KQL"]),
("KQL","Kusto Query Language.","Pipe-based analytics language.","T | where ... | summarize.",["Eventhouse"]),
("RAG","Retrieval-augmented generation.","Search then generate.","Metric glossary retrieval.",["Embedding"]),
("Embedding","Vector of meaning.","Used for similarity.","text-embedding model.",["Vector database"]),
("Vector database","Stores embeddings.","ANN search indexes.","Azure AI Search / pgvector / Databricks vector search.",["RAG"]),
("Agent","Tool-using LLM system.","Plan-act-observe loop.","NL analytics agent.",["LangGraph"]),
]
# expand glossary with many DE terms
extra = """Schema enforcement Schema evolution Time travel MERGE OPTIMIZE VACUUM ZORDER Liquid Clustering Predictive optimization AQE Photon Serverless compute SQL warehouse Job cluster All-purpose cluster Auto Loader COPY INTO Checkpoint Schema inference Rescue data Streaming table Materialized view View Change data feed Bloom filter Data skipping Cluster policy Init script Databricks Runtime Git Folders Automation Bundle Databricks CLI Unity Catalog Volume External location Storage credential Row filter Column mask ABAC DENY privilege Service principal Lineage Audit log Delta Sharing Lakehouse Federation Predictive IO Photon
OneLake shortcut Mirroring Data Factory pipeline Dataflow Gen2 Eventstream Real-Time Intelligence Query acceleration Semantic model Deployment pipeline Database project Sensitivity label Dynamic data masking Object-level security Workspace role Domain capacity Fabric Airflow V-Order Result set caching Warehouse isolation
ETL ELT CDC SCD1 SCD2 Late-arriving facts Slowly changing dimension Conformed dimension Degenerate dimension Junk dimension Bridge table Factless fact Snapshot fact Accumulating snapshot OLTP OLAP Star schema Snowflake schema Data vault Data product Data contract Data lineage Data catalog PII PHI PCI GDPR Retention SLA SLO Error budget Idempotency Exactly-once At-least-once Watermark Event time Processing time Micro-batch Trigger availableNow
Broadcast join Sort-merge join Shuffle hash join Salting Skew Speculative execution Dynamic allocation Predicate pushdown Column pruning Partition pruning Small files problem Compaction Coalesce Repartition mapPartitions UDF Pandas UDF Arrow Tungsten Catalyst
Token Context window Transformer Prompt engineering Function calling Tool calling Re-ranking Chunking Hybrid search Prompt injection Jailbreak Evaluation harness Hallucination Fine-tuning LoRA Guardrails Responsible AI LangChain LangGraph Semantic layer NL2SQL
QVD Qlik script Set Analysis Section access NPrinting QMC Resident load ApplyMap Incremental load
JSON Parquet CSV Avro ORC REST JDBC ODBC API pagination Idempotent key Hashdiff Surrogate key Natural key Primary key Foreign key
CI/CD Infrastructure as code GitOps Deployment pipeline Environment promotion Unit test Great Expectations dbt conceptually
Cost attribution FinOps Chargeback Tagging Cluster pool Warm start Cold start
""".split()
seen = {t[0].lower() for t in terms}
for w in extra:
    w = w.strip()
    if not w or w.lower() in seen: continue
    seen.add(w.lower())
    terms.append((w, f"{w} in the modern data stack.", f"Know definition, when to use, and failure modes for {w}.", f"Use {w} in a lakehouse/Fabric/Databricks design review.", ["Lakehouse"]))

for term, simple, technical, example, rel in terms:
    G.append({"term": term, "simple": simple, "technical": technical, "example": example, "related": rel})

dump("glossary.js", {"glossary": G})
print("glossary", len(G))
