#!/usr/bin/env python3
"""Original practice questions aligned to official 2026 blueprints. Not real exam items."""
import itertools, json, sys
sys.path.insert(0, "/workspace/tools")
from jsdump import dump

Q = []
nid = itertools.count(1)

def add(**k):
    k.setdefault("type", "mcq")
    k["id"] = k.get("id") or f"q{next(nid)}"
    Q.append(k)

INDS = ["retail","healthcare","banking","manufacturing","ecommerce","logistics","insurance","pharma","telecom","saas"]
CO = ["Northwind Health","Riverbank Retail","Summit Bank","Forge Motors","ParcelGrid","Helio Insurance","NovaPharm","Skyline Telco","Nimbus SaaS","Harbor Logistics"]

def cycle(i, arr):
    return arr[i % len(arr)]

# ---- Databricks bank: 7 sections, many unique stems ----
platform_q = [
("A team needs ACID tables, time travel after a bad MERGE, and one permission model for BI and AI. What is the core storage+governance pairing?",
 ["DBFS CSV + workspace ACLs only","Delta Lake + Unity Catalog","Local SSD checkpoint files + notebook comments","JSON in object storage + SAS URLs only"], 1,
 "Delta provides transactions/time travel; UC is the governance plane for the Intelligence Platform."),
("Analysts run concurrent SQL all day; ETL must not steal the warehouse. Which compute split is most appropriate?",
 ["One oversized all-purpose cluster for everything","SQL warehouse for BI + Jobs/serverless compute for ETL","Single-node cluster for both","GPU cluster for SQL"], 1,
 "Separate interactive SQL warehouses from job compute; matches cost models on the exam outline."),
("Which statement best describes Unity Catalog's role vs Delta Lake?",
 ["UC stores Parquet files; Delta stores users","Delta is table format/storage layer; UC is metastore/governance hierarchy","They are identical products","UC replaces Spark"], 1,
 "Platform section: architecture = Delta + UC + compute + workspace."),
("A data engineer iterates on notebooks interactively, then must run the same code as a scheduled production workload. What is the typical compute pattern?",
 ["All-purpose for prod jobs to keep caches warm","Jobs compute (or serverless jobs) for prod; all-purpose for interactive dev","SQL warehouse to run PySpark UDFs","GPU all-purpose for MERGE"], 1,
 "Job clusters/serverless jobs isolate cost and lifecycle from interactive clusters."),
("Predictive features that simplify data layout and optimize tables are most closely associated with which platform capability family?",
 ["Manual weekly VACUUM only as a workspace widget","Delta + predictive optimization / intelligent lakehouse features","CSV compaction in DBFS","Printing Spark plans to Slack"], 1,
 "Exam: enable features that simplify layout and optimize query performance — PO/Liquid clustering live in the Delta intelligent layer."),
]
for i, (stem, opts, ans, exp) in enumerate(platform_q):
    add(bank="dbx", domain="1 Platform", topic="Databricks Platform", difficulty="Easy" if i<2 else "Medium",
        stem=stem, options=opts, answer=ans, explain=exp, whyWrong=["Other options mix layers or use anti-patterns."],
        ref="https://docs.databricks.com/", tags=["platform","compute"], month=3)

for i in range(40):
    co, ind = cycle(i, CO), cycle(i, INDS)
    add(bank="dbx", domain="1 Platform", topic="Compute", difficulty=cycle(i,["Easy","Medium","Hard"]),
        stem=f"{co} ({ind}) must pick compute: short interactive PySpark debugging vs a 3-hour nightly MERGE of 8TB. What is the sound default?",
        options=["Use the same always-on all-purpose XL cluster for both to avoid startup","Interactive all-purpose or serverless for debug; Jobs/serverless job compute sized for the 8TB MERGE","SQL warehouse with Photon for the PySpark MERGE UDF","Single-node community edition for 8TB"],
        answer=1, explain="Match compute type and cost model to workload: interactive vs isolated jobs.",
        whyWrong=["Always-on XL burns money.","SQL warehouses are not the general PySpark job runtime.","Single-node cannot host 8TB shuffles."],
        ref="https://docs.databricks.com/compute/index.html", tags=["compute"], month=3)

ingest_templates = [
("{co} lands nightly CSVs in S3/ADLS. They want incremental loads into a UC Delta table with simple SQL and path-based copies. First tool to try?",
 ["COPY INTO","GPU streaming","NPrinting","Excel Power Query in a VM"], 0, "COPY INTO incrementally loads files from object storage into UC tables."),
("{co} needs continuous file arrival from many nested JSON dumps with schema evolution and a checkpoint. Best fit?",
 ["Auto Loader (cloudFiles)","One-time pandas read","Manual dbutils.fs.cp in a loop without checkpoint","Warehouse COPY without files"], 0, "Auto Loader is built for incremental files, schema evolution/enforcement, directory listing or file notification."),
("{co} must ingest Salesforce and SQL Server into UC with managed connectors rather than building JDBC notebooks. Which product family?",
 ["Lakeflow Connect","NPrinting","QMC","Eventhouse KQL only"], 0, "Lakeflow Connect standard/managed connectors are on the May 2026 outline."),
("{co} already has a partner ingestion tool certified on Databricks. When is that reasonable vs Auto Loader?",
 ["Never — Auto Loader is mandatory for all sources","When the source is an enterprise system the partner handles well (volume, CDC, SLA) and lands UC tables","Always use FTP into DBFS user folders","Only for images"], 1, "Exam: prioritize Auto Loader vs Connect vs partner connectors by volume, frequency, types, governance."),
("{co} uses notebooks with JDBC to pull a modest on-prem table hourly. How should this usually be orchestrated?",
 ["Leave the notebook running forever on all-purpose","Lakeflow Job schedule/trigger","Email the CSV to yourself","Unity Catalog ABAC"], 1, "JDBC/ODBC/REST in notebooks are typically scheduled with Lakeflow Jobs."),
("{co} must choose directory listing vs file notification for Auto Loader on millions of files.",
 ["Directory listing always cheaper at any scale","File notification scales better when listing becomes expensive; listing is simpler at small scale","Notification requires printing files to paper","They are identical at 100M files"], 1, "Know both Auto Loader modes."),
("{co} JSON has nested structs. Where should it land for associate-style pipelines?",
 ["UC-governed Delta (bronze) then flatten in silver","A Word document","GPU memory only","QVD on a laptop"], 0, "Semi-structured into UC Delta tables."),
]
for n in range(80):
    stem_t, opts, ans, exp = ingest_templates[n % len(ingest_templates)]
    co = cycle(n, CO)
    add(bank="dbx", domain="2 Ingestion", topic="Ingestion", difficulty=cycle(n,["Easy","Medium","Hard","Scenario"]),
        stem=stem_t.format(co=co), options=opts, answer=ans, explain=exp,
        whyWrong=["Distractors are non-Databricks or non-incremental anti-patterns."],
        ref="https://docs.databricks.com/ingestion/auto-loader/index.html", tags=["autoloader","copy into","lakeflow connect"], month=3)

for n in range(40):
    add(bank="dbx", domain="2 Ingestion", topic="COPY INTO vs Auto Loader", difficulty="Medium",
        stem=f"Night {n+1}: files are dropped to abfss://landing@.../date=2026-08-{(n%28)+1:02d}/. You must load only new files into catalog.ops.bronze_orders. Which SQL-oriented incremental command is purpose-built?",
        options=["COPY INTO catalog.ops.bronze_orders FROM 'abfss://...' FILEFORMAT = CSV","CREATE CLUSTER","GRANT SELECT ON CATALOG","VACUUM catalog.ops.bronze_orders RETAIN 0 HOURS"],
        answer=0, explain="COPY INTO is the SQL incremental file loader into UC tables.",
        whyWrong=["Other commands do not incrementally ingest files."],
        ref="https://docs.databricks.com/sql/language-manual/delta-copy-into.html", tags=["copy into"], month=3)

xform = [
("Silver cleaning from bronze: nulls, types, then write. Which API family is in-scope?",
 ["PySpark DataFrames / Spark SQL","Photoshop","Qlik NPrinting","KQL only on Eventhouse as the only option on Databricks"], 0, "Transformation section is PySpark/SQL cleaning bronze→silver."),
("Need unique invoice counts per day plus summed amount. Which aggregation is correct in spirit?",
 ["sum(amount) and count(distinct invoice_id)","sum(invoice_id) as if ids were measures","avg of strings","collect() then pandas unique on driver for 2B rows"], 0, "count distinct / approx_count_distinct + sum."),
("A 20 MB dimension joins a 4 TB fact. Default strategy?",
 ["Broadcast the dimension (if under threshold)","Broadcast the fact","cross join then distinct","UDF nested loop"], 0, "broadcast join + autoBroadcastJoinThreshold."),
("union vs unionByName vs union all: rows with different column order?",
 ["unionByName aligns by name; positional union can silently misalign","They always fail","union deletes Delta","union all is only for streaming"], 0, "Know union vs union all and name alignment."),
("explode on an array of payment methods creates which grain risk?",
 ["Fact grain changes — revenue can duplicate if you sum after explode without care","It always reduces rows","It deletes the parent","It is identical to broadcast"], 0, "explode is a row-multiplying transform."),
("Gold for BI with incremental maintenance of an aggregate. Which object type is a first-class exam concept?",
 ["Materialized view / streaming table vs plain view vs table","Excel named range","QVD only","ABAC policy as a table"], 0, "Gold objects: MV, views, streaming tables, tables."),
("spark.sql.shuffle.partitions is too low for a huge aggregation. Symptom?",
 ["Few giant tasks, spill, long stage","Too many tiny tasks only","UC GRANT fails","COPY INTO skips files"], 0, "Tuning parameters on the outline."),
("DQ on silver: amount >= 0 and valid customer_id. Where should failures go?",
 ["Quarantine/bad records table + fail pipeline if critical","Drop the rule because bronze is raw","Email screenshots only","Disable UC"], 0, "Apply DQ checks to silver/gold."),
]
for n in range(110):
    stem, opts, ans, exp = xform[n % len(xform)]
    add(bank="dbx", domain="3 Transformation", topic="PySpark/SQL", difficulty=cycle(n,["Easy","Medium","Hard","Scenario"]),
        stem=f"{cycle(n,CO)}: {stem}", options=opts, answer=ans, explain=exp,
        whyWrong=["Remaining options break grain, scale, or governance."],
        ref="https://spark.apache.org/docs/latest/api/python/", tags=["pyspark","gold","dq"], month=2)

# code interpretation
add(bank="dbx", domain="3 Transformation", topic="PySpark", difficulty="Hard", type="mcq",
    stem="What does this aggregation compute?",
    code='daily = billing_df.groupBy("billing_date").agg(F.sum("amount").alias("rev"), F.countDistinct("billing_id").alias("invoices"))',
    options=["Sum of amounts and distinct invoice ids per day","Sum of invoice ids","Count of patients only","Cartesian join"],
    answer=0, explain="groupBy date, sum measure, countDistinct business keys.",
    whyWrong=["sum of ids is meaningless; patient count is a different grain."],
    ref="https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.functions.count_distinct.html",
    tags=["pyspark"], month=2)

jobs_t = [
("A pipeline should rerun a failed ingest task 3 times then skip downstream if still failing. Feature?",
 ["Lakeflow Jobs retries + conditional/if-else task flow","VACUUM","Delta Sharing","Broadcast hint"], 0, "Control flows: retries, branching, looping."),
("Task A notebook ingest → Task B SQL gold → Task C dashboard refresh. How are dependencies expressed?",
 ["DAG task dependencies in Lakeflow Jobs","Alphabetical notebook names","Unity Catalog comments","Random"], 0, "Notebook, SQL, dashboard, pipeline tasks in a DAG."),
("Run the job when new files land, not at 2am blindly. Trigger?",
 ["File arrival trigger","Only manual click forever","ABAC","Liquid clustering"], 0, "Triggers: scheduled, file arrival, table update."),
("Gold job should start only after silver table version updates. Trigger family?",
 ["Table update / data-driven trigger","CPU interrupt from laptop lid","QMC reload","Git blame"], 0, "Choose time-based vs data-driven."),
("A downstream task should run only if an upstream quality task succeeds. Pattern?",
 ["Conditional tasks on task status","Delete the cluster mid-run","GRANT ALL TO PUBLIC","repartition(0)"], 0, "Branching on success/failure."),
]
for n in range(80):
    stem, opts, ans, exp = jobs_t[n % len(jobs_t)]
    add(bank="dbx", domain="4 Lakeflow Jobs", topic="Lakeflow Jobs", difficulty=cycle(n,["Easy","Medium","Hard"]),
        stem=f"{cycle(n,CO)} ops team: {stem}", options=opts, answer=ans, explain=exp,
        whyWrong=["Unrelated platform features."],
        ref="https://docs.databricks.com/jobs/", tags=["jobs","lakeflow"], month=3)

cicd_t = [
("Developers commit notebook changes, branch, and open PRs from the workspace. Feature name (2026)?",
 ["Git Folders (formerly Repos)","Delta Live CSV","QVD folders","Eventhouse"], 0, "Git Folders workflow is on the CI/CD section."),
("Same job definition, different warehouse_id per dev/test/prod. Mechanism?",
 ["Automation Bundle variables and target overrides","Hardcode prod id in every notebook","Email the ID","SCD2"], 0, "DAB/Automation Bundle variables."),
("Package Jobs + Lakeflow Spark Declarative Pipelines as code and deploy via CI. What?",
 ["Declarative Automation Bundles (formerly Databricks Asset Bundles)","Copy-paste jobs in UI only","Export dashboard PNG","NPrinting"], 0, "DABs package and promote assets."),
("CI pipeline should validate bundle then deploy. CLI family?",
 ["Databricks CLI bundle validate/deploy","ftp.exe","Qlik CLI only","kubectl on the driver"], 0, "CLI for bundles in automated CI/CD."),
]
for n in range(50):
    stem, opts, ans, exp = cicd_t[n % len(cicd_t)]
    add(bank="dbx", domain="5 CI/CD", topic="CI/CD", difficulty=cycle(n,["Easy","Medium","Hard"]),
        stem=f"{cycle(n,CO)} platform team: {stem}", options=opts, answer=ans, explain=exp,
        whyWrong=["UI-only or non-Databricks tools."],
        ref="https://docs.databricks.com/dev-tools/bundles/index.html", tags=["dabs","git"], month=3)

tr_t = [
("Most tasks 30s, one task 10 min; max shuffle read >> median. First class of problem?",
 ["Data skew","Missing GRANT","Wrong color theme","Expired Qlik license"], 0, "Spark UI skew pattern."),
("Stage writes lots of data to disk during shuffle. Term?",
 ["Disk spilling","Delta Sharing","Z-ordering the driver JVM","ABAC"], 0, "Spill is a Spark UI metric."),
("Job got slower vs last 14 days. Where to compare baselines in product UI?",
 ["Lakeflow Jobs run history","Photoshop timeline","QMC audit only","Git reflog only"], 0, "Run history vs historical baselines."),
("Upstream task failed so gold never started. Where do you see blockers?",
 ["Jobs DAG/task graph statuses","UC mask function","COPY INTO format","Broadcast join hint"], 0, "Jobs UI DAG blockers."),
("Tables benefit from automatic OPTIMIZE/VACUUM/stats. Feature?",
 ["Predictive optimization","Manual dropping the catalog","Print schema","crossJoin"], 0, "PO on the outline."),
("Flexible clustering keys instead of rigid partitions for many filter columns?",
 ["Liquid Clustering","Storing CSV on the driver","NPrinting","SCD1 only"], 0, "Liquid Clustering features."),
("Cluster never starts after a library change. Likely class?",
 ["Library conflict / init script / cloud quota / misconfig","Too much GRANT SELECT","Too few flashcards","KQL datetime"], 0, "Diagnose startup, libraries, OOM."),
("Executor OOM vs driver OOM: collect() of a full fact typically hits?",
 ["Driver OOM","UC metastore CPU","OneLake shortcut","Eventstream"], 0, "collect pulls to driver."),
]
for n in range(70):
    stem, opts, ans, exp = tr_t[n % len(tr_t)]
    add(bank="dbx", domain="6 Troubleshooting", topic="Monitoring/Perf", difficulty=cycle(n,["Medium","Hard","Expert","Scenario"]),
        stem=f"{cycle(n,CO)}: {stem}", options=opts, answer=ans, explain=exp,
        whyWrong=["Symptoms mapped to the wrong subsystem."],
        ref="https://docs.databricks.com/compute/spark-ui.html", tags=["spark ui","liquid","po"], month=4)

gov_t = [
("Databricks owns the data files lifecycle for a table in UC. Type?",
 ["Managed table","External table on random S3 with no UC","View","DAB"], 0, "Managed vs external."),
("Files stay in customer-owned storage; UC tracks metadata. Type?",
 ["External table","Managed only","Flashcard","SQL warehouse"], 0, "External tables."),
("Analyst group needs read on all current and future tables in schema sales. Typical privilege pattern (conceptually)?",
 ["GRANT SELECT on schema (and USE) to the group — follow current UC privilege model","GRANT MODIFY to PUBLIC","DENY USE CATALOG to admins","Drop the schema nightly"], 0, "GRANT/REVOKE/DENY to users/groups/service principals."),
("Hide SSN but allow analytics on other columns. Feature?",
 ["Column mask","COPY INTO","Liquid clustering","File arrival trigger"], 0, "Column-level masking."),
("Users see only their region's rows. Feature?",
 ["Row filter / RLS","union all","Broadcast join","Git squash"], 0, "Row-level security."),
("Central policies for row filter + mask by attributes/tags rather than copying SQL on every table. Feature?",
 ["Unity Catalog ABAC policies","Predictive optimization","Auto Loader notification","Photon color"], 0, "ABAC on May 2026 outline."),
("Service principal runs prod jobs. Grants should be applied to?",
 ["The service principal (and groups), not a human user","Everyone's personal PAT in a notebook","The Spark UI","Qlik service account on a VM only"], 0, "Principals include service principals."),
]
for n in range(80):
    stem, opts, ans, exp = gov_t[n % len(gov_t)]
    add(bank="dbx", domain="7 Governance", topic="Unity Catalog", difficulty=cycle(n,["Easy","Medium","Hard","Scenario"]),
        stem=f"{cycle(n,CO)} security: {stem}", options=opts, answer=ans, explain=exp,
        whyWrong=["Confuses performance features with security features."],
        ref="https://docs.databricks.com/data-governance/unity-catalog/index.html", tags=["uc","abac","rls"], month=3)

# ---- DP-700 bank ----
d1 = [
("Configure Spark settings at Fabric workspace level for default lakehouse runtime. Where?",
 ["Workspace Spark settings","Qlik NPrinting","Delta Sharing recipient","GitHub Issues only"], 0, "Configure Spark workspace settings."),
("Business domains group workspaces for federated governance. Feature?",
 ["Fabric domains","Liquid clustering","COPY INTO","LangGraph"], 0, "Domain workspace settings."),
("Default OneLake settings and storage behavior for the workspace. Where?",
 ["OneLake workspace settings","Eventhouse caching only","ABAC in Databricks UC as the only control","PowerPoint"], 0, "OneLake workspace settings."),
("Complex Python DAGs beyond Data Factory. Workspace feature on Jul 2026 blueprint?",
 ["Apache Airflow workspace settings / Fabric Airflow","NPrinting","QVD generator","Photon"], 0, "Airflow workspace settings."),
("Promote lakehouse from DEV to PROD with review. Feature?",
 ["Deployment pipelines","Manual download PBIX only","VACUUM","Broadcast"], 0, "Deployment pipelines."),
("SQL database/warehouse as code. Artifact?",
 ["Database projects + Git","Random CSV in Teams","Flashcards","SCD2 hash only"], 0, "Implement database projects."),
("Workspace Admin vs Contributor vs Viewer for a contractor. Control plane?",
 ["Workspace-level access controls","Spark UI","KQL bin()","Auto Loader"], 0, "Workspace-level ACLs."),
("Restrict a single semantic model without opening the whole workspace. Control?",
 ["Item-level permissions","Drop OneLake","Disable Git","Predictive optimization"], 0, "Item-level access."),
("Analysts see only their cost center rows in the warehouse. Feature?",
 ["RLS","COPY INTO","File notification","DAB targets"], 0, "RLS."),
("Hide salary column from HR-except groups. Feature?",
 ["CLS / object-level / masking patterns in Fabric","unionByName","Eventstream operator","Git squash"], 0, "Column/object security."),
("Files in OneLake folders need ACLs beyond table RLS. Feature family?",
 ["Folder/file-level and OneLake security","Spark AQE","Materialized view refresh only","LangChain"], 0, "Folder/file + OneLake security."),
("Mask PAN in query results. Feature?",
 ["Dynamic data masking","Liquid clustering","Broadcast join","Medallion bronze"], 0, "DDM."),
("MIP labels on items for compliance. Feature?",
 ["Sensitivity labels","shuffle partitions","Delta log JSON","Watermark"], 0, "Sensitivity labels."),
("Mark a lakehouse as trusted for the org. Action?",
 ["Endorse items","Delete audit logs","GRANT ALL PUBLIC","repartition(1) always"], 0, "Endorse items."),
("Investigate who changed a pipeline yesterday. Source?",
 ["Fabric audit logs","Qlik script log only","Spark UI SQL tab only","Flashcard known pile"], 0, "Audit logs."),
("Low-code ingest of 20 Excel files vs 8TB PySpark CDC vs orchestration of 15 activities. Choice skill?",
 ["Choose Dataflow Gen2 vs notebook vs pipeline","Always notebooks","Always Dataflows","Always Eventhouse"], 0, "Orchestration choice is Domain 1."),
("Run pipeline when a lakehouse table updates. Trigger type?",
 ["Event-based / data-driven trigger","Only monthly calendar invite","ABAC","ZORDER"], 0, "Schedules and event-based triggers."),
("Pipeline expression uses @pipeline().parameters.StartDate. Concept?",
 ["Parameters and dynamic expressions","Liquid clustering","UC ABAC","Token embeddings"], 0, "Parameters and expressions with notebooks/pipelines."),
]
for n in range(170):
    stem, opts, ans, exp = d1[n % len(d1)]
    add(bank="dp700", domain="D1 Manage", topic="Fabric management", difficulty=cycle(n,["Beginner","Intermediate","Advanced","Expert","Scenario"]),
        stem=f"{cycle(n,CO)}: {stem}", options=opts, answer=ans, explain=exp,
        whyWrong=["Databricks-only or unrelated features presented as Fabric controls."],
        ref="https://learn.microsoft.com/en-us/fabric/", tags=["fabric","security","cicd"], month=5)

d2 = [
("Nightly full dump vs MERGE on watermark vs Eventstream. Design skill?",
 ["Full vs incremental vs streaming load patterns","Always full dump 50TB","Always streaming even for yearly budgets","Print CSV"], 0, "Design loading patterns."),
("Build star schema facts/dims in Warehouse. Prep includes?",
 ["Keys, grain, late-arriving, SCD","Skipping dates","Storing JSON blobs as facts without grain","UDFs on the driver"], 0, "Prepare data for dimensional model."),
("Keep a single copy of data in a lakehouse while Warehouse needs it. Mechanism?",
 ["Shortcuts (and related SQL endpoint patterns)","Nightly FTP of QVDs","Printouts","GPU copy"], 0, "OneLake shortcuts."),
("Near-real-time replica of Azure SQL operational data into Fabric with low engineering. Feature?",
 ["Mirroring","Manual dump to USB","NPrinting","Git rebase"], 0, "Implement mirroring."),
("Transform 200MB Excel vs 4TB Delta vs time-series KQL. Choose engine?",
 ["Dataflows vs PySpark notebooks vs KQL vs T-SQL by scale/shape","Always Dataflows Gen2","Always KQL for Excel","Always T-SQL for IoT at 100k events/s without Eventhouse"], 0, "Choose transformation engine."),
("Deduplicate orders, fill missing status, handle late facts. Domain 2 skill?",
 ["Handle duplicate, missing, late-arriving data","Drop gold","Disable OneLake","Train an LLM on bronze PII"], 0, "Late/duplicate/missing."),
("Eventstream vs Spark structured streaming vs KQL ingestion. Skill?",
 ["Choose streaming engine","Always batch COPY INTO for fraud at 10ms","Qlik timer","Flashcards"], 0, "Choose streaming engine."),
("RTI: native Eventhouse tables vs OneLake shortcuts; query acceleration option. Exam topics?",
 ["Native vs shortcuts; query acceleration vs standard shortcuts","Only Spark UI spill","Only DAB CLI","Only SCD1"], 0, "RTI shortcut acceleration is on Jul 2026 guide."),
("Tumbling windows in KQL for 5-minute error rates. Feature?",
 ["KQL windowing functions","COPY INTO","Git Folders","Column mask"], 0, "Create windowing functions."),
("Denormalize dimensions into a gold wide table for Power BI import. Pattern?",
 ["Denormalize / star-style gold","3NF 20-join semantic model as a moral requirement","Store only images","ABAC"], 0, "Denormalize and aggregate."),
]
for n in range(170):
    stem, opts, ans, exp = d2[n % len(d2)]
    add(bank="dp700", domain="D2 Ingest/Transform", topic="Fabric ingest", difficulty=cycle(n,["Beginner","Intermediate","Advanced","Expert","Scenario"]),
        stem=f"{cycle(n,CO)}: {stem}", options=opts, answer=ans, explain=exp,
        whyWrong=["Wrong engine or copy-heavy anti-pattern."],
        ref="https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/dp-700", tags=["shortcuts","mirroring","kql"], month=5)

d3 = [
("Pipeline failed on a Copy activity to lakehouse. First operational skill?",
 ["Identify and resolve pipeline errors using monitoring","Delete the tenant","Increase LLM temperature","VACUUM RETAIN 0"], 0, "Pipeline error resolution."),
("Dataflow Gen2 refresh fails on a privacy level. Skill?",
 ["Troubleshoot Dataflow Gen2 errors","Enable GPU","Grant UC on Databricks by reflex","Ignore"], 0, "Dataflow errors are on the blueprint."),
("Notebook Spark OOM in Fabric. Skill?",
 ["Identify notebook errors; then optimize Spark","Always switch to Dataflow","Always Eventhouse","Always mirroring"], 0, "Notebook monitoring + Spark optimize."),
("Eventhouse ingest latency high; Eventstream dropped events. Skills?",
 ["Monitor/resolve Eventhouse and Eventstream errors; optimize RTI","Convert to Excel","Disable OneLake security","Use NPrinting"], 0, "RTI troubleshooting."),
("T-SQL query scans whole warehouse fact. Skill?",
 ["Optimize warehouse + query performance","Add more sensitivity labels","Train embeddings on the query text","COPY INTO from /dev/null"], 0, "Warehouse and query optimization."),
("Lakehouse table has too many tiny Parquet files. Skill?",
 ["Optimize lakehouse table (maintenance/V-Order/compaction patterns)","Create 10 more shortcuts to the same tiny files","ABAC","Git tag"], 0, "Optimize a lakehouse table."),
("Semantic model refresh fails after Gold change. Monitor what?",
 ["Semantic model refresh + alerts","Only Spark UI on a different cloud","QMC","DAB validate on a laptop with no Fabric"], 0, "Monitor semantic refresh."),
("Need Teams/email when pipeline SLA breaches. Feature?",
 ["Alerts","Liquid clustering","countDistinct","LangGraph memory"], 0, "Configure alerts."),
]
for n in range(170):
    stem, opts, ans, exp = d3[n % len(d3)]
    add(bank="dp700", domain="D3 Monitor/Optimize", topic="Fabric ops", difficulty=cycle(n,["Beginner","Intermediate","Advanced","Expert","Scenario"]),
        stem=f"{cycle(n,CO)}: {stem}", options=opts, answer=ans, explain=exp,
        whyWrong=["Fixes unrelated layers."],
        ref="https://learn.microsoft.com/en-us/fabric/data-engineering/data-engineering-overview", tags=["monitor","optimize"], month=6)

# ---- Core bank month 1-2, genai ----
core = [
("In Qlik you used incremental QVD + Exists. Closest lakehouse pattern?",
 ["MERGE/CDC into Delta with watermarks","Reload every table from scratch daily as a virtue","Store QVD in OneLake without transactions","Print PDF"], 0, "Incremental Delta load.", "core", "Incremental", 1),
("Window function LAG(status) to detect SCD2 change is closest to which Qlik idea?",
 ["Peek/Previous on sorted resident","Set Analysis totals on all rows","NPrinting cycle","Section access"], 0, "LAG ≈ Previous.", "core", "SQL", 1),
("Spark action vs transformation?",
 ["Transformations lazy; actions compute","Both always compute immediately","Actions are only SQL GRANT","Transformations write Gold"], 0, "Lazy evaluation.", "core", "Spark", 2),
("Why avoid Python UDFs for simple upper()?",
 ["Catalyst can't optimize them well; use built-in functions","They are always faster","They create UC catalogs","They replace Liquid clustering"], 0, "UDF cost.", "core", "PySpark", 2),
("RAG retrieves from where for 'why did sales drop?'",
 ["Governed Gold + metric docs, then LLM narrates","The model's training memory of another company","Bronze PII dumps without ACL","Random tweets"], 0, "Enterprise RAG on Gold.", "core", "GenAI", 7),
("Hallucination control for NL2SQL?",
 ["Allow-list schemas, read-only, validate SQL, cite numbers","Let the model DDL drop tables","Disable logging for privacy theater","Fine-tune on passwords"], 0, "Tool sandboxing.", "core", "GenAI", 7),
]
for stem, opts, ans, exp, bank, topic, month in core:
    add(bank=bank, domain="Core", topic=topic, difficulty="Medium", stem=stem, options=opts, answer=ans, explain=exp,
        whyWrong=["Insecure or non-scalable options."], ref="https://spark.apache.org/docs/latest/", tags=[topic.lower()], month=month)

for n in range(80):
    add(bank="core", domain="Core", topic="SQL/Python", difficulty=cycle(n,["Easy","Medium"]),
        stem=f"SQL practice {n+1}: a query joins fact to dim on a non-unique key and revenue doubles. Root cause?",
        options=["Fan-out join / wrong grain","Photon disabled","Too many flashcards","Missing Mermaid"],
        answer=0, explain="Duplicate dimension keys explode facts — same as Qlik cartesian.",
        whyWrong=["UI features do not duplicate grain."], ref="https://learn.microsoft.com/en-us/sql/t-sql/queries/select-transact-sql",
        tags=["sql"], month=1)

# True/false + multi
for n, stem in enumerate([
    "Delta time travel can restore a table version after a bad MERGE (within retention).",
    "Managed UC tables keep data in a Databricks-managed location by default.",
    "Fabric shortcuts always physically duplicate every byte.",
    "DP-700 expects you to choose among Dataflow Gen2, pipelines, and notebooks.",
    "Lakeflow Jobs can trigger on file arrival.",
    "Python UDFs are the fastest way to do a join.",
    "ABAC can centralize row filters and column masks in UC.",
    "Mirroring is ideal for every 50TB unstructured video lake.",
]):
    ans = 0 if n not in (2,5,7) else 1
    add(bank="core", domain="Core", topic="True/False", difficulty="Easy", type="mcq",
        stem=stem+" True or false?",
        options=["True","False","Not applicable","Only in Qlik"],
        answer=0 if n not in (2,5,7) else 1,
        explain="Shortcuts do not always copy; UDFs are slow; mirroring targets operational DBs not all unstructured video.",
        whyWrong=["Read the current docs for nuance (retention, managed vs external)."],
        ref="https://docs.databricks.com/", tags=["tf"], month=3)

dump("quizzes.js", {"quizzes": Q})
print("quizzes", len(Q), "dbx", sum(1 for x in Q if x["bank"]=="dbx"), "dp", sum(1 for x in Q if x["bank"]=="dp700"))
