<div align="center">

# 🤖 Rehab Multi-Bots

**AI-Powered Automated Research Pipeline for Physical Medicine and Rehabilitation (PM&R)**

[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB.svg?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/)
[![Gemini](https://img.shields.io/badge/Google_Gemini-2.5_Flash-8E75B2.svg?style=flat-square&logo=google&logoColor=white)](https://ai.google.dev/)
[![Zotero](https://img.shields.io/badge/Reference-Zotero_API-CC2936.svg?style=flat-square&logo=zotero&logoColor=white)](https://www.zotero.org/)
[![SQLite3](https://img.shields.io/badge/SQLite-3-003B57.svg?style=flat-square&logo=sqlite&logoColor=white)](https://www.sqlite.org/)

</div>

<br>

> **Rehab Multi-Bots** is an intelligent automated literature curation system deployed on Synology NAS via Docker Compose. It manages **11 distinct bots**, each dedicated to a specific sub-specialty of Rehabilitation Medicine, providing clinical researchers with highly structured, AI-curated research insights.

## ✨ Key Features

- **🏢 11 Sub-Specialty Bots**
  Efficiently operates 11 independent instances using a single Python codebase via Docker Compose anchors (`&bot-template`).
- **📚 Smart Literature Harvesting**
  Automatically fetches top-cited papers (categorized by recent trends, mainstream, and classic foundations) using the **OpenAlex API**.
- **🧠 AI Research Curation**
  Leverages **Google Gemini 2.5 Flash** to analyze paper abstracts, filter out generic methodologies (e.g., PRISMA guidelines), and propose highly actionable, novel research ideas (Research Gaps).
- **💾 Automated Reference Management**
  Deduplicates and syncs fetched papers directly into designated sub-specialty **Zotero** folders.
- **⚡ Local SQLite Caching**
  Maintains lightweight, per-bot local databases (`history_*.db`) to prevent redundant API calls and avoid duplicate notifications.
- **🔔 Omni-Channel Notifications**
  Delivers beautifully formatted AI briefings and raw literature lists via **HTML Email** and **Telegram**.

<br>

## 🗓️ Sub-Specialty Schedule

To optimize server load and API rate limits, each bot wakes up automatically at **09:00 AM** on its designated day of the month.

| Day | Bot Container Name | PM&R Sub-Specialty |
| :---: | :--- | :--- |
| **1st** | `bot_01_general` | General & Comprehensive Rehab |
| **2nd** | `bot_02_neuro` | Neurorehabilitation & Stroke |
| **3rd** | `bot_03_sci` | Spinal Cord Injury |
| **4th** | `bot_04_peds` | Pediatric Rehabilitation |
| **5th** | `bot_05_cardio` | Cardiopulmonary Rehabilitation |
| **6th** | `bot_06_dysphagia`| Dysphagia (Swallowing Disorders) |
| **7th** | `bot_07_emg` | EMG & Electrodiagnosis |
| **8th** | `bot_08_msk` | Musculoskeletal & Ultrasound |
| **9th** | `bot_09_pain` | Pain Medicine |
| **10th** | `bot_10_sports` | Sports Rehabilitation |
| **11th** | `bot_11_prosthetics`| Prosthetics, Orthotics & Biomechanics |

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
