-- Database Initialization Schema

CREATE TABLE IF NOT EXISTS courses (
    course_id VARCHAR(50) PRIMARY KEY,
    course_name VARCHAR(150) NOT NULL,
    total_seats INT NOT NULL,
    unassigned_seats INT NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS enrollment_logs (
    log_id SERIAL PRIMARY KEY,
    course_id VARCHAR(50) REFERENCES courses(course_id),
    previous_seats INT NOT NULL,
    new_seats INT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexing for rapid queries during high-volume daily updates
CREATE INDEX IF NOT EXISTS idx_course_seats ON courses(course_id, unassigned_seats);
CREATE INDEX IF NOT EXISTS idx_log_timestamp ON enrollment_logs(timestamp DESC);
