-- Schema for a project management application
-- Supports users, projects, and task tracking with priorities.

CREATE TABLE users (
    id          SERIAL PRIMARY KEY,
    username    VARCHAR(64) NOT NULL UNIQUE,
    email       VARCHAR(255) NOT NULL UNIQUE,
    full_name   VARCHAR(128),
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active   BOOLEAN DEFAULT TRUE
);

CREATE TABLE projects (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(128) NOT NULL,
    description TEXT,
    owner_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status      VARCHAR(20) DEFAULT 'active'
                CHECK (status IN ('active', 'archived', 'completed')),
    budget      DECIMAL(12, 2),
    started_on  DATE,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tasks (
    id          SERIAL PRIMARY KEY,
    project_id  INTEGER NOT NULL REFERENCES projects(id),
    title       VARCHAR(256) NOT NULL,
    priority    SMALLINT DEFAULT 3 CHECK (priority BETWEEN 1 AND 5),
    assigned_to INTEGER REFERENCES users(id),
    due_date    DATE,
    completed   BOOLEAN DEFAULT FALSE,
    hours_spent NUMERIC(6, 2) DEFAULT 0.00
);

CREATE INDEX idx_tasks_project ON tasks(project_id);
CREATE INDEX idx_tasks_assigned ON tasks(assigned_to) WHERE completed = FALSE;

-- Insert seed data
INSERT INTO users (username, email, full_name) VALUES
    ('alice',   'alice@example.com',   'Alice Chen'),
    ('bob',     'bob@example.com',     'Bob Martinez'),
    ('charlie', 'charlie@example.com', 'Charlie Park');

-- Summary: overdue tasks grouped by project
SELECT
    p.name                          AS project_name,
    COUNT(t.id)                     AS overdue_count,
    COALESCE(SUM(t.hours_spent), 0) AS total_hours,
    MIN(t.due_date)                 AS earliest_due
FROM projects p
INNER JOIN tasks t ON t.project_id = p.id
LEFT JOIN users u ON u.id = t.assigned_to
WHERE t.completed = FALSE
  AND t.due_date < CURRENT_DATE
  AND p.status != 'archived'
GROUP BY p.name
HAVING COUNT(t.id) > 0
ORDER BY overdue_count DESC, earliest_due ASC
LIMIT 20;
