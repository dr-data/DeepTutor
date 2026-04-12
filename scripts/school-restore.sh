#!/bin/bash
# ============================================
# DeepTutor — School Restore Script
# ============================================
# Restore a backup created by ./scripts/school-backup.sh. This is a
# destructive operation — it drops and recreates the PostgreSQL database
# and overwrites the on-disk knowledge base and user data directories.
#
# Usage:
#   ./scripts/school-restore.sh ./backups/manual/20260411_020000
#
# The script prompts for confirmation before touching anything. Pass
# --yes to skip the confirmation (use only in automated scripts, not
# interactively).
# ============================================

set -euo pipefail

# ---- configuration ----
POSTGRES_CONTAINER="${POSTGRES_CONTAINER:-deeptutor-postgres}"
POSTGRES_USER="${POSTGRES_USER:-deeptutor}"
POSTGRES_DB="${POSTGRES_DB:-deeptutor}"
APP_CONTAINER="${APP_CONTAINER:-deeptutor-app}"
DATA_DIR="${DATA_DIR:-./data}"

# ---- argument parsing ----
SKIP_CONFIRM=0
BACKUP_DIR=""
for arg in "$@"; do
    case "${arg}" in
        --yes|-y)
            SKIP_CONFIRM=1
            ;;
        -h|--help)
            sed -n '2,15p' "$0"
            exit 0
            ;;
        -*)
            echo "ERROR: unknown option: ${arg}" >&2
            exit 1
            ;;
        *)
            BACKUP_DIR="${arg}"
            ;;
    esac
done

if [ -z "${BACKUP_DIR}" ]; then
    echo "ERROR: no backup directory specified." >&2
    echo "Usage: $0 <backup-dir> [--yes]" >&2
    exit 1
fi

if [ ! -d "${BACKUP_DIR}" ]; then
    echo "ERROR: backup directory not found: ${BACKUP_DIR}" >&2
    exit 1
fi

# ---- preflight ----
if ! command -v docker >/dev/null 2>&1; then
    echo "ERROR: docker is not installed or not on PATH." >&2
    exit 1
fi

if ! docker ps --format '{{.Names}}' | grep -q "^${POSTGRES_CONTAINER}$"; then
    echo "ERROR: postgres container '${POSTGRES_CONTAINER}' is not running." >&2
    exit 1
fi

DB_DUMP="${BACKUP_DIR}/db.sql.gz"
KB_ARCHIVE="${BACKUP_DIR}/knowledge_bases.tar.gz"
USER_ARCHIVE="${BACKUP_DIR}/user_data.tar.gz"

if [ ! -f "${DB_DUMP}" ]; then
    echo "ERROR: missing database dump at ${DB_DUMP}" >&2
    exit 1
fi

# ---- confirm ----
echo "=========================================="
echo "DeepTutor school RESTORE"
echo "=========================================="
echo ""
echo "This will OVERWRITE the current data:"
echo "  - PostgreSQL database '${POSTGRES_DB}' on ${POSTGRES_CONTAINER}"
echo "  - ${DATA_DIR}/knowledge_bases"
echo "  - ${DATA_DIR}/user"
echo ""
echo "Backup source: ${BACKUP_DIR}"
if [ -f "${BACKUP_DIR}/manifest.txt" ]; then
    echo "---- manifest ----"
    cat "${BACKUP_DIR}/manifest.txt"
    echo "------------------"
fi
echo ""

if [ "${SKIP_CONFIRM}" -ne 1 ]; then
    read -r -p "Continue? Type 'yes' to proceed: " confirm
    if [ "${confirm}" != "yes" ]; then
        echo "Aborted."
        exit 0
    fi
fi

# ---- 1. stop app container ----
if docker ps --format '{{.Names}}' | grep -q "^${APP_CONTAINER}$"; then
    echo "[1/4] Stopping application container to release file locks..."
    docker stop "${APP_CONTAINER}" >/dev/null
    RESTART_APP=1
else
    echo "[1/4] Application container not running — skipping stop."
    RESTART_APP=0
fi
echo ""

# ---- 2. restore database ----
echo "[2/4] Restoring PostgreSQL database..."
# Drop and recreate the schema so leftovers don't survive the restore.
docker exec "${POSTGRES_CONTAINER}" \
    psql -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" \
    -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;" >/dev/null
gunzip -c "${DB_DUMP}" | docker exec -i "${POSTGRES_CONTAINER}" \
    psql -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" >/dev/null
echo "      -> database restored"
echo ""

# ---- 3. restore files ----
echo "[3/4] Restoring file archives..."
if [ -f "${KB_ARCHIVE}" ]; then
    rm -rf "${DATA_DIR}/knowledge_bases"
    mkdir -p "${DATA_DIR}"
    tar xzf "${KB_ARCHIVE}" -C "${DATA_DIR}"
    echo "      -> knowledge bases restored"
fi
if [ -f "${USER_ARCHIVE}" ]; then
    rm -rf "${DATA_DIR}/user"
    mkdir -p "${DATA_DIR}"
    tar xzf "${USER_ARCHIVE}" -C "${DATA_DIR}"
    echo "      -> user data restored"
fi
echo ""

# ---- 4. restart app ----
if [ "${RESTART_APP}" -eq 1 ]; then
    echo "[4/4] Restarting application container..."
    docker start "${APP_CONTAINER}" >/dev/null
    echo "      -> ${APP_CONTAINER} restarted"
else
    echo "[4/4] Application container was not running — skipping restart."
fi
echo ""

echo "=========================================="
echo "Restore complete."
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Verify the app is healthy:"
echo "       docker compose -f docker-compose.school.yml ps"
echo "  2. Check the schema version:"
echo "       docker exec ${APP_CONTAINER} alembic current"
