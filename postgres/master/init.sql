-- Create replication user
CREATE ROLE replicator WITH REPLICATION PASSWORD 'replicapass' LOGIN;

-- Create application table
CREATE TABLE IF NOT EXISTS scan_results (
    id SERIAL PRIMARY KEY,
    client_id VARCHAR(255) NOT NULL,
    scan_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for faster queries
CREATE INDEX idx_client_id ON scan_results(client_id);
CREATE INDEX idx_created_at ON scan_results(created_at DESC);

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON scan_results TO postgres;
GRANT USAGE, SELECT ON SEQUENCE scan_results_id_seq TO postgres;
