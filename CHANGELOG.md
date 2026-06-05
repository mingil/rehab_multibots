# 📝 Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-06-05

### Added
- **Obsidian Second Brain Integration:** Completely separated Email HTML and Obsidian Markdown generation. The bot now attaches a perfectly formatted `.md` file to the email, complete with YAML Frontmatter (metadata/tags) and a Zotero to-do checklist (`- [ ]`) for seamless PKM (Personal Knowledge Management) syncing.
- **Deep Parsing & Metadata Extraction:** Introduced an advanced OpenAlex parsing algorithm to accurately extract First Authors (`et al.`), Journal Names, and dynamically infer the `Study Design` (e.g., RCT, Meta-analysis, Guideline) based on concepts and abstract keywords.
- **Telegram Premium Mini-Dashboard:** Upgraded Telegram notifications from a simple alert to an "Executive Summary". It now features an AI-generated 3-line summary (TL;DR) parsed via Regex, direct mobile quick-links to the Top 3 highly cited papers, and automatically generated hashtags for easy searching (e.g., `#RehabBot #통증재활 #2026_06`).
- **Target Journal Transparency Board:** Hardcoded the official target journal pool with their academic tiers (e.g., JCR Q1) into the Python configuration. This list is transparently rendered as a clean HTML table at the top of every email and Obsidian file.
- **Massive Expansion for December AI Bot:** The 12th bot (Medical AI) now scans a combined total of 50 top-tier journals, encompassing all PM&R specialty journals plus 11 world-class general/digital medical journals (including *NEJM, The Lancet, JAMA, Nature Medicine, JMIR*).
- **Universal Remote Control (`manual_run.py`):** Added an interactive CLI remote control to trigger bots manually without disrupting the scheduled cron jobs. Included strict absolute-path binding (`sys.path.insert`) to resolve `ModuleNotFoundError` during manual executions.

### Changed
- **Premium Academic Email UI/UX:** Completely redesigned the email HTML template into a "Notion-style" academic minimalism theme featuring a top "Metadata Dashboard", clean typography, and a "Card-view" paper list with direct, clickable DOI hyperlinks.
- **Direct DOI Hyperlinking (AI Prompting):** Forced the Gemini AI to natively embed direct DOI hyperlinks into the body text (`[Paper Title](DOI)`), eliminating the need for users to scroll to the bottom reference list to access a study.
- **AI Engine Migration:** Deprecated the legacy `google-generativeai` package and fully migrated to the latest official `google-genai` SDK to prevent deprecation errors and improve stability.

### Fixed
- **Terminal Warning Suppression:** Resolved the terminal spam issue caused by `pyzotero`'s outdated datetime module (`WheneverDeprecationWarning`) by implementing strict warning filters, maintaining a pristine log environment.
- **Dynamic DB Schema Migration & Cache Fix:** Safely upgraded the SQLite DB schema to accommodate new metadata columns (`journal`, `authors`, `study_design`). Resolved the "Unknown Journal/Authors" issue by purging corrupted legacy caches.

---

## [1.1.0] - 2026-06-04

### Changed
- **Scheduling Logic (Annual Rotation):** Redesigned the execution schedule from a daily check for `RUN_DAY` to a yearly rotation based on `RUN_MONTH`. Each of the 11 bots now operates exclusively in its assigned month to avoid API rate limits and notification fatigue.
- **Execution Time:** Moved the daily schedule check time from 09:00 AM to 06:30 AM.

### Added
- **Catch-up Mechanism (Fail-safe):** Implemented a persistent state tracker (`bot_settings` table in SQLite). If the Synology NAS is offline during the scheduled time, the bot will automatically detect the missed execution and deliver the briefing immediately upon server boot within the assigned month.

---

## [1.0.0] - 2026-06-01

### Added
- Initial release of Rehab Multi-Bots.
- Configured 11 isolated PM&R sub-specialty bots using Docker Compose anchors.
- Automated literature harvesting via OpenAlex API (Recent, Mainstream, Classic periods).
- AI research curation using Google Gemini 2.5 Flash API to identify research gaps.
- Automated reference deduplication and syncing to Zotero API.
- Local caching via SQLite3 to prevent redundant API calls.
- Omni-channel notifications via HTML Email and Telegram.
