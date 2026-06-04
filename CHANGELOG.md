# 📝 Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
