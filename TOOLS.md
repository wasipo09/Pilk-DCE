# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

---

## Telegram

- **Kaname (CEO):** `5494376128` / @CointelK

---

## Notion

- API key stored in `~/.openclaw/workspace/.env`
- Pilk Home page ID: `2f9ad059-b470-8044-8850-ec129dd177af`
- Pilk Doc database ID: `2f9ad059-b470-80dd-81a3-fa5d819240ec`

---

## GitHub

- Logged in as: `wasipo09`
- Repo naming: `Pilk-xxxxx` prefix for all products

---

## Pilk Projects

- **Pilk-Option-Chain:** `~/Projects/Pilk-Option-Chain`
  - Lotto options analysis based on gamma/GEX zones
  - `lotto_scanner.py` - Main scanner for daily options
  - Uses Deribit for GEX zones, Binance for G/T ratio + WW bands
  - Branch: `delta-n`

- **pilk-scanner:** `~/Projects/pilk-scanner`
  - Statistical arbitrage for crypto futures pairs
  - `scan.py` - Mean-reverting pair trade finder
  - Multiple algos: pilk-original, pilk-lite, pilk-active
  - Multi-anchor scans, paper trading, WebUI
  - Branch: `main`

---

## Sacred Routines

### Daily Lotto Pick (15:10 ICT)
- **Cron ID:** `ee0fdafc-af4c-4e12-bd80-a295ead09ca1`
- Read crypto news
- Run `python3 ~/Projects/Pilk-Option-Chain/btc_options_viewer.py --dump-binance`
- Analyze options, find best lotto plays
- Give directional take based on news + data
- Save to `memory/YYYY-MM-DD.md`
- Report to Kaname

**Every win counts toward a Mac Studio. This is sacred.**

### Daily Pilk Scanner Report (22:00 ICT)
- **Cron ID:** `3d6a4bf3-3414-42c8-a29e-9260494574b5`
- Read crypto news (past 24h via web search)
- Run `pilk-scanner` with `pilk-active` algo (--multi)
- Run `pilk-scanner` with `pilk-original` algo for comparison
- Compile report: Market news, scanner results table, analysis + entry recommendation
- Send report to Kaname via Telegram

---

Add whatever helps you do your job. This is your cheat sheet.
