# AutoWA — Professional WhatsApp Outreach & Workflow Automation

AutoWA is a desktop automation platform built to streamline large-scale WhatsApp communication workflows with human-like behavior simulation, dynamic personalization, and document-based messaging.

Designed for agencies, recruiters, sales teams, and operations-heavy workflows, it transforms repetitive WhatsApp outreach into a controlled and scalable system.

![Demo Screenshot](./AutoWA.PNG)

---

## The Problem

Manual WhatsApp outreach becomes unsustainable when working with:

- hundreds of leads
- repeated follow-ups
- personalized messaging
- document attachments
- multiple account sessions

Common challenges include:

- time-consuming repetitive tasks
- inconsistent personalization
- operational mistakes
- account safety risks from bot-like behavior
- lack of workflow visibility

Traditional bulk messaging tools often feel robotic and increase the risk of account restrictions.

---

## The Solution

AutoWA simulates realistic user behavior while providing structured workflow controls.

Key capabilities include:

- human-like randomized typing delays
- dynamic message templates
- batch interval control
- account rotation
- document attachments per contact
- live execution tracking
- recovery & resume workflows

This allows teams to scale WhatsApp communication while maintaining more natural interaction patterns.

---

## Use Cases

### Lead Generation & Sales Outreach
Send personalized first-touch and follow-up messages to lead lists.

### Recruitment & HR
Automate candidate communication and document delivery.

### Customer Support Operations
Handle repetitive support-side messaging workflows.

### Agency / Marketing Outreach
Scale campaign communication across multiple accounts.

### Internal Operations
Send structured reminders, approvals, and updates.

---

## Core Features

- Human-like workflow simulation
- Dynamic placeholder templating
- Randomized message variants
- Attachment automation
- Account rotation
- Batch execution controls
- Real-time execution monitoring

---

## System Architecture

AutoWA follows a layered architecture to keep the system maintainable and scalable.

```text
GUI Layer
    ↓
Core Workflow Engine
    ↓
Automation Controller
    ↓
WhatsApp Web Interface
```

### Layer Breakdown

### GUI Layer
Handles execution control, settings, monitoring, and user feedback.

### Core Engine
Validates input data, orchestrates workflow logic, controls batching and retries.

### Automation Layer
Performs browser and desktop interaction using image recognition and event simulation.

### Data & Config Layer
Stores templates, schemas, job inputs, logs, and assets.

---

## Technical Stack

- Python
- FreeSimpleGUI
- PyAutoGUI
- OpenCV
- Pandas

---

## Known Constraints

- Windows desktop only
- foreground execution required
- image-recognition dependent
- currently optimized for Egyptian workflows
- dark mode support prioritized

---

## Roadmap

- analytics dashboard
- support-agent mode
- global number formatting
- multilingual UI
- richer interaction types