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
| message        | optional    | The text message to send          |
| doc_path       | optional    | The absolute path to the document |
| status         | optional    | `pending`, `success`, `fail`      |
| status_message | optional    | execution result                  |

---

# Example

```csv
number,contact_name,message,doc_path,status,status_message
201234567890,Ahmed,Hello officer,,pending,
201234567891,Mohamed,Permit attached,C:/docs/permit_1.pdf,pending,
201234567892,Ali,,C:/docs/permit_2.pdf,pending,
```
