<div align="center">

# 🤖 Rehab Multi-Bots

**AI-Powered Automated Research Pipeline for Physical Medicine and Rehabilitation (PM&R)**

[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB.svg?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/)
[![Gemini](https://img.shields.io/badge/Google_Gemini-3.8_Flash-8E75B2.svg?style=flat-square&logo=google&logoColor=white)](https://ai.google.dev/)
[![Zotero](https://img.shields.io/badge/Reference-Zotero_API-CC2936.svg?style=flat-square&logo=zotero&logoColor=white)](https://www.zotero.org/)
[![SQLite3](https://img.shields.io/badge/SQLite-3-003B57.svg?style=flat-square&logo=sqlite&logoColor=white)](https://www.sqlite.org/)

<br>

**[ 📖 View Update History (Changelog) ](./CHANGELOG.md)**

</div>

<br>

> **Rehab Multi-Bots** is an intelligent automated literature curation system deployed on Synology NAS via Docker Compose. Operated by a **Single Master Scheduler (`multibot_master`)**, it dynamically manages **12 distinct sub-specialties** of Rehabilitation Medicine (including Medical AI), providing clinical researchers with highly structured, AI-curated research insights.

## ✨ Key Features

- **👑 Single Master Scheduler (12 Sub-Specialties)**
  Efficiently operates all 12 PM&R sub-specialty tracks from a single lightweight container (`multibot_master`) via dynamic monthly configuration (`BOT_REGISTRY`).
- **📚 Smart Literature Harvesting**
  Automatically fetches top-cited papers (categorized by recent trends, mainstream, and classic foundations) using the **OpenAlex API** with automatic cross-period deduplication.
- **🧠 2-Phase Hybrid AI Curation (`Gemini 3.8 Flash`)**
  Leverages **Google Gemini 3.8 Flash** (with automatic fallback to `3.6-flash` and `3.5-flash-lite`) in two stages: Phase 1 (Editor-in-Chief thematic categorization & study protocols) and Phase 2 (1:1 paper deep-dive with key findings, citation tips, and research gaps).
- **💾 Automated Reference Management & Local Backup**
  Deduplicates and syncs fetched papers directly into designated sub-specialty **Zotero** folders, while backing up `.md` (Obsidian) and `.html` reports locally to `/app/reports`.
- **⚡ Local SQLite Caching**
  Maintains lightweight, per-bot local databases (`data/history_*.db`) to prevent redundant API calls and avoid duplicate notifications.
- **🔔 Omni-Channel Notifications**
  Delivers beautifully formatted Notion-style HTML Email briefings (with Obsidian `.md` attachments) and Telegram Executive Dashboards.

<br>

## 🗓️ Sub-Specialty Schedule (Annual Rotation)

To optimize server load and minimize information fatigue, each bot operates on a **monthly rotation system**. They wake up automatically at **06:30 AM** during their designated month. *(Includes a Fail-Safe catch-up mechanism if the NAS is offline).*

| Run Month | Bot Container Name | PM&R Sub-Specialty |
| :---: | :--- | :--- |
| **January** | `bot_01_general` | General & Comprehensive Rehab |
| **February**| `bot_02_neuro` | Neurorehabilitation & Stroke |
| **March** | `bot_03_sci` | Spinal Cord Injury |
| **April** | `bot_04_peds` | Pediatric Rehabilitation |
| **May** | `bot_05_cardio` | Cardiopulmonary Rehabilitation |
| **June** | `bot_06_dysphagia`| Dysphagia (Swallowing Disorders) |
| **July** | `bot_07_emg` | EMG & Electrodiagnosis |
| **August** | `bot_08_msk` | Musculoskeletal & Ultrasound |
| **September**| `bot_09_pain` | Pain Medicine |
| **October** | `bot_10_sports` | Sports Rehabilitation |
| **November**| `bot_11_prosthetics`| Prosthetics, Orthotics & Biomechanics |
| December | bot_12_ai | AI & Machine Learning in PM&R |

<br>

## 🔄 Automated Workflow

1. **Trigger:** `schedule` runs daily. If the current date matches the `RUN_DAY` environment variable, the specific bot activates.
2. **Fetch:** Scans OpenAlex for top-cited papers matching the sub-specialty's targeted ISSNs.
3. **Filter:** Checks the local `SQLite` cache to avoid reprocessing existing papers.
4. **Sync:** Pushes deduplicated metadata and abstracts directly to `Zotero`.
5. **Analyze:** Sends the collected batch to the `Gemini API` with an advanced clinical prompting strategy.
6. **Broadcast:** Dispatches the final AI-generated HTML report to Gmail and Telegram.

<br>

## 🚀 Installation & Setup

### 1. Prerequisites
- Docker & Docker Compose
- API Keys & Credentials:
  - Google Gemini API Key
  - Zotero User ID & API Key
  - Telegram Bot Token & Chat ID
  - Gmail Address & App Password

### 2. Clone the Repository
```bash
git clone [https://github.com/mingil/rehab_multibots.git](https://github.com/mingil/rehab_multibots.git)
cd rehab_multibots
```

### 3. Environment Variables (.env)
Create a .env file based on the template. (Never commit .env to Git!)

```bash
cp .env.example .env
nano .env  # Fill in your secure credentials
```

### 4. Deploy via Docker Compose
Build the image and deploy the master scheduler in the background:

```bash
docker compose up -d --build
```

### 🛠️ Maintenance & Hot-Reload
This project utilizes Docker volume mounts (`/volume1/docker/rehab_multibots:/app`), meaning you can update the Python logic without rebuilding the entire Docker image.

Update Code & Apply:

```bash
git pull origin main
docker compose restart
```

Check Master Scheduler Logs:

```bash
docker logs -f multibot_master
```

Manual Remote Control (Interactive CLI):

```bash
docker exec -it multibot_master python manual_run.py
```

### 📂 Project Structure
```Plaintext
📦 rehab_multibots
 ┣ 📜 compose.yaml         # Master scheduler Docker Compose config
 ┣ 📜 Dockerfile           # Python 3.11 slim image setup
 ┣ 📜 requirements.txt     # Python dependencies
 ┣ 📜 main.py              # Master scheduler & pipeline execution logic
 ┣ 📜 manual_run.py        # Interactive CLI remote control for manual runs
 ┣ 📜 config.py            # 12-bot registry, target journals & env loader
 ┣ 📜 db_manager.py        # SQLite caching & auto schema migration
 ┣ 📜 openalex_client.py   # OpenAlex API harvesting & metadata parser
 ┣ 📜 zotero_client.py     # Zotero API deduplication & syncing
 ┣ 📜 gemini_client.py     # 2-Phase hybrid AI curation (Gemini 3.6 Flash)
 ┣ 📜 report_builder.py    # Obsidian Markdown, HTML Email & Telegram renderer
 ┣ 📜 notifier.py          # Telegram & Gmail SMTP notification logic
 ┣ 📜 logger.py            # Rotating file & console logger
 ┣ 📂 data/                # Per-specialty SQLite databases (history_*.db)
 ┣ 📂 logs/                # Execution logs (app_*.log)
 ┗ 📂 reports/             # Local backup of generated .md and .html reports
```

### 📜 License & Disclaimer
This project is for personal, academic, and non-commercial use. Please adhere to the API usage policies of Google Gemini, OpenAlex, and Zotero.

Disclaimer: AI-generated summaries and research insights should be critically reviewed by medical professionals. This tool is designed to assist in research planning and does not replace clinical judgment.
