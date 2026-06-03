# 🤖 Rehab Multi-Bots: AI-Powered Research Assistant

![Python](https://img.shields.io/badge/Python-3.11-blue.svg?logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg?logo=docker&logoColor=white)
![Gemini AI](https://img.shields.io/badge/AI-Gemini_2.5_Flash-8E75B2.svg?logo=google&logoColor=white)
![Zotero](https://img.shields.io/badge/Reference-Zotero_API-CC2936.svg?logo=zotero&logoColor=white)
![SQLite](https://img.shields.io/badge/Database-SQLite3-003B57.svg?logo=sqlite&logoColor=white)

An automated AI research pipeline specifically designed for **Physical Medicine and Rehabilitation (PM&R)**.

Deployed on a Synology NAS (Docker), this project operates **11 independent automated bots**, each dedicated to a specific sub-specialty of rehabilitation medicine. They autonomously harvest highly cited papers, sync metadata to Zotero, analyze trends using AI, and deliver structured research briefings via Email and Telegram.

---

## ✨ Key Features

- **🏢 11 Sub-Specialty Bots:** Manages 11 isolated instances via Docker Compose anchors (`&bot-template`), sharing a single Python codebase efficiently.
- **📚 Smart Literature Harvesting:** Fetches top-cited papers categorized by recent trends, mainstream research, and classic foundations using the **OpenAlex API**.
- **🧠 AI Research Curation:** Utilizes **Google Gemini 2.5 Flash** to analyze paper abstracts, filter out generic methodologies (like PRISMA guidelines), and propose 3 highly actionable novel research ideas (Research Gaps).
- **💾 Automated Reference Management:** Deduplicates and automatically saves fetched papers directly into specific sub-specialty Zotero folders.
- **⚡ Local Caching:** Uses lightweight `SQLite` (`history_*.db`) per bot to prevent redundant API calls and duplicate alerts.
- **🔔 Omni-Channel Notifications:** Delivers beautifully formatted HTML emails and instant Telegram alerts.
- **🕒 Scheduled Execution:** Each bot wakes up automatically at 09:00 AM on its designated day of the month, minimizing server load.

---

## 🗓️ Sub-Specialty Schedule

| Run Day | Bot Name | Sub-Specialty (Rehabilitation Medicine) |
| :---: | :--- | :--- |
| **1st** | `bot_01_general` | General & Comprehensive Rehab |
| **2nd** | `bot_02_neuro` | Neurorehabilitation & Stroke |
| **3rd** | `bot_03_sci` | Spinal Cord Injury |
| **4th** | `bot_04_peds` | Pediatric Rehabilitation |
| **5th** | `bot_05_cardio` | Cardiopulmonary Rehabilitation |
| **6th** | `bot_06_dysphagia` | Dysphagia (Swallowing Disorders) |
| **7th** | `bot_07_emg` | EMG & Electrodiagnosis |
| **8th** | `bot_08_msk` | Musculoskeletal & Ultrasound |
| **9th** | `bot_09_pain` | Pain Medicine |
| **10th** | `bot_10_sports` | Sports Rehabilitation |
| **11th** | `bot_11_prosthetics` | Prosthetics, Orthotics & Biomechanics |

---

## 🔄 Automated Workflow

1. **Trigger:** The script runs daily. If the current date matches the container's `RUN_DAY`, the bot activates.
2. **Fetch:** Scans OpenAlex for top-cited papers matching targeted ISSNs.
3. **Filter:** Checks local `SQLite` cache to avoid reprocessing known papers.
4. **Sync:** Pushes deduplicated metadata and abstracts to `Zotero`.
5. **Analyze:** Sends the collected batch to the `Gemini API` with an advanced "Senior Professor" prompt.
6. **Broadcast:** Dispatches the final AI-generated HTML report to Gmail and Telegram.

---

## 🚀 Installation & Setup

### 1. Prerequisites
- **Docker** and **Docker Compose**
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

### 3. Environment Variables
Create a .env file based on the provided template. Never commit .env to Git.

Bash
cp .env.example .env
nano .env # Fill in your API keys

### 4. Deploy via Docker Compose
Build the image and deploy all 11 bots in the background:

Bash
docker compose up -d --build
🛠️ Maintenance & Hot-Reload
Because the project utilizes Docker volume mounts, you can update the Python logic without rebuilding the Docker image:

Bash
# Pull latest code from Git
git pull origin main

# Restart containers to apply changes instantly
docker compose restart
Check Logs:

Bash
# View Docker logs for a specific bot
docker logs -f multibot_02_neuro
📂 Project Structure
Plaintext
.
├── compose.yaml          # Docker Compose configurations for 11 bots
├── Dockerfile            # Python 3.11 slim image setup
├── requirements.txt      # Dependencies
├── main.py               # Main execution logic and scheduling
├── config.py             # Global configurations & Env loaders
├── db_manager.py         # SQLite caching operations
├── openalex_client.py    # OpenAlex API wrapper
├── zotero_client.py      # Zotero API wrapper
├── gemini_client.py      # AI prompt engineering and analysis
└── notifier.py           # Telegram & Email notification dispatcher
📜 License & Disclaimer
This project is for personal, academic, and non-commercial use. Please adhere to the API usage policies of Google Gemini, OpenAlex, and Zotero.

Disclaimer: AI-generated reports should be reviewed by medical professionals. This tool is designed to assist in research planning, not to replace clinical judgment.
