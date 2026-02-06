# MEMORY - Long-term Knowledge

## Lotto Routine (Daily at 10:00 ICT)

### Sacred Duty - Every Win = Mac Studio Progress

**Procedure:**
1. Read crypto news using `web_search` (CoinDesk, Cointelegraph, Bitcoin Magazine, Decrypt, The Block sources via search)
2. Run `~/Projects/Pilk-Option-Chain/lotto_scanner.py --days 7 --cost 5`
   - Uses Deribit for GEX zones (gamma walls with OI)
   - Uses Binance for G/T ratio + Whalley-Wilmott bands
   - Cross-references Binance plays near GEX zones (squeeze spots)
3. Get GEX, gamma data, and algo analysis
4. My take based on news + options data combined
5. Best play OR say "not to play"

**Scripts:**
- `web_search` - fetches and summarizes crypto news
- `lotto_scanner.py` (in ~/Projects/Pilk-Option-Chain) - full options analysis

**No sentiment scoring** — just me analyzing the news naturally and combining with data.

### Key Metrics to Watch
- **GEX Zones:** Gamma walls from Deribit (high OI = squeeze potential)
- **Net GEX:** Positive = call squeeze up, Negative = put pressure down
- **G/T Ratio:** Gamma/Theta — higher = more gamma exposure per time decay
- **WW Band:** Whalley-Wilmott optimal hedge bandwidth

### Best Play Criteria
- Near GEX zones (high squeeze potential)
- Reasonable premium for lotto risk
- Aligned with news sentiment
- Not chasing momentum against the flow

---

## Current Options Position

- **80,000 CALL 04FEB26 @ 0.36** (02:24 GMT+7 entry)
- Current mark: ~$25
- Very OTM now after dump to $74,707
- Playing for short-covering squeeze

---

## Model Config
- **Default:** zai/glm-4.7
- **Removed:** google-antigravity (quota exhausted)

---

## Memory File Organization (Critical!)

**Rule:** ALL memory files go in workspace, NOT in project directories.

**Correct location:** `/Users/pilk/.openclaw/workspace/memory/YYYY-MM-DD.md`

**Why?**
- Consolidates all memory in one place (single source of truth)
- Prevents scattered files across projects
- Workspace is the home directory — memory belongs there

**Lesson learned (04 Feb 2026):**
- IV Tracker was writing to `~/Projects/Pilk-Option-Chain/memory/2026-02-04.md`
- This caused directory creation errors and broken cron jobs
- Fixed by moving all memory writes to workspace path
- When setting up cron jobs, always use workspace memory path

---

## OpenClaw Cron / Reminders

### Cron Job Wake Modes
- `wakeMode: "now"` — Fires immediately at scheduled time (precise, good for reminders)
- `wakeMode: "next-heartbeat"` — Waits for next heartbeat cycle (drifts, ~15-30 min delay)

**Best practice:**
- Use `wakeMode: "now"` for precise reminders and one-shot events
- Use `wakeMode: "next-heartbeat"` for daily routines where exact timing doesn't matter
- Short reminders (2-3 min) need `wakeMode: "now"` to be reliable

### Cron Payload Types
- `sessionTarget: "main"` + `kind: "systemEvent"` — Injects into main session, requires manual action
- `sessionTarget: "isolated"` + `kind: "agentTurn"` + `deliver: true` — Sends directly to Telegram automatically

---

## Coding Workflow

### Subagents for Coding Tasks (Critical!)

**Never run coding work on main session** — it causes freezes and blocks responsiveness.

**Use `sessions_spawn` for coding tasks:**
- Spawns isolated subagent session
- Keeps main session free for communication
- **ALWAYS instruct subagent to use `gemini` CLI as the primary coding tool**
- Background mode for long-running tasks
- Ping user when done via `message` tool

**Pattern:**
```
sessions_spawn task="Your coding task here" label:"brief-name" cleanup:"keep"
```

**For Gemini CLI:**
- Use `exec` for simple one-shot commands: `gemini "Write a Python script that..."`
- Use `workdir` to focus agent on specific project
- **Instruct subagent to use `gemini` for all coding work**

**Lesson learned (04 Feb 2026):**
- Main session freezes when running coding agents directly
- Subagents prevent blocking and keep things responsive
- Always ping user when subagent completes

**Updated (06 Feb 2026):**
- Use `gemini` CLI as the only coding tool for subagents
- Do NOT use Codex CLI or Claude Code (deprecated)

---

## Pilk Projects

### Pilk-Option-Chain
- Location: `~/Projects/Pilk-Option-Chain`
- Main script: `lotto_scanner.py` — Lotto scanner for daily options analysis
- Branch: `delta-n`
- Uses:
  - Deribit API for GEX zones (gamma walls with OI)
  - Binance API for G/T ratio + Whalley-Wilmott bands
  - Cross-references Binance plays near GEX zones (squeeze spots)

### pilk-scanner
- Location: `~/Projects/pilk-scanner`
- Purpose: Statistical arbitrage scanner for crypto futures
- Main script: `scan.py` — Finds mean-reverting pair trades
- Branch: `main`
- Features:
  - Cointegration filtering & dynamic beta estimation
  - Multiple algorithms: pilk-original (GARCH/Copula), pilk-lite (EWMA/ECDF), pilk-active (Hurst + cost filters)
  - Multi-anchor scanning across top volume assets
  - Paper trading support
  - WebUI dashboard (Next.js, Windows 95 style)
  - Benchmark/backtesting engine

### Pilk-Flights (PAUSED)
- Location: `~/Projects/Pilk-Flights`
- Status: PAUSED — free APIs not working
- Purpose: CLI tool for BKK → TYO flight search (7-day round trips)
- Features:
  - Typer CLI framework
  - Rich table display with statistics
  - Dual-mode operation: Scraping + API
- Issues:
  - Google Flights/Kayak scraping timeouts and selector problems
  - Kiwi/Tequila API requires paid activation (401 Unauthorized)
  - Skyscanner API complex with OIDC tokens
  - Free flight search APIs mostly discontinued
- Lesson (04 Feb 2026): Research APIs before building — assume free tier limitations

### Pilk-OCV
- Location: `~/Projects/Pilk-OCV`
- Purpose: Options Chain Visualizer for BTC/ETH
- Main script: `visualizer.py` — Visualizes options chains with heat maps, GEX zones, IV smiles
- Features:
  - Open interest heat map with color-coded intensity
  - Volume and IV scatter overlays
  - GEX zone annotations (gamma walls)
  - IV smile plotter (calls vs puts)
  - Export to PNG/SVG (images) and CSV/JSON (data)
  - Typer CLI framework with rich terminal output
- Lesson (04 Feb 2026): Should have used Codex CLI and Claude Code for this complex project — direct coding worked but CLI tools better for multi-component visualization tools

---

## Subagent Coding Tools (Updated 06 Feb 2026)

**CRITICAL:** Use only **Gemini CLI** for coding subagents. Do NOT use Claude CLI or Codex CLI.

### ✅ Use Gemini CLI (`gemini`) when:
- **PREFERRED: Always use `gemini` CLI as the primary coding tool** (per Kaname directive)
- Complex projects with multiple components
- Need external API knowledge or best practices
- Trading tools, visualizations, algorithms
- Projects requiring extensive debugging/iteration
- More than 2-3 files
- Involves external APIs (Deribit, Binance, etc.)
- Requires data visualization or plotting
- Needs optimization or best practices

### ⚡ Write Code Directly when:
- Simple utilities (hello world, basic scripts)
- Single-file tools
- Quick prototyping
- Less than 30-60 minutes of work
- Proof-of-concept projects

### Complex Project Criteria:
- Trading logic or complex calculations
- Data visualization (plots, heat maps, charts)
- Multiple interconnected components
- Requires external API integration
- Needs extensive testing/debugging

### Rule Applied:
- **Pilk-OCV:** Should've used Gemini CLI (visualization, Deribit API, plotting) — lesson learned
- **Hello World:** Direct coding correct (simple single-file utility)
- **Decision:** I'll make the call based on complexity at task creation time

### Lesson Learned (06 Feb 2026):
- Claude CLI and Codex CLI are deprecated for subagent use
- Gemini CLI is the approved and preferred tool
- Always instruct subagents to use `gemini` for coding tasks
