-- Base table from Practice 7. Keeping the old table name makes old code work.
CREATE TABLE IF NOT EXISTS phonebook (
    id         SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    phone      VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create groups table for contact categorization
CREATE TABLE IF NOT EXISTS groups (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

-- Insert default groups, skip if they already exist
INSERT INTO groups (name) VALUES
    ('Family'),
    ('Work'),
    ('Friend'),
    ('Other')
ON CONFLICT DO NOTHING;

-- Add new columns to phonebook (safe to run multiple times)
ALTER TABLE phonebook
    ADD COLUMN IF NOT EXISTS email      VARCHAR(100),
    ADD COLUMN IF NOT EXISTS birthday   DATE,
    ADD COLUMN IF NOT EXISTS group_id   INTEGER REFERENCES groups(id),
    ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW();

-- Create phones table for storing multiple numbers per contact
CREATE TABLE IF NOT EXISTS phones (
    id         SERIAL PRIMARY KEY,
    contact_id INTEGER REFERENCES phonebook(id) ON DELETE CASCADE,
    phone      VARCHAR(20) NOT NULL,
    type       VARCHAR(10) CHECK (type IN ('home', 'work', 'mobile'))
);
