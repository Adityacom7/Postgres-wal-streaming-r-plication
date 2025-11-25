#!/bin/bash
set -e

# Copy custom pg_hba.conf to data directory
cp /docker-entrypoint-initdb.d/pg_hba.conf /var/lib/postgresql/data/pg_hba.conf

# Update postgresql.conf for replication
echo "wal_level = replica" >> /var/lib/postgresql/data/postgresql.conf
echo "max_wal_senders = 3" >> /var/lib/postgresql/data/postgresql.conf
echo "max_replication_slots = 3" >> /var/lib/postgresql/data/postgresql.conf
echo "wal_keep_size = 64MB" >> /var/lib/postgresql/data/postgresql.conf
echo "hot_standby = on" >> /var/lib/postgresql/data/postgresql.conf

# Reload configuration
psql -U postgres -c "SELECT pg_reload_conf();"

echo "Master replication setup completed"
