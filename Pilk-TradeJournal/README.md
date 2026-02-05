# Pilk-TradeJournal

Trade Journal Helper CLI designed for quick logging, searching, and reviewing trades.

## Features

- `pilk-journal log` – log a trade with ticker, direction, prices, size, notes, and optional screenshot references.
- `pilk-journal list` – review trades with filters (ticker, type, date range) plus export to CSV/JSON.
- `pilk-journal search` – search notes for keywords and filter winners/losses.
- `pilk-journal stats` – summarize Total PnL, win rate, average win/loss, and breakdown by ticker.

## Storage

Trades are stored in `~/trade_journal/trades.json` and optional screenshots land under `~/trade_journal/screenshots/YYYY-MM-DD/`.

## Installation

```sh
python -m pip install -e .
```

## Quick example

```sh
pilk-journal log --ticker BTC --type long --entry 75000 --exit 76500 --size 0.1 --notes "Tested 73k support" --screenshot ~/tmp/btc.png
```
