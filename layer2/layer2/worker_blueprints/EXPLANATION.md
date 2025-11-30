# Worker Blueprint Explanation

## What is This?

This folder contains the **base structure** for creating workers.

---

## How to Create a Worker

### Step 1: Copy the Blueprint
Copy `worker_blueprint.py` to your main folder:
```
AWS HACKATHON/worker_blueprint.py
```

### Step 2: Edit the Values
Open the file and edit these 7 things:

#### 1. **worker_id** (Required)
Unique identifier for your worker (no spaces)
```python
worker_id="my_browser"
```
Examples: `"my_browser"`, `"news_bot_1"`, `"terminal_main"`

#### 2. **name** (Required)
Display name (can have spaces)
```python
name="My Web Browser"
```
Examples: `"My Web Browser"`, `"AI News Bot"`, `"File Manager"`

#### 3. **worker_type** (Required)
Create ANY type you want:
```python
worker_type="your_custom_type"
```

**You can create ANY worker type!**

Examples:
- `"browser"` → Opens websites
- `"terminal"` → Shell commands
- `"email"` → Send emails
- `"sms"` → Send text messages
- `"video"` → Video processing
- `"audio"` → Audio processing
- `"image"` → Image editing
- `"pdf"` → PDF operations
- `"excel"` → Excel operations
- `"calendar"` → Calendar management
- `"slack"` → Slack integration
- `"discord"` → Discord bot
- **Anything you need!**

#### 4. **capabilities** (Required)
List what your worker can do
```python
capabilities=["web_scraping", "browser_automation"]
```

**Examples by Type:**
- Browser: `["web_scraping", "browser_automation", "url_fetch"]`
- Terminal: `["shell_execution", "command_line"]`
- File: `["file_read", "file_write", "file_list"]`
- App: `["app_launch", "process_management"]`
- API: `["api_calls", "data_fetch"]`
- DBMS: `["database_query", "sql_execution"]`

#### 5. **api_keys** (Optional)
API keys or credentials (if needed)
```python
api_keys={}  # No API key needed
```

**With API Key:**
```python
api_keys={"api_key": "your_api_key_here"}
```

**With Database Connection:**
```python
api_keys={"connection_string": "postgresql://user:pass@localhost:5432/db"}
```

#### 6. **endpoints** (Optional)
API endpoints (if needed)
```python
endpoints={}  # No endpoint needed
```

**With Endpoint:**
```python
endpoints={"default": "https://api.example.com"}
```

#### 7. **model_config** (Optional)
LLM settings (can leave as default)
```python
model_config={
    "temperature": 0.3,    # 0.0 = precise, 1.0 = creative
    "max_tokens": 1024     # response length
}
```

---

## Complete Examples

### Example 1: Browser Worker (No API Key)
```python
layer2.create_worker(
    worker_id="my_browser",
    name="My Web Browser",
    worker_type="browser",
    capabilities=["web_scraping", "browser_automation"],
    api_keys={},
    endpoints={},
    model_config={"temperature": 0.3, "max_tokens": 1024}
)
```

### Example 2: News Worker (With API Key)
```python
layer2.create_worker(
    worker_id="my_news",
    name="My News Bot",
    worker_type="api",
    capabilities=["news_fetch", "articles"],
    api_keys={"api_key": "your_news_api_key"},
    endpoints={"default": "https://newsapi.org/v2/top-headlines"},
    model_config={"temperature": 0.5, "max_tokens": 2048}
)
```

### Example 3: Terminal Worker (No API Key)
```python
layer2.create_worker(
    worker_id="my_terminal",
    name="My Terminal",
    worker_type="terminal",
    capabilities=["shell_execution", "command_line"],
    api_keys={},
    endpoints={},
    model_config={"temperature": 0.2, "max_tokens": 512}
)
```

### Example 4: Database Worker (With Connection)
```python
layer2.create_worker(
    worker_id="my_database",
    name="My Database",
    worker_type="dbms",
    capabilities=["database_query", "sql_execution"],
    api_keys={"connection_string": "postgresql://user:pass@localhost:5432/db"},
    endpoints={},
    model_config={"temperature": 0.1, "max_tokens": 1024}
)
```

### Example 5: Email Worker (Custom Type)
```python
layer2.create_worker(
    worker_id="my_email",
    name="My Email Sender",
    worker_type="email",  # Custom type!
    capabilities=["send_email", "read_email"],
    api_keys={"api_key": "sendgrid_api_key"},
    endpoints={"default": "https://api.sendgrid.com/v3/mail/send"},
    model_config={"temperature": 0.3, "max_tokens": 1024}
)
```

### Example 6: Video Worker (Custom Type)
```python
layer2.create_worker(
    worker_id="my_video",
    name="My Video Processor",
    worker_type="video",  # Custom type!
    capabilities=["video_edit", "video_convert"],
    api_keys={},
    endpoints={},
    model_config={"temperature": 0.2, "max_tokens": 512}
)
```

---

## What Happens When You Run It?

### 1. Worker Configuration Created
The system creates a configuration with your values.

### 2. Saved to JSON File
File created: `layer2/layer2/workers/{worker_id}.json`

### 3. Automatically Connected
- ✅ Layer-1: Planner, Memory, LLM
- ✅ Layer-3: MCP Tools
- ✅ Layer-4: Safety
- ✅ Layer-5: Audit

### 4. Ready to Use
Run `python main.py` and use your worker!

---

## Field Reference

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| worker_id | Yes | string | Unique ID (no spaces) |
| name | Yes | string | Display name |
| worker_type | Yes | string | Type: browser, terminal, file, app, api, dbms |
| capabilities | Yes | list | What worker can do |
| api_keys | No | dict | API keys/credentials |
| endpoints | No | dict | API endpoints |
| model_config | No | dict | LLM settings |

---

## Quick Reference

### Worker Types:
**You can create ANY type!**

Common examples:
- **browser** → Web operations
- **terminal** → Shell commands
- **file** → File operations
- **app** → Launch apps
- **api** → API calls
- **email** → Email operations
- **sms** → Text messages
- **video** → Video processing
- **audio** → Audio processing
- **image** → Image editing
- **pdf** → PDF operations
- **excel** → Spreadsheet operations
- **calendar** → Calendar management
- **slack** → Slack integration
- **discord** → Discord bot
- **custom** → Your own type!

### When You Need API Keys:
Depends on what your worker does:
- API integrations → API key needed
- Database access → Connection string needed
- Local operations → No API key needed

---

## Summary

1. **Copy** `worker_blueprint.py`
2. **Edit** the 7 values
3. **Run** `python worker_blueprint.py`
4. **Use** `python main.py`

**That's it!**
