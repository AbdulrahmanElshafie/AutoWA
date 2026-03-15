# WhatsApp Automation System – System Contract

## Purpose

This document defines the **system architecture contract** for the WhatsApp Automation System.
All implementation must follow the structure and interfaces defined here.

This contract ensures multiple developers or AI agents can work independently without introducing incompatibilities.

---

# Architecture Overview

The system is divided into **three independent layers**.

```
GUI Layer
    ↓
Core Engine
    ↓
Automation Layer
```

### GUI Layer

Responsible only for:

* user interaction
* displaying progress
* editing templates
* selecting files
* triggering execution

GUI **must never interact directly with automation logic**.

Allowed entry point:

```
core.runner.execute_jobs()
```

---

### Core Engine

Responsible for:

* loading jobs
* validating jobs
* resolving templates
* resolving documents
* executing jobs through the automation layer
* updating job status

Core must remain **independent from GUI frameworks**.

---

### Automation Layer

Responsible for:

* desktop automation
* WhatsApp Web interaction
* sending messages
* sending documents

Automation must accept **already-resolved instructions** from the core.

Automation must not parse CSV files or templates.

---

# Execution Workflow

```
jobs.csv
   ↓
job_loader
   ↓
validator
   ↓
message resolver
   ↓
document resolver
   ↓
runner
   ↓
WAController
   ↓
status update
```

---

# File Responsibilities

## Core Engine

```
core/
    job_model.py
    job_loader.py
    validator.py
    resolver.py
    runner.py
```

---

## Automation

```
automation/
    Controller.py
    WAController.py
```

---

## GUI

```
gui/
    layout.py
    events.py
    helpers.py
```

---

# Contract Rules

1. GUI must not call WAController directly.
2. Automation must not read CSV files.
3. Core must not import GUI modules.
4. Core communicates with automation using **resolved message and document objects only**.

---

# Contract Versioning

Current contract version:

```
v1.0
```

Breaking changes require:

* schema update
* contract documentation update
* version increment

---

# Stability Guarantees

Stable interfaces:

```
core.runner.execute_jobs()
core.job_loader.load_jobs()
core.validator.validate_job()
core.resolver.resolve_message()
core.resolver.resolve_document()
```

These interfaces must remain backward compatible unless contract version changes.
