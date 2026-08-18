import json, pathlib, sys
sys.path.insert(0, "/workspace/tools")
from jsdump import dump

dump("meta.js", {
  "meta": {
    "name": "PathForge SSOT",
    "audience": "Experienced Qlik/BI engineer (12+ years) transitioning to Senior Data & AI Analytics Consultant / Data & AI Architect",
    "verified": "2026-08-18",
    "disclaimer": "Structured preparation around official blueprints. Does not guarantee certification."
  },
  "roadmap": [
    {"title": "Month 1 — Foundations", "goal": "Python, advanced SQL, Git, lakehouse vocabulary, incremental/CDC/SCD using your ETL instincts.",
     "outcomes": ["Write production-grade Python for ingestion", "Window functions and MERGE as Qlik incremental equivalents", "Design star vs lakehouse without relearning BI basics", "Ship e-commerce pipeline v1"]},
    {"title": "Month 2 — Spark + PySpark", "goal": "Think in distributed DataFrames the way you once thought in Qlik resident loads.",
     "outcomes": ["Explain jobs/stages/tasks", "Optimize joins, skew, shuffle", "Translate Qlik transforms to PySpark", "Batch + streaming mental model"]},
    {"title": "Month 3 — Databricks platform", "goal": "Delta, medallion, Unity Catalog, Lakeflow on the May 2026 associate exam stack.",
     "outcomes": ["Bronze/Silver/Gold with DQ", "Auto Loader vs COPY INTO vs Lakeflow Connect", "Jobs DAG, Git Folders, DABs", "UC grants, RLS, masking, ABAC"]},
    {"title": "Month 4 — Databricks certification", "goal": "Objective-mapped practice, mocks, Spark UI, Liquid Clustering, predictive optimization.",
     "outcomes": ["500+ original questions", "5 mock exams", "30-day bootcamp", "Weak-topic closure"]},
    {"title": "Month 5 — Microsoft Fabric", "goal": "DP-700 as of 21 Jul 2026: workspace, OneLake, lakehouse/warehouse, DF, Dataflows Gen2, mirroring, RTI, Airflow, security, CI/CD.",
     "outcomes": ["Choose lakehouse vs warehouse vs Eventhouse", "Pipelines vs Dataflows vs notebooks", "Shortcuts, mirroring, KQL windows", "Git + deployment pipelines"]},
    {"title": "Month 6 — DP-700 + GenAI + Capstone", "goal": "Pass-prep plus AI systems on enterprise data, not academic ML.",
     "outcomes": ["500+ DP-700 questions", "RAG/agent architecture on Gold", "NL-to-SQL with governance", "Capstone + freelance packaging"]}
  ],
  "dbxBlueprint": [
    {"name": "1. Databricks Intelligence Platform", "weight": "6%", "objectives": [
      "Core components: architecture, Delta Lake, Unity Catalog",
      "Compute services: characteristics, limits, cost models, workload fit"]},
    {"name": "2. Data Ingestion and Loading", "weight": "21%", "objectives": [
      "Batch, streaming, incremental; files, Lakeflow Connect standard/managed",
      "COPY INTO from ADLS/S3/GCS into UC tables",
      "Auto Loader schema enforcement/evolution; directory listing vs file notification",
      "Lakeflow Connect enterprise sources",
      "JDBC/ODBC/REST in notebooks orchestrated by Lakeflow Jobs",
      "Choose Auto Loader vs Connect vs partner connectors",
      "Semi-structured/unstructured JSON nested into Delta"]},
    {"name": "3. Data Transformation and Modeling", "weight": "22%", "objectives": [
      "Bronze→Silver cleaning with PySpark/SQL",
      "Joins including broadcast, multi-key, cross, union/union all",
      "Column/row ops, explode",
      "Dedup and aggregations (count, approx_count_distinct, mean, summary)",
      "Tuning: shuffle.partitions, default.parallelism, executor/driver memory, autoBroadcastJoinThreshold",
      "Gold: materialized views, views, streaming tables, tables for BI",
      "Data quality checks on Silver/Gold"]},
    {"name": "4. Working with Lakeflow Jobs", "weight": "16%", "objectives": [
      "Retries, conditional tasks, branching, looping",
      "Notebook, SQL, dashboard, pipeline tasks and DAG dependencies",
      "Triggers: scheduled, file arrival, table update",
      "Time-based vs data-driven triggers"]},
    {"name": "5. Implementing CI/CD", "weight": "10%", "objectives": [
      "Git Folders (formerly Repos): branches, commit, PR",
      "Automation Bundle variables/overrides across dev/test/prod",
      "Deploy DABs (formerly Databricks Asset Bundles) for Jobs and Spark Declarative Pipelines",
      "Databricks CLI validate/deploy/manage bundles"]},
    {"name": "6. Troubleshooting, Monitoring, and Optimization", "weight": "10%", "objectives": [
      "Jobs run history vs baselines",
      "Jobs UI statuses, DAG blockers, failure rates",
      "Spark UI: skew, shuffle, disk spill",
      "Liquid Clustering and predictive optimization",
      "Cluster startup failures, library conflicts, OOM"]},
    {"name": "7. Governance and Security", "weight": "15%", "objectives": [
      "Managed vs external tables; convert/CRUD",
      "GRANT/REVOKE/DENY on users, groups, service principals",
      "Column masking and row-level security",
      "Unity Catalog ABAC for centralized row filter and mask"]}
  ],
  "dp700Blueprint": [
    {"name": "1. Implement and manage an analytics solution", "weight": "30–35%", "objectives": [
      "Spark, domain, OneLake, Apache Airflow workspace settings",
      "Version control, database projects, deployment pipelines",
      "Workspace/item/RLS/CLS/OLS/folder security, DDM, sensitivity labels, endorse, audit logs, OneLake security",
      "Choose Dataflow Gen2 vs pipeline vs notebook; schedules and event triggers; parameters and dynamic expressions"]},
    {"name": "2. Ingest and transform data", "weight": "30–35%", "objectives": [
      "Full vs incremental vs streaming loads; dimensional model prep",
      "Choose store; Dataflows/notebooks/KQL/T-SQL; shortcuts; mirroring; pipelines; PySpark/SQL/KQL; denormalize; aggregate; duplicates/missing/late data",
      "Streaming engine choice; native tables vs shortcuts; query acceleration; Eventstreams; Spark structured streaming; KQL; windowing"]},
    {"name": "3. Monitor and optimize an analytics solution", "weight": "30–35%", "objectives": [
      "Monitor ingestion, transformation, semantic model refresh, alerts",
      "Resolve pipeline, Dataflow Gen2, notebook, Eventhouse, Eventstream, T-SQL, shortcut errors",
      "Optimize lakehouse table, pipeline, warehouse, Eventstreams/Eventhouses, Spark, queries"]}
  ],
  "changelog": [
    {"date": "2026-05-04", "exam": "Databricks Data Engineer Associate",
     "change": "New live exam: 7 sections. Lakeflow Jobs/Connect/Spark Declarative Pipelines; Git Folders; Declarative Automation Bundles (formerly DABs/Asset Bundles); Liquid Clustering; predictive optimization; UC ABAC. Delta Sharing and Lakehouse Federation are not listed on this associate outline (they appeared on the pre-May-4 2026 outline).",
     "impact": "Study May 2026 PDF, not 2024/2025 five-domain blogs. Do not memorize retired Delta Sharing-heavy associate blueprints as if they were current."},
    {"date": "2026-03", "exam": "Databricks Data Engineer Associate",
     "change": "Databricks published dual exam guide (current until 3 May 2026 vs new on 4 May 2026) at databricks.com/sites/default/files/2026-03/...",
     "impact": "If sitting before 4 May 2026 use the older five-section outline in that PDF; this artifact defaults to the May 4 2026+ outline because the six-month window extends past that date."},
    {"date": "2026-07-21", "exam": "DP-700",
     "change": "Skills measured updated (Microsoft study guide last dated 2026-05-31, changelog compares pre/post 21 Jul 2026). Workspace settings now explicitly include Apache Airflow; OneLake security and query acceleration for RTI shortcuts called out.",
     "impact": "Follow https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/dp-700 over third-party 2024 DP-700 dumps."}
  ]
})
print("meta done")
