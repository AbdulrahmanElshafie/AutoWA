# Jobs CSV Schema

File location:

```
data/jobs.csv
```

This file defines the input dataset used to execute WhatsApp automation jobs.

---

# Columns

| column         | required    | description                       |
| -------------- | ----------- | --------------------------------- |
| number         | yes         | WhatsApp phone number             |
| contact_name   | optional    | Contact name                      |
| message_mode   | yes         | `fixed`, `template`, `doc_only`   |
| message_text   | conditional | Used when `message_mode=fixed`    |
| message_key    | conditional | Used when `message_mode=template` |
| doc_mode       | yes         | `none`, `fixed`, `variable`       |
| doc_path       | conditional | Used when `doc_mode=variable`     |
| status         | optional    | `pending`, `success`, `fail`      |
| status_message | optional    | execution result                  |

---

# Message Mode Rules

| mode     | behavior                           |
| -------- | ---------------------------------- |
| fixed    | send `message_text`                |
| template | pick message variant from template |
| doc_only | skip message sending               |

---

# Document Mode Rules

| mode     | behavior                             |
| -------- | ------------------------------------ |
| none     | no document                          |
| fixed    | use fixed document defined in config |
| variable | use document path from row           |

---

# Validation Rules

Invalid row conditions:

```
message_mode = fixed AND message_text empty
message_mode = template AND message_key empty
doc_mode = variable AND doc_path empty
message_mode = doc_only AND doc_mode = none
```

---

# Example

```
number,contact_name,message_mode,message_text,message_key,doc_mode,doc_path,status,status_message
201234567890,Ahmed,fixed,Hello officer,,none,,pending,
201234567891,Mohamed,template,,permit_msg,fixed,,pending,
201234567892,Ali,doc_only,,,variable,docs/permit_1.pdf,pending,
```
