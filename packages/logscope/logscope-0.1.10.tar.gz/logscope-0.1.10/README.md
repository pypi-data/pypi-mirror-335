# Logscope

Logscope is a Python logging library that brings together SQLite storage and pretty console output. Write logs to both your terminal and a queryable database with a dead-simple API.

## Features

- Write logs to SQLite + console simultaneously
- Smart context tracking (captures function names and calling code)
- Colorized, pretty console output
- Thread-safe SQLite operations
- Dead simple API
- **Trace Execution**: Automatically log function calls, returns, and exceptions
- **Flexible Querying**: Retrieve logs with custom SQL queries

## Installation

```bash
pip install logscope
```

## Quick Start

```python
from logscope import logger

# Get a logger with default settings (SQLite + console output)
log = logger()

# Log some things!
log("Starting analysis")
log("Processing item", {"id": 123, "status": "pending"})
```

## Configuration

```python
import logging
from logscope import logger

# All settings are optional
log = logger(
    db_path='app.db',      # Where to store the SQLite database
    style='plain',         # 'plain' or 'colorful' console output
    name='MyApp',          # Logger name (defaults to timestamp)
    level=logging.INFO     # Logging level (default: DEBUG)
)
```

## Tracing Functions

Logscope includes a `@trace` decorator to automatically log function calls, returns, and exceptions:

```python
from logscope.tracing import trace

@trace
def my_function(a, b):
    return a + b

my_function(2, 3)  # Automatically logs the call, return value, and source code
```

## How It Works

Each log message is:
1. Written to a SQLite database for later querying
2. Displayed in your console with context details
3. Tracked with its calling context (which function called it and how)

Example console output:
```
2024-03-15 14:23:45.123456> Starting analysis
  · process_data:data = process_data("large_file.txt")
  · /path/to/script.py:45
```

## Querying Logs

Use the `query` function to fetch logs directly from Python:

```python
from logscope import query

logs = query("SELECT * FROM logs WHERE event_type = 'error'", db_path='app.db')
for log in logs:
    print(log)
```

## Database Schema

Logs are stored in SQLite with this schema:

```sql
CREATE TABLE logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run TEXT,              -- Unique ID for each logger instance
    timestamp TEXT,        -- ISO format with microseconds
    message TEXT,          -- The logged message
    filename TEXT,         -- Source file path
    lineno INTEGER,        -- Line number
    source TEXT,          -- The actual calling code
    function TEXT,         -- Calling function name
    event_type TEXT        -- Custom event type (e.g., 'error', 'info')
);
```

## Example Queries

Get the last 10 logs from a specific run:
```sql
SELECT timestamp, message, function
FROM logs
WHERE run = '2024-03-15 14:23:45.123456'
ORDER BY timestamp DESC
LIMIT 10;
```

Find all errors from a specific function:
```sql
SELECT timestamp, message
FROM logs
WHERE function = 'process_data'
  AND message LIKE '%error%'
ORDER BY timestamp;
```

Retrieve all logs with a custom event type:
```sql
SELECT *
FROM logs
WHERE event_type = 'trace';
```

## License

MIT License - See LICENSE file for details
