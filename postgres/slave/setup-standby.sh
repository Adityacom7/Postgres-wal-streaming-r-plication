#!/bin/bash
set -euo pipefail

# Safer standby setup for OpenShift / arbitrary UID environments.
# Strategy:
# - Avoid wiping the entire PVC.
# - Use a per-UID subdirectory under /var/lib/postgresql/data so the running
#   process can create and own its data directory even when OpenShift assigns
#   an arbitrary non-root UID.

CURRENT_UID=$(id -u 2>/dev/null || echo 0)
BASE_DATA_DIR=/var/lib/postgresql/data

if [ "$CURRENT_UID" -ne 0 ]; then
  # Use a UID-specific data directory on the shared volume
  DATA_DIR="$BASE_DATA_DIR/$CURRENT_UID"
else
  DATA_DIR="$BASE_DATA_DIR"
fi

mkdir -p "$DATA_DIR"
# Ensure the directory is writable by the current user; chown may fail on some PV drivers,
# so fall back to permissive permissions if chown is not allowed.
chown "$CURRENT_UID":"$CURRENT_UID" "$DATA_DIR" 2>/dev/null || true
chmod 0700 "$DATA_DIR" 2>/dev/null || true

echo "Using PGDATA=$DATA_DIR"

until pg_isready -h "${MASTER_HOST}" -p "${MASTER_PORT}" -U "${REPLICATION_USER}"; do
  echo "Waiting for master database to be ready..."
  sleep 2
done

export PGPASSWORD="${REPLICATION_PASSWORD}"

# Run pg_basebackup into the chosen DATA_DIR. Use -R to write recovery.conf/standby.signal.
PGPASSWORD="$REPLICATION_PASSWORD" pg_basebackup -h "$MASTER_HOST" -D "$DATA_DIR" -U "$REPLICATION_USER" -v -P -W -R

# Ensure standby signal exists (for modern Postgres, -R creates standby.signal/primary_conninfo)
touch "$DATA_DIR/standby.signal" 2>/dev/null || true

# Set PGDATA so the default entrypoint starts Postgres with the same path
export PGDATA="$DATA_DIR"

# Exec the regular Postgres entrypoint
exec docker-entrypoint.sh postgres

