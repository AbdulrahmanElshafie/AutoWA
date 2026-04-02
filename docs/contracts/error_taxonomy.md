# Error and Status Taxonomy

This document defines standardized status and error meanings across the system.

---

# Job Status

| status  | meaning                    |
| ------- | -------------------------- |
| pending | job not executed           |
| success | job completed successfully |
| fail    | job execution failed       |

---

# Validation Errors

| error                | description                  |
| -------------------- | ---------------------------- |
| invalid_message_mode | unknown message mode         |
| missing_message_text | fixed message without text   |
| missing_message_key  | template message without key |
| missing_doc_path     | variable doc without path    |

---

# Runtime Errors

| error                 | description           |
| --------------------- | --------------------- |
| template_not_found    | message key missing   |
| template_disabled     | template disabled     |
| document_not_found    | document path invalid |
| whatsapp_not_detected | WhatsApp UI not found |
| send_failure          | message send failed   |

---

# Error Handling

Validation errors:

```
job.status = fail
job.status_message = validation_error
```

Automation errors:

```
job.status = fail
job.status_message = runtime_error
```

---

# Retry Policy

Retryable errors:

```
send_failure
whatsapp_not_detected
```

Non-retryable errors:

```
template_not_found
missing_doc_path
invalid_message_mode
```
