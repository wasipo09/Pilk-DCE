# Pilk-Flights CLI Tool

A command-line tool for searching flights from Bangkok (BKK) to Tokyo (TYO). Features dual-mode operation: free web scraping and optional Skyscanner API integration.

**⚠️ Development Status: PAUSED**

This project is currently on ice. The flight search functionality is not working due to issues with free API providers:

- **Kiwi/Tequila API:** Requires paid account/key activation (not available on free tier)
- **Skyscanner API:** Complex setup with OIDC tokens (not implemented)
- **Duffel API:** Discontinued free tier
- **Google Flights/Kayak Scraping:** Timeouts and selector issues prevent reliable operation

---

## What Works

- ✅ **CLI Interface:** Fully functional with Typer
- ✅ **Rich Display:** Color-coded tables with statistics
- ✅ **Config Management:** Environment variables, dual-mode switching
- ✅ **Project Structure:** Clean separation of concerns
- ✅ **Setup Script:** Easy installation with pip install

---

## Current Issues

### API Providers
- Most free flight search APIs have been discontinued or require paid activation
- Kiwi/Tequila needs account activation; free tier access unclear
- Skyscanner requires OIDC tokens; complex setup for simple flight search

### Scraping Challenges
- **Google Flights:** Selector timeouts (15000ms limit exceeded)
- **Kayak:** Invalid URL construction (query parameters appended incorrectly)
- Both scrapers frequently return no results

### Architecture Decisions Made
- Dual-mode design (scraping + API) was good in theory
- Modular structure with separate `api_client.py` files
- Anti-bot protection with random delays and user-agent rotation

---

## Restarting This Project

To resume development, these issues need to be addressed:

1. **Switch to Paid API:** Use Amadeus, Skyscanner (paid), or fix Kiwi activation
2. **Fix Scraping Issues:** Update selectors, increase timeouts, fix URL construction
3. **Use Existing Tools:** Consider using Google Flights website directly or specialized scrapers
4. **API Improvements:** Implement proper Skyscanner API integration with OIDC tokens

---

## Installation

The CLI tool is installed and ready to use. To install Playwright browsers:

```bash
pip install -e .
playwright install chromium
```

---

## Project Structure

```
~/Projects/Pilk-Flights/
├── main.py           # CLI entry point (Typer)
├── scraper.py        # Playwright web scraper (needs fixes)
├── api_client_kiwi.py  # Kiwi API client (needs activation)
├── api_client.py     # Skyscanner API client (legacy)
├── parser.py         # Data parsing and normalization
├── filters.py        # Filtering and sorting
├── display.py        # Rich table output
├── config.py         # Configuration management
├── requirements.txt  # Python dependencies
├── README.md         # This file
└── .env.example      # Environment template
```

---

## Current Commit

**Branch:** main  
**Status:** Uncommitted changes

**Modified files:**
- `.env.example` — API key template
- `config.py` — Added API provider support
- `main.py` — CLI entry point
- `scraper.py` — Web scrapers (needs fixes)
- `api_client_kiwi.py` — Kiwi integration

**Untracked files:**
- `KIWI_API_IMPLEMENTATION.md` — Implementation notes
- `.env.backup` — Environment backup
- Test files

---

## Author

Created for Pilk projects.
