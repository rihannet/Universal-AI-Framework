CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    username TEXT NOT NULL,
    access_level TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
