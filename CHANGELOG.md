# Changelog

All notable changes to the **WhatsApp Automation System** ("AutoWA") will be documented in this file.

The format is inspired by **Keep a Changelog** and follows semantic versioning.

---

# [v2.1.0 Beta] — Monitoring & Modularization (Unreleased)

## ✨ Major Features

* Added **Analytics Module** for structured tracking of session-based throughput metrics (all, current, and last sessions)
* Added **Health Monitoring System** to isolate minor error detection and comprehensively display system health status
* Introduced **JSONL Structured Logging** into the core engine for enhanced diagnostic monitoring and automated log analysis
* Introduced **App Modularization**, drastically decoupling the GUI into targeted components (analytics, monitoring, recovery event handlers) away from the main application entry point

---

# [v2.0.0] — Core System Refactor
## 🚨 Breaking Changes

* Replaced Excel-based workflow with **CSV-based job system**
* Introduced strict **schema-driven architecture**
* Decoupled system into:

  * Core Engine
  * GUI Layer
  * Automation Layer
* Removed direct GUI → Automation interaction (now routed through core runner)

---

## ✨ Major Features

* Introduced **job execution engine**

  * `execute_jobs(csv_path)` as single entry point
* Added **template-based messaging system**

  * Supports multiple variants per message key
  * Randomized message selection
* Introduced **document handling modes**

  * `none`
  * `fixed`
  * `variable`
* Added **config-driven execution behavior**

---

## 🧠 System Architecture

* Added full system contract:

  * `docs/system_contract.md`
  * `contracts/core_api.md`
  * `contracts/error_taxonomy.md`
* Introduced strict schema validation:

  * `schemas/jobs.schema.md`
  * `schemas/messages.schema.json`
  * `schemas/config.schema.json`

---

## 📦 Data Model Changes

* New CSV schema:

  * `message_mode` replaces message type logic
  * `doc_mode` replaces attach_doc flag
* Removed:

  * `message_type`
  * `attach_doc`
* Added:

  * `status`
  * `status_message`

---

## ⚙️ Engine Capabilities

* Job validation before execution
* Message resolution with placeholders
* Template variant randomization
* Document resolution logic
* Execution stats reporting

---

## 🖥️ GUI Changes

* Replaced Excel input with CSV
* Added template management system
* GUI now triggers:

  * `core.runner.execute_jobs()`
* Removed direct automation calls

---

## 🔁 Internal Improvements

* Standardized error taxonomy
* Defined retry vs non-retry errors
* Introduced execution stats tracking

---

## ⚠️ Migration Notes

* Old Excel sheets are no longer supported
* Templates must be defined in:

  * `config/messages.json`
* Jobs must follow:

  * `schemas/jobs.schema.md`

---

# [v1.5.1 Alpha]

## 🐛 Fixes

* Fixed icon capture issues
* Fixed break popup behavior

---

# [v1.5.0 Alpha]

## ✨ Features

* Introduced icon capture system

---

# [v1.4.0]

## ✨ Features

* Auto switch application language to English

---

# [v1.3.1]

## 🐛 Fixes

* Improved handling when WhatsApp restarts (partial fix)
* Attempted progress save on cancel/exit
* Disabled buttons when invalid state detected
* Fixed pause trigger when all jobs completed

---

# [v1.3.0]

## ✨ Features

* Added execution stats in results popup:

  * sent
  * pending
  * failed
* Added progress and timing popup

---

# [v1.2.0]

## ✨ Features

* Support sending different document types (permits + seglat) in one sheet

---

# [v1.1.0]

## 🐛 Fixes

* Fixed WhatsApp number detection issues
* Fixed number deletion bug
* Improved UI stability detection

## ✨ Features

* Added WhatsApp Business assets support

---

# Planned (Not Released)

## 🐛 Bugs & Fixes

* Improve WhatsApp restart recovery (current solution unstable)
* Ensure reliable progress saving on exit
* Fix batch switching logic edge cases

---

## ✨ Minor Features

* Handle already existing WhatsApp numbers
* Improve resume/continue progress system
* Persist last used WhatsApp account across sessions

---

## 🚀 Major Features

* System health monitoring dashboard
* Error logging + alert system
* Icon capture & management system (in progress)

---
