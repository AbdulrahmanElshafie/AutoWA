# Changelog

All notable changes to the **WhatsApp Automation System** ("AutoWA") will be documented in this file.

The format is inspired by **Keep a Changelog** and follows semantic versioning.

---

# [v2.2.0] - UI Recovery, Theming, and Image Operations

## ✨ Major Features

* **Icon Management & UI Recovery System**: A dedicated module allowing users to delete redundant icon screenshots to maintain system speed. Also introduces a powerful "Recovery" feature where missing UI elements trigger a full-screen snapshot, enabling users to manually crop and heal the bot's vision seamlessly via the interface. This allows it to support multiple WhatsApp web styles and languages. 
* **Global Stylization & Multi-Language Support**: The application now gracefully maps secondary assets and configuration fallbacks, actively supporting additional languages and Light Mode styling out-of-the-box.
* **System Health Monitoring Dashboard**: A comprehensive dashboard showing system health evaluations, catching recent errors, and sorting them by severity based on type and frequency (while presenting logs and tracebacks).
* **Error Logging & Alert System**: Extensive logging per session for rapid analytics and deep-dive error logs to diagnose UI bugs efficiently. The recent alerts section natively expands to reveal underlying error details and tracebacks when clicked.

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

* Fixed icon capture issues => Capture the screen on issues and save it correctly 
* Fixed break popup behavior => UI design and make sure it's displayed correctly 

---

# [v1.5.0 Alpha]

## ✨ Features

* Introduced icon capture system (Beta)

---

# [v1.4.0]

## ✨ Features

* Auto switch application language to English => PyAutoGUI only supports typing and works smoothly when the system is in English so forced the system to be on English mode (Need to notify the user)

---

# [v1.3.1]

## 🐛 Fixes

* Improved handling when WhatsApp restarts (partial fix) => Close WA and opens a new tab to send msg correctly 
* Disabled buttons when invalid state detected => UI btns status fixed to match the app status
* Fixed pause trigger when all jobs completed => UI btns status fixed to match the app status

---

# [v1.3.0]

## ✨ Features

* Added execution stats in results popup to alert user with results after finishing the batch:
  * sent
  * pending
  * failed
* Added progress and timing popup to be displayed on batch break 

---

# [v1.2.0]

## ✨ Features

* Support sending different document types (permits + seglat) in one sheet

---

# [v1.1.0]

## 🐛 Fixes

* Fixed WhatsApp number detection issues => (UI Stability function)
* Fixed number deletion bug => Numbs must be deleted after finish (updated icons)
* Improved UI stability detection => check UI stability function that waits for the UI to finish animation before checking icon

## ✨ Features

* Added WhatsApp Business assets support => Adding the WA Business icons imgs
* Non-English text is being sent smoothly => Copying each word and pasting it to simulate the human typing event while sending the msg correctly 

---

# Planned (Not Released)

## 🚀 Major Features 

* **AI Chatbot / Customer Support Agent Mode**: Turning the system into a conversational WhatsApp agent.
* **Richer WhatsApp Interactions**: Support for sending locations, emojis, and deeper interactions.
* **Global Number Support**: Adding routing and native handling for foreign (non-Egyptian) phone numbers.

---

## 🐛 Bugs & Fixes

* Improve WhatsApp restart recovery (current solution unstable)
* Ensure reliable progress saving on force exit (cancel/x exit)

---

## ✨ Minor Features

* Limit icon search area to the designated screen region (prevents taskbar/bookmark false positives)
* Add UI alert badges (red dots) on health/monitoring and recovery tabs when issues arise
* Handle already existing WhatsApp numbers efficiently
* Improve the continue progress sheet
* Persist last used WhatsApp account across sessions and automatically switch if halted

---
