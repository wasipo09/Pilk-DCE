# MEMORY - Long-term Knowledge

## Lotto Routine (Cron every 2 hours)

### Sacred Duty - Every Win = Mac Studio Progress

**Procedure:**
1. Read crypto news using `web_search` (CoinDesk, Cointelegraph, Bitcoin Magazine, Decrypt, The Block sources via search)
2. Run enhanced scalp algo: `cd ~/Projects/Pilk-Option-Chain && python -m pilk_options.main --scalp`
   - Uses **ML-framework scoring** with institutional-grade methodology
   - Deribit + Binance integrated data
3. Get enhanced metrics and algo analysis
4. My take based on news + options data combined
5. Best play OR say "not to play"

**Note:** Lotto scans run every 2 hours via cron job. **Default position size: 0.1 contracts** (not 0.05).

**Scripts:**
- `web_search` - fetches and summarizes crypto news
- **Enhanced scalp algo** (`--scalp` flag) - ML-framework scoring system on main branch

**Note:** Lotto scans are now done **manually on request** or by running `--scalp` directly. No longer rely on automated cron jobs.

**No sentiment scoring** — just me analyzing the news naturally and combining with data.

### Key Metrics (Enhanced Scalp Algo)
- **Vol-Spread Edge** (Sinclair 2013): Daily expected gamma P&L from RV-IV spread
- **Liquidity Score** (Kyle 1985): Bid-ask spread, delta-hedging slippage, OI/volume
- **VRP Multiplier** (Carr & Wu 2009): Variance Risk Premium ratio clipped [0.5, 2.0]
- **Kurtosis Penalty** (Bates 1996): Discounts heavy-tailed return distributions
- **Stochastic Vol Adjustment** (Heston 1993): Signal-to-noise ratio for gamma vs vega
- **Half-Kelly Sizing** (Thorp 2006): Optimal position sizing as % of capital

### Best Play Criteria (Updated Feb 7, 2026)
- **Only pick lotto play if there are HIGH POSITIVE SCORES**
- High composite Score (Edge * Liquidity * VRP * Kurtosis * StochVol)
- Positive Kelly% (means trade has positive edge)
- Reasonable spread (low liquidity penalty)
- Aligned with news sentiment
- Not chasing momentum against the flow
- **If all scores are 0.00 or negative → NOT TO PLAY**
- **Default position size: 0.1 contracts** (not 0.05)

---

## Gamma Scalping - "Small Play" Guide (from Pilk-Option-Chain TUTORIAL.md)

**Concept:** Buy options (long volatility), hedge with short futures to be delta-neutral. Profit from Bitcoin's actual volatility exceeding what options are pricing in.

**The Workflow:**
1. **Entry (T=0)**: Buy 0.05 BTC options → Calculate hedge (0.05 × delta) → Open short position → Delta-neutral
2. **The Grind (T=4h)**: Check delta deviation every 4 hours vs "Band" parameter → Trade to maintain delta neutrality
3. **Exit**: IV spikes or market flat for 48h → Close everything

**Key Points:**
- **Rent (positive) = Profit potential > Time Decay (theta)** - Good to buy
- **Band** = "Action Trigger" - When deviation exceeds band, trade to re-hedge
- **Size 0.05 BTC** = Fixed small position, not scalable
- **Delta-neutral hedging** = Sell 0.05 × Delta of futures to offset option delta

**Example Scenario:**
- T=0: Buy 0.05 Call @ $72K, Short 0.025 BTC (hedge)
- T=4h: BTC pumps to $71K, delta deviation 0.10 > Band 0.035 → Increase short by 0.005 BTC
- T=12h: BTC dumps back, IV spikes → Sell everything, close short → Profit $5

**Note:** This is institutional-grade gamma scalping with theoretical backing, not gambling. Use ML-framework (--scalp) for scoring.

---

## Current Options Position

**FLAT** - All positions closed (sold on 2026-02-06 21:50 ICT)

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
- **Use `wakeMode: "now"` for all cron jobs that need to fire on time**

**Lesson learned (07 Feb 2026):**
- If cron jobs stop firing, delete and recreate them with `wakeMode: "now"`
- The 5-min test ping proved `wakeMode: "now"` works correctly
- Always verify cron jobs fire after creation

---

## Task Tracking with Pilk-Tasks

**Tool:** Pilk-Tasks CLI v2.0 (installed in workspace)

### How Satsuki Uses Pilk-Tasks (My Internal Workflow)

**Daily Task Management:**
1. **Morning Check:** Run `pilk-tasks list` to see current queue
2. **Add New Tasks:** Use `pilk-tasks add -t "Task" -d "Description" -p high -c work --tags important`
3. **Update Progress:** `pilk-tasks update --id X --status in-progress`
4. **Quick Complete:** `pilk-tasks done X` for one-step completion
5. **Search:** `pilk-tasks search "query"` to find tasks
6. **Analytics:** Run `pilk-tasks dashboard` for econometric insights
7. **JSON Export:** Any command can use `--json` flag for programmatic access

**Advanced Features:**
- **Subtasks:** `pilk-tasks add -t "Subtask" --parent 5`
- **Time Tracking:** `pilk-tasks start X` and `pilk-tasks stop X`
- **Batch Ops:** `pilk-tasks bulk --complete --ids 1,2,3`
- **Dependencies:** `pilk-tasks add -t "Blocked task" --depends-on 5`
- **Recurring:** `pilk-tasks add -t "Daily sync" --recurrence daily`
- **Notes:** `pilk-tasks notes X` with markdown support
- **Templates:** `pilk-tasks template bug/feature/meeting`

**Natural Language Date Parsing:**
- `pilk-tasks add -t "Report due" --due "next monday"`
- `pilk-tasks add -t "Meeting" --due "tomorrow"`
- `pilk-tasks add -t "Review" --due "in 3 days"`

**Heartbeat behavior:**
- Run `pilk-tasks list` to show current task queue
- Ask user if they'd like to add anything

**JSON Mode for Natural Language Reports:**
- `pilk-tasks dashboard --json` → Full econometric metrics
- `pilk-tasks list --json` → All tasks structured
- `pilk-tasks stats --json` → Statistics
- `pilk-tasks search "work" --json` → Search results
- Purpose: Easy NL report generation from structured data

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
- Do NOT use Codex CLI or Claude Code (these are deprecated)
- This directive is permanent — always use Gemini for coding via subagents

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
