CREATE TABLE IF NOT EXISTS state_tasks (
    task_id TEXT PRIMARY KEY,
    workflow_id TEXT NOT NULL,
    step_id TEXT,
    assigned_worker TEXT,
    status TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (workflow_id) REFERENCES workflows(workflow_id)
);

CREATE INDEX IF NOT EXISTS idx_state_tasks_workflow_id ON state_tasks(workflow_id);
CREATE INDEX IF NOT EXISTS idx_state_tasks_status ON state_tasks(status);
