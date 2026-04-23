# DeepTutor — School Deployment Guide

This guide walks a school IT administrator through deploying DeepTutor on a
single school server with **no internet required at runtime**. The stack is
self-contained: application, database, and local LLM all run inside Docker
Compose on the same machine.

Related documents:

- [`secondary-school-features.md`](./secondary-school-features.md) — the
  feature brainstorm this deployment is designed to support.
- [`roadmap.md`](./roadmap.md) — the broader product roadmap.

---

## What You Get

| Component | Image | Purpose |
|-----------|-------|---------|
| `deeptutor-app` | `ghcr.io/hkuds/deeptutor:latest` | FastAPI backend + Next.js frontend |
| `deeptutor-postgres` | `postgres:16-alpine` | Multi-user database (users, classrooms, assignments, audit logs) |
| `deeptutor-ollama` | `ollama/ollama:latest` | Local LLM + embedding runtime (qwen2.5:14b by default) |
| `deeptutor-backup` | `prodrigestivill/postgres-backup-local:16-alpine` | Automated daily `pg_dump` with rolling retention |

All four containers are orchestrated by [`docker-compose.school.yml`](../docker-compose.school.yml).

---

## Hardware Recommendations

| Setup | Hardware | Concurrent students | LLM quality |
|-------|----------|---------------------|-------------|
| Minimal (CPU) | 16GB RAM, any modern CPU | 5-10 | Basic (7B model, slow) |
| **Recommended** | **32GB RAM, 1× RTX 3060/4060 (12GB VRAM)** | **20-30** | **Good (14B model)** |
| Classroom+ | 64GB RAM, 1× RTX 3090/4090 (24GB VRAM) | 40-60 | Excellent (32B model) |
| Cloud hybrid | Minimal local + cloud LLM API | Unlimited | Best (GPT-4o / Claude) |

A mini-PC with a consumer GPU (~$800-1200 total) can comfortably serve a
classroom of 30 students running `qwen2.5:14b` through Ollama.

---

## First-Time Setup

### 1. Clone the repo (or copy from USB)

```bash
git clone https://github.com/HKUDS/DeepTutor.git
cd DeepTutor
```

### 2. Create the environment file

```bash
cp .env.school.example .env.school
```

Edit `.env.school` and set at minimum the two secrets marked `[REQUIRED]`:

```bash
POSTGRES_PASSWORD="$(openssl rand -base64 32)"
DEEPTUTOR_JWT_SECRET="$(openssl rand -base64 48)"
```

### 3. Bring up the stack

```bash
docker compose -f docker-compose.school.yml up -d
```

First startup downloads the images and initialises PostgreSQL. Progress:

```bash
docker compose -f docker-compose.school.yml logs -f
```

### 4. Pull the LLM models (one-time)

Ollama starts with an empty model cache. Pull the models you need:

```bash
docker exec deeptutor-ollama ollama pull qwen2.5:14b
docker exec deeptutor-ollama ollama pull nomic-embed-text
```

The downloads are cached in the `ollama_models` Docker volume, so they
persist across container restarts.

### 5. Apply database migrations

Migrations run automatically on app startup when `AUTO_MIGRATE_ON_START=true`
is set in `.env.school` (the default). To run them manually:

```bash
docker exec deeptutor-app alembic upgrade head
```

To check the current schema version:

```bash
docker exec deeptutor-app alembic current
```

### 6. Verify

Open `http://<server-ip>:3782` in a browser. The login page should appear.

```bash
# Quick health check from the server itself
curl -sf http://localhost:8001/ && echo "API OK"
```

---

## Creating the First Admin User

After the stack is running, bootstrap the initial school and admin account.
The helper is bundled with the DeepTutor CLI:

```bash
docker exec -it deeptutor-app python -m deeptutor_cli.school bootstrap \
    --school-name "Lincoln High School" \
    --school-slug lincoln-high \
    --admin-email admin@lincoln.edu \
    --admin-name "Principal Davis"
```

You will be prompted for an initial password. Change it on first login.

After that, teachers can be invited by the admin from the settings page,
and students join via classroom invite codes issued by their teacher.

---

## Offline Installation (Air-Gapped Schools)

If the school server has no internet at all, bundle everything on a
machine **that does** have internet and transfer via USB:

### On the build machine

```bash
# 1. Pull all images
docker compose -f docker-compose.school.yml pull

# 2. Save images to a portable tarball
docker save \
    ghcr.io/hkuds/deeptutor:latest \
    postgres:16-alpine \
    ollama/ollama:latest \
    prodrigestivill/postgres-backup-local:16-alpine \
    | gzip > deeptutor-school-images.tar.gz

# 3. Pre-download Ollama models into a portable folder
mkdir -p ollama-cache
docker run --rm -v "$PWD/ollama-cache:/root/.ollama" \
    ollama/ollama ollama pull qwen2.5:14b
docker run --rm -v "$PWD/ollama-cache:/root/.ollama" \
    ollama/ollama ollama pull nomic-embed-text

# 4. Copy everything to USB
cp deeptutor-school-images.tar.gz /mnt/usb/
cp -r ollama-cache /mnt/usb/
cp -r DeepTutor /mnt/usb/
```

### On the school server

```bash
# 1. Load the Docker images
gunzip -c /mnt/usb/deeptutor-school-images.tar.gz | docker load

# 2. Restore the Ollama model cache into the volume
docker volume create deeptutor_ollama_models
docker run --rm \
    -v deeptutor_ollama_models:/dest \
    -v /mnt/usb/ollama-cache:/src \
    alpine sh -c "cp -a /src/. /dest/"

# 3. Start the stack normally
cd /path/to/DeepTutor
cp .env.school.example .env.school   # edit secrets
docker compose -f docker-compose.school.yml up -d
```

The stack now runs fully offline.

---

## Backups

### Automated (included)

The `deeptutor-backup` sidecar container runs `pg_dump` on the schedule
defined in `.env.school`:

```bash
BACKUP_SCHEDULE=@daily     # cron syntax or shortcuts: @daily, @hourly, ...
BACKUP_KEEP_DAYS=30        # keep 30 daily snapshots
BACKUP_KEEP_WEEKS=4
BACKUP_KEEP_MONTHS=6
```

Backups land in `./backups/postgres/` on the host filesystem:

```
backups/postgres/
├── daily/
│   ├── deeptutor-20260411.sql.gz
│   ├── deeptutor-20260410.sql.gz
│   └── ...
├── weekly/
└── monthly/
```

Copy the `backups/` directory to offsite storage (NAS, cloud bucket, USB)
as part of your normal school backup routine.

### Manual (full snapshot)

To capture everything — database, knowledge bases, and user workspace —
in a single timestamped bundle:

```bash
./scripts/school-backup.sh
# → ./backups/manual/20260411_143022/
#     ├── db.sql.gz
#     ├── knowledge_bases.tar.gz
#     ├── user_data.tar.gz
#     └── manifest.txt
```

Or target a different directory (e.g. external drive):

```bash
./scripts/school-backup.sh /mnt/usb/deeptutor-backups
```

### Restore

```bash
./scripts/school-restore.sh ./backups/manual/20260411_143022
```

The script:

1. Stops the app container (`deeptutor-app`)
2. Drops and recreates the PostgreSQL schema
3. Loads the dump and file archives
4. Restarts the app container

It prompts for confirmation before doing anything destructive. Pass
`--yes` to skip the prompt in automation.

---

## Updating to a New Version

The update workflow preserves all data:

```bash
# 1. Take a manual safety snapshot
./scripts/school-backup.sh

# 2. Pull the new image (or docker load from USB for offline)
docker compose -f docker-compose.school.yml pull

# 3. Restart — migrations run automatically on startup
docker compose -f docker-compose.school.yml up -d

# 4. Verify
docker exec deeptutor-app alembic current
docker compose -f docker-compose.school.yml ps
```

If a migration fails, the app container exits with an error. Your data is
untouched — fix the underlying issue, downgrade via
`docker compose pull` with the previous image tag, and try again.

### Rolling back a migration

```bash
# Roll back the most recent migration
docker exec deeptutor-app alembic downgrade -1

# Roll back to a specific revision
docker exec deeptutor-app alembic downgrade 0002

# Inspect migration history
docker exec deeptutor-app alembic history
```

---

## Monitoring & Troubleshooting

### Health checks

```bash
docker compose -f docker-compose.school.yml ps
# All services should report "healthy" or "running".
```

### Live logs

```bash
docker compose -f docker-compose.school.yml logs -f deeptutor
docker compose -f docker-compose.school.yml logs -f ollama
```

### Database shell

```bash
docker exec -it deeptutor-postgres psql -U deeptutor -d deeptutor
```

Useful queries once inside:

```sql
SELECT version_num FROM alembic_version;      -- current schema revision
SELECT COUNT(*) FROM users;                   -- how many users
SELECT role, COUNT(*) FROM users GROUP BY role;
SELECT COUNT(*) FROM assignments WHERE due_at > EXTRACT(epoch FROM now());
```

### Common issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| `deeptutor-app` restarts in a loop | Migration failed | `docker logs deeptutor-app` — fix error or roll back |
| Students see "login failed" with correct password | `DEEPTUTOR_JWT_SECRET` changed | Restore the original secret in `.env.school` |
| Ollama returns empty responses | Model not pulled | `docker exec deeptutor-ollama ollama list` → `ollama pull <model>` |
| Backups not appearing | `backup` container failing | `docker logs deeptutor-backup` |
| Slow LLM responses | CPU-only, large model | Switch to `qwen2.5:7b` or add a GPU |

---

## Security Checklist

Before enrolling real students:

- [ ] `POSTGRES_PASSWORD` and `DEEPTUTOR_JWT_SECRET` are strong and unique
- [ ] `.env.school` is readable only by the docker daemon user (`chmod 600`)
- [ ] The server is behind a firewall; ports 8001/3782 are not exposed to
      the public internet unless you have put a reverse proxy with TLS in
      front of them
- [ ] Daily backups are being copied to offsite storage
- [ ] A second admin account exists (so you can recover if the primary is
      locked out)
- [ ] You have tested the restore workflow end-to-end on a staging copy

---

## Going Further

- **Multiple schools on one server**: supported via shared PostgreSQL with
  `school_id` isolation. See the district-scale section of
  [`secondary-school-features.md`](./secondary-school-features.md).
- **Cloud LLMs instead of Ollama**: set `LLM_BINDING=openai` (or another
  provider) in `.env.school` and remove the `ollama` service from
  `docker-compose.school.yml`.
- **External Postgres**: point `DEEPTUTOR_DATABASE_URL` at your own
  PostgreSQL instance and remove the `postgres` service from the compose
  file. Migrations still apply on startup.
