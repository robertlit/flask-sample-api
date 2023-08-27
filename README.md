# Sample Flask API
An HTTP API implemented using Flask

# Running
```commandline
pip install -r requirements.txt
python run.py
```
Note: It is good practice to use a virtual environment

# Testing
The included test suite has various test cases for invalid requests, non-existing messages and also good requests.
Run it with:
```commandline
pytest
```
Note: when using SQLite, the database is expected to be empty (or non-existent) before running the tests

# Data Storage
Both in-memory storage and disk storage (SQLite) are implemented
and can be used [interchangeably](app/api.py#L12).

# Extra Features
- Input validation
  - Schema validation, including types, in /AddMessage
  - Query parameter validation in /GetMessage and /DeleteMessage
- API consistency
  - All responses, including errors, are in JSON format -- no plain HTML
  - Consistent schema in responses for easier parsing, for example /GetMessage returns a list even if it only has one message
- Meaningful error messages
- /DeleteMessage returns the amount of messages deleted, for confirmation and easier testing

# Endpoints
## POST /AddMessage
Saves a message.

Request body should be JSON with the following required fields of the correct type:

application_id: integer, session_id: string, message_id: string (unique), participants: list of string, content: string
<details>
<summary>Example request</summary>

```
POST /AddMessage
```
```json
{
  "application_id": 1,
  "session_id": "s1",
  "message_id": "m1",
  "participants": ["john", "jack"],
  "content": "Hello, world!"
}
```
</details>

<details>
<summary>Example response</summary>

```json
{
  "result": "Message added successfully"
}
```
</details>

## GET /GetMessage
Returns messages according to the URL parameter.

Exactly one of the following URL parameters must be specified:
applicationId, sessionId, messageId.

Note: for consistency, a list of messages is returned even if it contains only one message

<details>
<summary>Example request</summary>

```
GET /GetMessage?applicationId=1
```
</details>

<details>
<summary>Example response</summary>

```json
{
  "messages": [
    {
      "application_id": 1,
      "content": "hello",
      "message_id": "m1",
      "participants": [
        "john",
        "jack"
      ],
      "session_id": "s1"
    },
    {
      "application_id": 1,
      "content": "hello",
      "message_id": "m2",
      "participants": [
        "john",
        "jack"
      ],
      "session_id": "s1"
    }
  ]
}
```
</details>

## DELETE /DeleteMessage
Deletes messages according to the URL parameter.

Exactly one of the following URL parameters must be specified:
applicationId, sessionId, messageId.

Returns the amount of deleted messages.

<details>
<summary>Example request</summary>

```
DELETE /DeleteMessage?applicationId=1
```
</details>

<details>
<summary>Example response</summary>

```json
{
  "deleted_amount": 2
}
```
</details>