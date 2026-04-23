#!/bin/bash
# ============================================
# DeepTutor — School Backup Script
# ============================================
# One-command full backup for school deployments. Captures the PostgreSQL
# database, knowledge bases, and user workspace files into a single
# timestamped directory that IT staff can copy to offsite media.
#
# Usage:
#   ./scripts/school-backup.sh                       # default output dir
#   ./scripts/school-backup.sh /mnt/usb/backups      # custom output dir
#
# Safe to run while the stack is up: pg_dump takes a consistent snapshot,
# and tar uses --ignore-failed-read for files that might be mid-write.
# ============================================

set -euo pipefail

# ---- configuration ----
DEFAULT_BACKUP_ROOT="./backups/manual"
BACKUP_ROOT="${1:-$DEFAULT_BACKUP_ROOT}"
POSTGRES_CONTAINER="${POSTGRES_CONTAINER:-deeptutor-postgres}"
POSTGRES_USER="${POSTGRES_USER:-deeptutor}"
POSTGRES_DB="${POSTGRES_DB:-deeptutor}"
DATA_DIR="${DATA_DIR:-./data}"

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_DIR="${BACKUP_ROOT}/${TIMESTAMP}"

# ---- preflight ----
if ! command -v docker >/dev/null 2>&1; then
    echo "ERROR: docker is not installed or not on PATH." >&2
    exit 1
fi

if ! docker ps --format '{{.Names}}' | grep -q "^${POSTGRES_CONTAINER}$"; then
    echo "ERROR: postgres container '${POSTGRES_CONTAINER}' is not running." >&2
    echo "       Start the stack with:" >&2
    echo "         docker compose -f docker-compose.school.yml up -d" >&2
    exit 1
fi

mkdir -p "${BACKUP_DIR}"

echo "=========================================="
echo "DeepTutor school backup"
echo "=========================================="
echo "Output directory: ${BACKUP_DIR}"
echo ""

# ---- 1. postgres dump ----
echo "[1/4] Dumping PostgreSQL database..."
docker exec "${POSTGRES_CONTAINER}" \
    pg_dump -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" --no-owner --no-privileges \
    | gzip -9 > "${BACKUP_DIR}/db.sql.gz"
DB_SIZE="$(du -h "${BACKUP_DIR}/db.sql.gz" | cut -f1)"
echo "      -> db.sql.gz (${DB_SIZE})"
echo ""

# ---- 2. knowledge bases ----
echo "[2/4] Archiving knowledge bases..."
if [ -d "${DATA_DIR}/knowledge_bases" ]; then
    tar czf "${BACKUP_DIR}/knowledge_bases.tar.gz" \
        -C "${DATA_DIR}" knowledge_bases \
        --ignore-failed-read 2>/dev/null || true
    KB_SIZE="$(du -h "${BACKUP_DIR}/knowledge_bases.tar.gz" | cut -f1)"
    echo "      -> knowledge_bases.tar.gz (${KB_SIZE})"
else
    echo "      -> skipped (no ${DATA_DIR}/knowledge_bases directory)"
fi
echo ""

# ---- 3. user workspace ----
echo "[3/4] Archiving user workspace..."
if [ -d "${DATA_DIR}/user" ]; then
    tar czf "${BACKUP_DIR}/user_data.tar.gz" \
        -C "${DATA_DIR}" user \
        --ignore-failed-read 2>/dev/null || true
    USER_SIZE="$(du -h "${BACKUP_DIR}/user_data.tar.gz" | cut -f1)"
    echo "      -> user_data.tar.gz (${USER_SIZE})"
else
    echo "      -> skipped (no ${DATA_DIR}/user directory)"
fi
echo ""

# ---- 4. manifest ----
echo "[4/4] Writing backup manifest..."
cat > "${BACKUP_DIR}/manifest.txt" <<EOF
DeepTutor School Backup
=======================
Created at:       $(date -u '+%Y-%m-%d %H:%M:%S UTC')
Hostname:         $(hostname)
Postgres DB:      ${POSTGRES_DB}
Postgres user:    ${POSTGRES_USER}
Data directory:   ${DATA_DIR}

Contents:
  db.sql.gz                — pg_dump of ${POSTGRES_DB}
  knowledge_bases.tar.gz   — ${DATA_DIR}/knowledge_bases
  user_data.tar.gz         — ${DATA_DIR}/user

To restore:
  ./scripts/school-restore.sh ${BACKUP_DIR}
EOF
echo "      -> manifest.txt"
echo ""

echo "=========================================="
echo "Backup complete: ${BACKUP_DIR}"
echo "Total size: $(du -sh "${BACKUP_DIR}" | cut -f1)"
echo "=========================================="
