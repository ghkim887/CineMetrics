# 🎬 CineMetrics

> Data-driven movie discovery for every kind of viewer

**CS 3200 - Database Design | Spring 2026 | Northeastern University**

---

## 👥 Team GERCK

| Name | Email |
|------|-------|
| Glenn Kule | kule.g@northeastern.edu |
| Ella Yuan | yuan.el@northeastern.edu |
| Kenneth Kim | kim.gyun@northeastern.edu |
| Ryan Ma | ma.ry@northeastern.edu |
| Cecilia Kye | kye.c@northeastern.edu |

---

## 🎥 Overview

With thousands of movies available across dozens of streaming platforms, users face a growing problem: too many choices and too little time. Existing recommendation systems tend to rely on generic trending lists or broad genre categories, leaving users scrolling endlessly without finding something they'll actually enjoy.

**CineMetrics** is a data-driven movie recommendation platform that solves this by putting user data at the center of the discovery experience. By collecting and analyzing individual ratings, written reviews, viewing history, and genre preferences, CineMetrics builds a personalized profile for each user that improves with every interaction.

---

## 🎭 User Personas

CineMetrics is built around four distinct user personas, each with unique needs and workflows:

- **🍿 Jake Morrison — Casual Viewer**
  Wants quick, reliable suggestions without endless browsing. Values speed and simplicity over deep customization.

- **🎞️ Priya Sharma — Movie Enthusiast**
  Craves deep personalized discovery and community engagement. Writes reviews, curates watchlists, and explores niche genres.

- **🛠️ Marcus Chen — Platform Administrator**
  Manages and maintains the movie database. Oversees content quality, moderates reviews, and handles user accounts.

- **📊 Elena Vasquez — Data Analyst**
  Tracks trends and extracts actionable insights. Uses platform-wide analytics to inform business decisions.

---

## 🧱 Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Streamlit (Python) |
| Backend | Flask REST API (Python) |
| Database | MySQL 9 |
| Infrastructure | Docker Compose |

---

## 🏗️ Architecture

CineMetrics follows a classic **3-tier architecture** with each tier running in its own Docker container:

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│  Streamlit  │──────▶│ Flask REST  │──────▶│   MySQL 9   │
│   :8501     │       │    :4000    │       │   :3200     │
└─────────────┘       └─────────────┘       └─────────────┘
   Presentation          Application             Data
```

- **Presentation tier** — Streamlit renders the UI and routes users to persona-specific pages
- **Application tier** — Flask exposes a RESTful API organized into 7 blueprints
- **Data tier** — MySQL 9 stores all persistent state across 13 relational tables

---

## 🚀 Getting Started

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Git

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ghkim887/CineMetrics.git
   cd CineMetrics
   ```

2. **Create the environment file:**
   ```bash
   cp api/.env.template api/.env
   ```
   Edit `api/.env` if you want to change defaults (database password, etc.).

3. **Start all services:**
   ```bash
   docker compose up -d
   ```

4. **Access the application:**
   - 🎨 **Frontend** — http://localhost:8501
   - 🔌 **API** — http://localhost:4000
   - 🗄️ **Database** — `localhost:3200` (MySQL)

### Resetting the Database

To reload the schema and seed data from scratch:

```bash
docker compose down db -v
docker compose up db -d
```

> The `-v` flag removes the database volume, which triggers the container to re-run every `.sql` file in `database-files/` on the next startup.

---

## 🗃️ Database Schema

The CineMetrics database is built on **13 normalized tables** covering movies, users, ratings, reviews, watchlists, genres, recommendations, moderation, and analytics.

Full DDL lives at [`database-files/00_cinemetrics_schema.sql`](database-files/00_cinemetrics_schema.sql), and seed data is loaded from [`database-files/01_cinemetrics_seed.sql`](database-files/01_cinemetrics_seed.sql).

---

## 🔌 API Overview

The Flask backend is organized into **7 blueprints**, each handling a focused slice of the domain:

| Blueprint | Prefix | Purpose |
|-----------|--------|---------|
| `movies` | `/movies` | Movie catalog CRUD |
| `users` | `/users` | User history, ratings, and stats |
| `reviews` | `/reviews` | Review CRUD and flagging |
| `watchlists` | `/watchlists` | Watchlist management |
| `recommendations` | `/recommendations` | Recommendation engine |
| `admin` | `/admin` | User & review moderation |
| `analytics` | `/analytics` | Platform-wide analytics |

---

## 📁 Project Structure

```
cs3200-app/
├── api/                    # Flask REST API
│   └── backend/
│       ├── movies/         # Movie catalog routes
│       ├── users/          # User management routes
│       ├── reviews/        # Review routes
│       ├── watchlists/     # Watchlist routes
│       ├── recommendations/# Recommendation routes
│       ├── admin/          # Admin/moderation routes
│       └── analytics/      # Analytics routes
├── app/                    # Streamlit frontend
│   └── src/
│       ├── Home.py         # Landing page
│       ├── modules/        # Shared UI modules (nav, etc.)
│       └── pages/          # Persona-specific pages
├── database-files/         # SQL schema + seed scripts
│   ├── 00_cinemetrics_schema.sql
│   └── 01_cinemetrics_seed.sql
├── docker-compose.yaml     # Service orchestration
└── README.md
```

---

## 🎬 Demo Video

*[Demo Video Link - Coming Soon]*

---

## 📜 License

Educational use only — developed for CS 3200 (Database Design), Spring 2026 at Northeastern University.
