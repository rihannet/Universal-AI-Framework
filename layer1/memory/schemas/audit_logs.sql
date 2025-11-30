CREATE TABLE IF NOT EXISTS audit_logs (
    log_id SERIAL PRIMARY KEY,
    workflow_id TEXT,
    step_id TEXT,
    user_id TEXT,
    action TEXT,
    timestamp TIMESTAMP DEFAULT NOW()
);
