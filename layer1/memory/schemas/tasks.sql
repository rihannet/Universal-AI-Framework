CREATE TABLE IF NOT EXISTS tasks (
    task_id TEXT PRIMARY KEY,
    workflow_id TEXT,
    step_id TEXT,
    status TEXT,
    assigned_worker TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
