# Phase One - Project Ideas

## 🎯 New Project Ideas (Brainstormed 04 Feb 2026)

### 1. **Pilk-Portfolio** — Unified Position Tracker
- Track all positions across exchanges (Binance, Bybit, Deribit, etc.)
- Real-time P&L, exposure breakdown, risk metrics
- Telegram summary when positions move >5%
- Archive historical trades for strategy review

### 2. **Pilk-Flow** — Order Flow Analytics
- Monitor large unusual orders (whale alerts, block trades)
- Track CVD (Cumulative Volume Delta) and order book imbalance
- Detect aggressive buying/selling pressure before price moves
- Alert when flow diverges from price (reversal signal)

### 3. **Pilk-Basis** — Funding + Basis Monitor
- Track perpetual funding rates across exchanges
- Spot-futures arbitrage opportunities
- Calendar spread monitor (quarterly vs perpetual)
- Alert when funding deviates >2 std from mean

### 4. **Pilk-Backtest** — Strategy Framework
- Generic backtesting engine for any strategy
- Walk-forward analysis, parameter optimization
- Monte Carlo simulation for robustness testing
- Visual equity curves, drawdown charts, Sharpe metrics

### 5. **Pilk-Correlation** — Regime Detection
- Real-time correlation matrix across top 20 assets
- Regime classifier (risk-on, risk-off, chop, trend)
- Asset clustering for pair selection
- Alert when correlation structure breaks

### 6. **Pilk-Vol** — Vol Surface + Term Structure
- Track implied vol surface across strikes & expirations
- Term structure monitor (contango/backwardation)
- RV vs IV divergence alerts (volatility mispricing)
- Historical vol percentiles for "cheap" vs "rich" options

### 7. **Pilk-Execute** — Automated Signal Engine
- Unified signal aggregator from all Pilk tools
- Risk checks before execution (size, exposure, drawdown)
- Multi-exchange order routing (best price, slippage control)
- Paper trade → live trade migration path

### 8. **Pilk-Dashboard** — Web Frontend
- Single pane of glass for all Pilk tools
- Real-time charts, alerts, position tracking
- Mobile-friendly UI (Next.js + shadcn/ui)
- Dark mode, clean aesthetics (Pilk branding)

### 9. **Pilk-Sentiment** — Social Signals
- Twitter/X sentiment tracker (crypto influencers, accounts)
- Reddit/Telegram sentiment analysis
- Fear & Greed alternative index
- Contrarian signals when sentiment extremes

### 10. **Pilk-Ledger** — Trade Journal
- Smart trade journal with auto-tagging
- Screenshots, notes, P&L screenshots
- Strategy performance breakdown
- Weekly/monthly performance reports

---

## 🚀 Quick Wins (Low Effort, High Value)

1. **Pilk-Alerts** — Telegram alert aggregator (one bot for all Pilk tools)
2. **Pilk-Config** — Unified config manager for all projects
3. **Pilk-Docs** — Auto-generated API docs + strategy guides

---

## Building First: Pilk-Portfolio (Binance Only)

**Scope for Phase 1:**
- Binance futures positions tracking only
- Real-time P&L
- Telegram alerts for significant moves
- Historical trade logging
