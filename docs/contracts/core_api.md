# Core Engine API Contract

This document defines how external modules (GUI, CLI) interact with the automation engine.

---

# Entry Point

```
execute_jobs(csv_path)
```

Located in:

```
core/runner.py
```

---

# Function

```
execute_jobs(csv_path: str) -> ExecutionStats
```

Responsibilities:

1. Load jobs
2. Validate jobs
3. Resolve templates
4. Resolve documents
5. Execute automation
6. Update job status
7. Save results

---

# Supporting APIs

## Load Jobs

```
load_jobs(csv_path) -> List[ContactJob]
```

---

## Validate Job

```
validate_job(job) -> ValidationResult
```

---

## Resolve Message

```
resolve_message(job, templates) -> str
```

---

## Resolve Document

```
resolve_document(job, config) -> Optional[str]
```

---

# Automation Call

Runner must call:

```
WAController.send(number, message, document)
```

---

# Execution Stats

Return object example:

```
{
  "total": 100,
  "success": 94,
  "failed": 6
}
```

---

# Stability Rules

The following functions are **stable public interfaces**:

```
execute_jobs
load_jobs
validate_job
resolve_message
resolve_document
```

Breaking these functions requires contract version upgrade.
