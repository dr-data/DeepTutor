# DeepTutor for Secondary School: Feature Brainstorm

## Context

DeepTutor is currently an **agent-native personalized tutoring platform** designed for individual learners (self-learners, researchers, university students). It runs in **single-user mode** with no authentication, no role system, and no classroom management. The core AI capabilities (Chat, Deep Solve, Quiz Generation, Deep Research, Guided Learning, Math Animator, Co-Writer, TutorBot, Knowledge Bases, Memory) are powerful but entirely self-directed.

To adapt DeepTutor for **secondary school** (ages ~11-18), the platform needs features that support **structured classroom environments**, **teacher oversight**, **age-appropriate safety**, **curriculum alignment**, and **collaborative learning** — while preserving the powerful AI tutoring that makes DeepTutor unique.

---

## 13 Essential Features for Secondary School

### 1. Classroom & Role Management System

**Who:** Teachers, Students, Admins

**What:** Multi-user authentication with role-based access control. Teachers create "classrooms" and invite students via class codes or email. Admins manage the school-wide instance.

- Teacher role: create classes, manage students, view all student activity, configure AI settings per class
- Student role: join classes, access assigned materials, limited AI configuration
- Admin role: manage teachers, school-wide settings, usage quotas

**Why critical:** The current single-user architecture is the #1 blocker. Every other school feature depends on knowing *who* is using the system and *what role* they have.

### 2. Assignment & Homework System

**Who:** Teachers (create), Students (complete)

**What:** Teachers create assignments tied to knowledge bases, with due dates, instructions, and rubrics. Assignment types:

- **Reading assignments** — assign Guided Learning paths from uploaded materials
- **Quiz assignments** — teacher-configured quizzes (topic, difficulty, question count, time limit) auto-generated from curriculum materials
- **Research assignments** — students use Deep Research on assigned topics, submit reports
- **Problem sets** — students use Deep Solve, teacher reviews solution traces
- **Writing assignments** — students use Co-Writer, teacher reviews drafts
- Submission tracking, late policy, resubmission support

**Why critical:** Assignments are the core workflow of secondary school. Without them, DeepTutor is just a fancy chatbot — with them, it becomes a structured learning tool.

### 3. Teacher Dashboard & Live Classroom Grid

**Who:** Teachers

**What:** A dedicated dashboard with a **real-time classroom grid view** — a tiled/grid layout where each tile represents one student, showing:

- **Live interaction feed:** teacher can see what each student is currently asking the AI and what the AI is responding, in real-time (like monitoring a physical classroom)
- **Click-to-expand:** click any student tile to see their full conversation history, or open side-by-side to monitor multiple students
- **Status indicators:** per-tile badges showing active/idle, on-task/off-topic, struggling/progressing
- **Intervention tools:** teacher can send a message directly into a student's AI conversation ("Try thinking about it this way..."), pause a student's AI access, or flag a conversation for follow-up
- **Assignment status:** submitted / in-progress / not started / late, with grade distribution
- **Learning progress:** per-student mastery across curriculum topics (derived from quiz scores, Guided Learning completion, Memory profiles)
- **Struggle detection:** flag students who repeatedly fail quiz questions on a topic, spend excessive time, or show declining engagement
- **AI interaction insights:** what topics students are asking about most, common misconceptions surfaced by quiz errors

**Why critical:** This is the digital equivalent of walking around the classroom and looking over students' shoulders. Teachers need to see ALL student-AI interactions in a single view to identify who needs help, who is off-task, and who is excelling — without waiting for assignment submissions.

### 4. Curriculum-Aligned Knowledge Base Templates

**Who:** Teachers, Content Admins

**What:** Pre-built, standards-mapped knowledge bases for common secondary school subjects:

- Aligned to national/regional curriculum standards (e.g., Common Core, NGSS, UK National Curriculum, HKDSE)
- Subject packs: Mathematics (Algebra, Geometry, Calculus), Sciences (Biology, Chemistry, Physics), English Language Arts, History, Geography
- Each pack includes: textbook-grade reference materials, topic taxonomy, suggested quiz configurations, Guided Learning paths
- Teachers can customize, extend, or build their own from scratch

**Why critical:** Most teachers don't have time to upload and organize all curriculum materials from scratch. Ready-made packs dramatically lower the adoption barrier.

### 5. Quiz & Assessment Center (Enhanced)

**Who:** Teachers (configure), Students (take)

**What:** Expand the existing quiz generation into a full assessment system:

- **Formative quizzes:** low-stakes practice with instant AI feedback and explanations (existing capability, enhanced)
- **Summative assessments:** timed, proctored-mode quizzes with no AI assistance during the test, auto-graded, results sent to teacher
- **Adaptive difficulty:** quizzes that adjust question difficulty based on student performance in real-time
- **Question banks:** teachers curate and approve AI-generated questions, build reusable question pools per topic
- **Exam simulation:** mimic real exam formats (e.g., GCSE, SAT, AP, HKDSE) with proper timing and section structure
- **Spaced repetition review:** automatically resurface questions students previously got wrong at optimal intervals

**Why critical:** Assessment is how learning is measured in schools. The current quiz feature is powerful but unstructured — schools need grading, timing, and anti-cheating controls.

### 6. Content Safety & AI Guardrails

**Who:** Admins, Teachers (configure), Students (protected)

**What:** Age-appropriate content filtering and AI behavior controls:

- **Content filtering:** block or flag inappropriate, violent, or age-inappropriate AI responses
- **Topic restrictions:** teachers can restrict AI conversations to curriculum-relevant topics per class (e.g., a math class AI won't help write essays)
- **Citation requirements:** AI always cites sources from the knowledge base, discouraging fabrication
- **Usage limits:** configurable daily/weekly AI interaction quotas to prevent over-reliance
- **Prompt injection protection:** prevent students from jailbreaking the AI tutor
- **Audit logging:** all AI interactions logged for teacher/admin review if needed

**Why critical:** Schools have duty-of-care obligations. Parents and administrators need assurance that AI interactions are safe, on-topic, and transparent.

### 7. Student Progress Portfolio & Learning Journal

**Who:** Students (own), Teachers (view), Parents (optional view)

**What:** A personal learning portfolio that automatically captures:

- **Learning timeline:** visual history of topics studied, quizzes taken, assignments completed
- **Mastery map:** topic-by-topic competency visualization (building on the existing Memory feature)
- **Achievement badges:** gamification elements for milestones (completed 10 quizzes, mastered Algebra chapter, 7-day study streak)
- **Reflection journal:** students write reflections on their learning, prompted by AI
- **Export:** generate PDF progress reports for parent-teacher conferences

**Why critical:** Secondary students benefit from seeing their own growth. Portfolios support metacognition, motivation, and parent communication — all essential for the age group.

### 8. Collaborative Learning Spaces

**Who:** Students (in groups), Teachers (configure)

**What:** Group-based learning features:

- **Study groups:** teacher assigns students to small groups that share a conversation space with the AI tutor
- **Peer tutoring:** pair stronger and weaker students; the AI facilitates Socratic dialogue between them
- **Group projects:** shared knowledge bases and Co-Writer documents for collaborative research/writing
- **Discussion boards:** class-wide Q&A where students can post questions, answer peers, and the AI can contribute
- **Shared notebooks:** groups can build shared notebooks from their learning sessions

**Why critical:** Collaborative learning is a core pedagogy in secondary education. The current platform is entirely solo — group features reflect how real classrooms work.

### 9. Parent/Guardian Portal

**Who:** Parents/Guardians

**What:** A simplified read-only view for parents:

- **Weekly summary:** automated email/dashboard showing what their child studied, time spent, quiz scores, assignments due/completed
- **Progress alerts:** notifications when a student is falling behind, missing assignments, or excelling
- **Teacher messages:** direct communication channel with the teacher through the platform
- **Activity transparency:** parents can see (but not modify) their child's learning activity log

**Why critical:** Parental engagement is one of the strongest predictors of academic success in secondary school. A portal keeps parents informed without requiring them to learn the full platform.

### 10. Lesson Planning & Teaching Assistant for Teachers

**Who:** Teachers

**What:** AI tools specifically designed for teachers (not students):

- **Lesson plan generator:** input a topic + curriculum standard + class level, get a structured lesson plan with activities, timing, and DeepTutor integration points
- **Material generator:** auto-generate worksheets, handouts, slide outlines from knowledge base content
- **Differentiated instruction:** AI suggests modifications for advanced students, struggling students, and students with learning accommodations
- **Quiz builder assistant:** teacher describes what they want to assess, AI generates a draft quiz for teacher review and approval
- **Marking assistant:** AI pre-grades written assignments with suggested scores and feedback, teacher reviews and finalizes

**Why critical:** Teachers are overworked. AI that saves teacher prep time (not just student study time) is the key to institutional adoption.

### 11. Offline Mode & Low-Bandwidth Support

**Who:** Students, Teachers

**What:** Support for schools with limited internet infrastructure:

- **Offline knowledge base access:** cache curriculum materials locally for offline reading
- **Lightweight mode:** text-only UI option that works on slow connections and older devices
- **Batch sync:** queue AI interactions when offline, sync when reconnected
- **Progressive Web App (PWA):** installable on phones/tablets without app store distribution

**Why critical:** Many secondary schools (especially in developing regions) have unreliable internet. Offline/low-bandwidth support dramatically expands accessibility.

### 12. Accessibility & Inclusive Design

**Who:** All users, especially students with disabilities

**What:** Compliance with accessibility standards:

- **Screen reader support:** full ARIA labeling, keyboard navigation throughout
- **Text-to-speech:** AI responses can be read aloud (critical for students with reading difficulties/dyslexia)
- **Speech-to-text:** students can speak questions instead of typing
- **Font/contrast options:** dyslexia-friendly fonts, high-contrast mode, adjustable text size
- **Multilingual support:** expand beyond English/Chinese to cover languages used in target schools
- **Simplified UI mode:** reduced cognitive load option for students who find the full interface overwhelming

**Why critical:** Schools serve diverse learners. Legal requirements (ADA, WCAG) aside, inclusive design is a moral and practical necessity.

### 13. Gamification & Motivation Engine

**Who:** Students

**What:** Game-like elements designed for teenage engagement:

- **XP and leveling:** earn experience points for completing quizzes, assignments, study sessions
- **Streaks:** daily study streaks with visual tracking (similar to Duolingo)
- **Leaderboards:** opt-in class leaderboards (teacher-configurable, can be anonymous)
- **Challenges:** weekly AI-generated challenges ("Master 5 new vocabulary words", "Solve 10 geometry proofs")
- **Unlockable themes/avatars:** cosmetic rewards for sustained engagement

**Why critical:** Teenage motivation is fragile. Gamification, when done respectfully, significantly increases engagement and habit formation — critical for a tool that competes with social media for attention.

---

## Implementation Priority

| Priority | Feature | Reason |
|----------|---------|--------|
| P0 | 1. Classroom & Role Management | Foundation — everything else depends on it |
| P0 | 6. Content Safety & Guardrails | Non-negotiable for school deployment |
| P1 | 2. Assignment & Homework System | Core school workflow |
| P1 | 3. Teacher Dashboard & Classroom Grid | Teachers need real-time visibility |
| P1 | 5. Quiz & Assessment Center | Direct enhancement of existing feature |
| P2 | 4. Curriculum-Aligned Templates | Adoption accelerator |
| P2 | 10. Lesson Planning & Teaching Tools | Teacher value proposition |
| P2 | 7. Student Progress Portfolio | Student motivation + parent communication |
| P3 | 9. Parent/Guardian Portal | Parental engagement |
| P3 | 8. Collaborative Learning Spaces | Pedagogical best practice |
| P3 | 13. Gamification & Motivation | Engagement for teens |
| P3 | 12. Accessibility & Inclusive Design | Legal/moral requirement |
| P4 | 11. Offline Mode & Low-Bandwidth | Expands reach |

---

## Existing Features to Leverage

These current DeepTutor capabilities map directly to school use cases:

| Existing Feature | School Use Case |
|-----------------|-----------------|
| Quiz Generation | Assessment Center foundation |
| Guided Learning | Structured lesson delivery |
| Knowledge Bases | Curriculum material management |
| Memory system | Student progress tracking foundation |
| TutorBot | Personalized per-subject tutors |
| Co-Writer | Writing assignments |
| Deep Research | Research assignments |
| Notebooks | Portfolio/journal foundation |
| i18n support (i18next) | Multilingual expansion |

---

## Summary

The 13 features above transform DeepTutor from a **personal AI learning tool** into a **school-ready learning management system (LMS) with AI superpowers**. The critical insight is that secondary schools need **structure** (roles, assignments, grades, schedules) and **safety** (content filtering, audit trails, guardrails) wrapped around the existing AI capabilities. The AI tutoring is already excellent — the gap is the institutional scaffolding that makes it deployable in a classroom of 30+ students with a teacher who needs oversight and control.

---

## Implementation & Deployment Strategy

### Current Architecture (Limitations)

DeepTutor today runs as a **single-user, single-instance** application:

- **Database**: SQLite file (`data/user/chat_history.db`) — no multi-user support
- **Auth**: None — all API endpoints are open (`allow_origins=["*"]`)
- **Isolation**: Zero — any API call can access any session or knowledge base
- **Config**: Global YAML files (`main.yaml`, `agents.yaml`) — one config for all
- **LLM**: Requires cloud API keys (OpenAI, Anthropic, etc.)
- **Deployment**: Single Docker container with supervisord running FastAPI + Next.js

For schools, this needs to change. Below is a strategy that is **simple to start**, **easy to scale**, and **supports offline deployment**.

---

### Recommended Approach: "School-in-a-Box" Appliance

The simplest, most school-friendly model: **one self-contained Docker deployment per school** that includes everything — app, database, LLM, and embeddings — with no internet required.

#### Phase 1: Single-School Deployment (Simple)

```
┌─────────────────────────────────────────────────────┐
│  School Server (Docker Compose)                     │
│                                                     │
│  ┌──────────────┐  ┌──────────────┐                 │
│  │  DeepTutor   │  │   Ollama     │                 │
│  │  (FastAPI +  │──│  (Local LLM  │                 │
│  │   Next.js)   │  │  + Embedding)│                 │
│  └──────┬───────┘  └──────────────┘                 │
│         │                                           │
│  ┌──────┴───────┐                                   │
│  │  PostgreSQL  │  (replaces SQLite)                │
│  │  (single     │                                   │
│  │   instance)  │                                   │
│  └──────────────┘                                   │
│                                                     │
│  Volume: /data/knowledge_bases                      │
│  Volume: /data/user                                 │
└─────────────────────────────────────────────────────┘
```

**What changes from current architecture:**

1. **Add PostgreSQL** — replace SQLite for multi-user concurrency
   - Add `user_id` and `school_id` columns to all existing tables
   - Use SQLAlchemy or raw asyncpg (keep it simple, match current raw-SQL style)
   - Migration: one-time script to convert existing SQLite schema

2. **Add lightweight JWT auth** — minimal, no external dependency
   - New tables: `users` (id, email, name, role, hashed_password, school_id), `schools`, `classrooms`
   - FastAPI middleware: decode JWT on every request, inject `current_user` into request state
   - Login endpoint: email + password → JWT token
   - Student onboarding: teacher generates class invite code → student signs up with code

3. **Add Ollama for offline LLM** — already supported via `LLM_BINDING=ollama`
   - Bundle Ollama container in docker-compose with a pre-downloaded model
   - Recommended models for school use:
     - LLM: `qwen2.5:14b` or `llama3.1:8b` (good quality, runs on modest GPU)
     - Embedding: `nomic-embed-text` or `bge-large-en-v1.5`
   - For schools with no GPU: `qwen2.5:7b` with CPU-only (slower but functional)

4. **Add RBAC middleware** — simple role check on each endpoint
   - Three roles: `admin`, `teacher`, `student`
   - Decorators: `@require_role("teacher")` on assignment/dashboard endpoints
   - Students can only access their own sessions, assigned knowledge bases
   - Teachers can access all student data within their classrooms

**docker-compose.school.yml** (conceptual):
```yaml
services:
  deeptutor:
    image: ghcr.io/hkuds/deeptutor:school
    depends_on: [postgres, ollama]
    environment:
      - DATABASE_URL=postgresql://deeptutor:pass@postgres:5432/deeptutor
      - LLM_BINDING=ollama
      - LLM_HOST=http://ollama:11434
      - LLM_MODEL=qwen2.5:14b
      - EMBEDDING_BINDING=ollama
      - EMBEDDING_HOST=http://ollama:11434
      - EMBEDDING_MODEL=nomic-embed-text
      - JWT_SECRET=${JWT_SECRET}
      - SCHOOL_MODE=true
    volumes:
      - ./data:/app/data

  postgres:
    image: postgres:16-alpine
    volumes:
      - pgdata:/var/lib/postgresql/data

  ollama:
    image: ollama/ollama:latest
    volumes:
      - ollama_models:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - capabilities: [gpu]  # optional, works without GPU too

volumes:
  pgdata:
  ollama_models:
```

**Offline setup for IT staff:**
```bash
# 1. On a machine WITH internet, pull everything
docker compose -f docker-compose.school.yml pull
docker save deeptutor postgres ollama > deeptutor-school.tar

# 2. Also download the LLM model
docker run ollama/ollama pull qwen2.5:14b
docker run ollama/ollama pull nomic-embed-text

# 3. Transfer deeptutor-school.tar + ollama models to school server via USB

# 4. On the school server (no internet needed)
docker load < deeptutor-school.tar
docker compose -f docker-compose.school.yml up -d
```

---

#### Phase 2: District / Multi-School Scale-Up

When a school district wants to manage multiple schools, add a **thin orchestration layer** on top of the same architecture:

```
┌────────────────────────────────────────────┐
│  District Management Portal                │
│  (Admin dashboard for all schools)         │
└───────┬────────────┬───────────┬───────────┘
        │            │           │
   ┌────┴───┐  ┌────┴───┐  ┌───┴────┐
   │School A│  │School B│  │School C│
   │(Docker)│  │(Docker)│  │(Docker)│
   └────────┘  └────────┘  └────────┘
   (on-prem)   (on-prem)   (cloud)
```

**Two scaling strategies:**

| Strategy | When to use | How |
|----------|------------|-----|
| **Shared PostgreSQL** | Schools on same network / cloud | All schools share one PostgreSQL, isolated by `school_id` column. Single DeepTutor instance serves all. |
| **Instance-per-school** | Offline schools, data sovereignty | Each school gets its own Docker Compose stack. District portal connects to each via VPN/API. |

**For most secondary schools, instance-per-school is better** because:
- Schools often have their own servers and IT policies
- Offline capability per school
- No single point of failure
- Data stays physically within the school (privacy regulations)
- Simple: if one school's instance breaks, others are unaffected

---

#### Phase 3: Cloud Hybrid (Optional)

For schools that want cloud benefits + offline resilience:

```
┌─────────────────────┐     ┌──────────────────┐
│  Cloud (optional)   │     │  School Server   │
│                     │     │  (always works)  │
│  - Shared models    │◄───►│  - Local Ollama  │
│  - Central analytics│sync │  - Local Postgres │
│  - Backup storage   │     │  - Full DeepTutor│
└─────────────────────┘     └──────────────────┘
```

- School runs fully offline by default
- When internet is available, syncs analytics/backups to cloud
- Cloud provides: model updates, curriculum template distribution, cross-school analytics
- School works 100% without cloud — cloud is optional enhancement

---

### Implementation Roadmap (Phased)

#### Sprint 1 (2-3 weeks): Auth + Multi-User Foundation
**Files to modify:**
- `deeptutor/api/main.py` — add auth middleware
- `deeptutor/services/session/sqlite_store.py` — add user_id filtering (or replace with PostgreSQL)
- New: `deeptutor/api/auth/` — JWT auth module (login, register, invite codes)
- New: `deeptutor/db/models.py` — user, school, classroom tables
- `web/` — add login page, role-based nav hiding

**Keep it simple:**
- Use `python-jose` for JWT, `passlib` for password hashing
- Add `user_id` to existing session queries (WHERE clause)
- PostgreSQL via `asyncpg` (raw SQL, matching existing style)
- Frontend: simple login form → store JWT in httpOnly cookie

#### Sprint 2 (2-3 weeks): Teacher Dashboard + Classroom Grid
**Files to modify:**
- New: `web/app/(workspace)/classroom/` — classroom grid page
- New: `deeptutor/api/routers/classroom.py` — student activity endpoints
- Modify: WebSocket in `deeptutor/api/routers/unified_ws.py` — broadcast student events to teacher
- New: `web/components/classroom/StudentGrid.tsx` — real-time tile grid

**Architecture:**
- Teacher opens classroom grid → WebSocket subscribes to all student sessions in that class
- Each student tile shows last message + status (via existing EventBus)
- Click tile → full session history (reuse existing `ChatMessages.tsx`)

#### Sprint 3 (2-3 weeks): Assignments + Enhanced Quizzes
**Files to modify:**
- New: `deeptutor/db/assignments.py` — assignment CRUD
- New: `deeptutor/api/routers/assignments.py` — create, submit, grade endpoints
- Modify: `web/components/quiz/` — add timed mode, teacher review
- New: `web/app/(workspace)/assignments/` — assignment list + submission UI

**Leverage existing:**
- Quiz generation already works → add teacher approval + grading layer
- Guided Learning already works → wrap in assignment context with due dates
- Co-Writer already works → add submission endpoint

#### Sprint 4 (1-2 weeks): Content Safety + Offline Deployment
**Files to modify:**
- New: `deeptutor/services/safety/` — content filter middleware
- Modify: `deeptutor/api/main.py` — add safety middleware to LLM response pipeline
- New: `docker-compose.school.yml` — school deployment with Ollama + PostgreSQL
- New: `scripts/offline-setup.sh` — offline installation script

---

### Hardware Recommendations for Schools

| Setup | Hardware | Students | LLM Quality |
|-------|----------|----------|-------------|
| **Minimal** (CPU only) | Any modern PC, 16GB RAM | 5-10 concurrent | Basic (7B model, slow) |
| **Recommended** | Server with 1x RTX 3060/4060 (12GB VRAM), 32GB RAM | 20-30 concurrent | Good (14B model) |
| **Optimal** | Server with 1x RTX 3090/4090 (24GB VRAM), 64GB RAM | 40-60 concurrent | Excellent (32B model) |
| **Cloud hybrid** | Minimal local + cloud LLM API | Unlimited | Best (GPT-4o / Claude) |

**Cheapest offline option:** A single mini-PC with a consumer GPU (RTX 4060, ~$300) can serve a classroom of 30 students running `qwen2.5:14b` through Ollama. Total hardware cost: ~$800-1200.

---

### Technology Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Database** | PostgreSQL (replace SQLite) | Multi-user concurrency, scales to district level, battle-tested |
| **Auth** | JWT + bcrypt (self-contained) | No external IdP needed, works offline, simple |
| **LLM (offline)** | Ollama + Qwen 2.5 / Llama 3.1 | Free, fast, good quality, already supported |
| **LLM (cloud)** | Keep existing multi-provider | OpenAI/Anthropic/etc. for schools with budget + internet |
| **Embedding (offline)** | Ollama + nomic-embed-text | Good quality, runs on CPU, no API key needed |
| **Deployment** | Docker Compose (all-in-one) | Simple for school IT staff, portable, offline-friendly |
| **Scaling** | Instance-per-school | Data sovereignty, offline support, fault isolation |
| **Real-time** | Existing WebSocket + EventBus | Already built for chat streaming, extend for classroom grid |
