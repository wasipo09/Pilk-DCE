from __future__ import annotations

import csv
import json
import shutil
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from zoneinfo import ZoneInfo

app = typer.Typer(help="Pilk Trade Journal CLI for logging, listing, searching, and summarizing trades.")

HOME = Path.home()
JOURNAL_DIR = HOME / "trade_journal"
TRADES_PATH = JOURNAL_DIR / "trades.json"
SCREENSHOT_ROOT = JOURNAL_DIR / "screenshots"
TIMEZONE = ZoneInfo("Asia/Bangkok")
console = Console()


def ensure_journal_dirs() -> None:
    JOURNAL_DIR.mkdir(parents=True, exist_ok=True)
    SCREENSHOT_ROOT.mkdir(parents=True, exist_ok=True)


def load_trades() -> list[dict]:
    ensure_journal_dirs()
    if not TRADES_PATH.exists():
        return []
    try:
        with TRADES_PATH.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
            if isinstance(data, list):
                return data
    except json.JSONDecodeError:
        console.print("[yellow]Warning:[/] Corrupted trades file. Starting fresh list.")
    return []


def save_trades(trades: list[dict]) -> None:
    ensure_journal_dirs()
    with TRADES_PATH.open("w", encoding="utf-8") as handle:
        json.dump(trades, handle, indent=2, ensure_ascii=False)


def format_currency(value: float) -> str:
    sign = "+" if value >= 0 else "-"
    return f"{sign}${abs(value):,.2f}"


def format_percent(value: float) -> str:
    return f"{value:+.2f}%"


def to_local(dt_str: str) -> str:
    try:
        dt = datetime.fromisoformat(dt_str)
        return dt.astimezone(TIMEZONE).strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return dt_str


def store_screenshot(source: Path | None, trade_time: datetime) -> str | None:
    ensure_journal_dirs()
    if not source:
        return None
    source = source.expanduser()
    target_dir = SCREENSHOT_ROOT / trade_time.strftime("%Y-%m-%d")
    target_dir.mkdir(parents=True, exist_ok=True)
    if source.exists():
        destination = target_dir / f"{trade_time.strftime('%H%M%S')}_{source.name}"
        shutil.copy2(source, destination)
        return str(destination)
    console.print(
        f"[yellow]Warning:[/] Screenshot {source} not found. Saving provided path reference instead."
    )
    return str(source)


def build_record(
    ticker: str,
    trade_type: str,
    entry_price: float,
    exit_price: float,
    position_size: float,
    notes: str,
    screenshot: str | None,
    timestamp: datetime,
    pnl: float,
    pnl_pct: float,
) -> dict:
    return {
        "timestamp": timestamp.isoformat(),
        "ticker": ticker.upper(),
        "trade_type": trade_type.upper(),
        "entry_price": entry_price,
        "exit_price": exit_price,
        "position_size": position_size,
        "pnl": pnl,
        "pnl_pct": pnl_pct,
        "notes": notes,
        "screenshot_path": screenshot,
    }


def apply_filters(
    trades: Iterable[dict],
    ticker: str | None = None,
    trade_type: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> list[dict]:
    results = []
    for trade in trades:
        if ticker and trade.get("ticker", "").lower() != ticker.lower():
            continue
        if trade_type and trade.get("trade_type", "").lower() != trade_type.lower():
            continue
        trade_time = None
        timestamp = trade.get("timestamp")
        if timestamp:
            try:
                trade_time = datetime.fromisoformat(timestamp)
            except ValueError:
                pass
        if start_date and trade_time and trade_time < start_date:
            continue
        if end_date and trade_time and trade_time > end_date:
            continue
        results.append(trade)
    return results


def export_to_csv(trades: list[dict], path: Path) -> None:
    path = path.expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "timestamp",
        "ticker",
        "trade_type",
        "entry_price",
        "exit_price",
        "position_size",
        "pnl",
        "pnl_pct",
        "notes",
        "screenshot_path",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for trade in trades:
            writer.writerow({key: trade.get(key, "") for key in fieldnames})
    console.print(f"[green]Exported {len(trades)} trades to {path} (CSV).[/]")


def export_to_json(trades: list[dict], path: Path) -> None:
    path = path.expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(trades, handle, indent=2, ensure_ascii=False)
    console.print(f"[green]Exported {len(trades)} trades to {path} (JSON).[/]")


def print_table(trades: list[dict], title: str = "Trades") -> None:
    if not trades:
        console.print("[yellow]No trades to show.[/]")
        return
    table = Table(title=f"{title} ({len(trades)})", show_lines=False)
    table.add_column("Date", style="cyan", no_wrap=True)
    table.add_column("Ticker", style="bold magenta")
    table.add_column("Type", style="bold")
    table.add_column("Entry", justify="right")
    table.add_column("Exit", justify="right")
    table.add_column("Size", justify="right")
    table.add_column("PnL", justify="right")
    table.add_column("PnL %", justify="right")
    table.add_column("Notes", style="dim")

    for trade in trades:
        table.add_row(
            to_local(trade.get("timestamp", "")),
            trade.get("ticker", ""),
            trade.get("trade_type", ""),
            f"${trade.get('entry_price', 0):,.2f}",
            f"${trade.get('exit_price', 0):,.2f}",
            f"{trade.get('position_size', 0):,.4f}",
            format_currency(trade.get("pnl", 0.0)),
            format_percent(trade.get("pnl_pct", 0.0)),
            trade.get("notes", ""),
        )
    console.print(table)


@app.command()
def log(
    ticker: str = typer.Option(..., prompt="Ticker (e.g., BTC)", help="Ticker symbol"),
    trade_type: str = typer.Option(
        ..., prompt="Trade type (long/short)", help="Choose long or short"
    ),
    entry_price: float = typer.Option(..., prompt="Entry price", help="Entry price"),
    exit_price: float = typer.Option(..., prompt="Exit price", help="Exit price"),
    position_size: float = typer.Option(..., prompt="Position size", help="Position size"),
    notes: str = typer.Option("", "-n", "--notes", help="Notes about setup/lessons"),
    screenshot: Path | None = typer.Option(
        None,
        "-s",
        "--screenshot",
        exists=False,
        help="Optional screenshot to store/copy",
    ),
) -> None:
    now = datetime.now(tz=TIMEZONE)
    normalized_type = trade_type.lower()
    if normalized_type not in {"long", "short"}:
        raise typer.BadParameter("Trade type must be 'long' or 'short'.")
    sign = 1 if normalized_type == "long" else -1
    price_diff = exit_price - entry_price
    pnl = sign * price_diff * position_size
    capital = abs(entry_price) * position_size if entry_price else 0
    pnl_pct = (pnl / capital) * 100 if capital else 0
    screenshot_path = store_screenshot(screenshot, now)
    record = build_record(
        ticker=ticker,
        trade_type=normalized_type,
        entry_price=entry_price,
        exit_price=exit_price,
        position_size=position_size,
        notes=notes,
        screenshot=screenshot_path,
        timestamp=now,
        pnl=pnl,
        pnl_pct=pnl_pct,
    )
    trades = load_trades()
    trades.append(record)
    save_trades(trades)

    console.print("\n📝 [bold]TRADE LOGGED[/bold]\n")
    console.print(f"Ticker: {record['ticker']}")
    console.print(f"Type: {record['trade_type']}")
    console.print(f"Entry: ${record['entry_price']:,.2f}")
    console.print(f"Exit: ${record['exit_price']:,.2f}")
    console.print(f"PnL: {format_currency(record['pnl'])} ({format_percent(record['pnl_pct'])})")
    console.print(f"Notes: {notes or '—'}")
    console.print(f"Screenshot: {screenshot_path or '—'}")


@app.command(name="list")
def list_trades(
    ticker: str | None = typer.Option(None, "-t", "--ticker", help="Filter by ticker"),
    trade_type: str | None = typer.Option(None, "-y", "--type", help="Filter by trade type"),
    start_date: str | None = typer.Option(
        None, "-s", "--start-date", help="Start date (YYYY-MM-DD)"
    ),
    end_date: str | None = typer.Option(None, "-e", "--end-date", help="End date (YYYY-MM-DD)"),
    export_csv: Path | None = typer.Option(None, "--export-csv", help="Export filtered list to CSV"),
    export_json: Path | None = typer.Option(None, "--export-json", help="Export filtered list to JSON"),
) -> None:
    trades = load_trades()
    if not trades:
        console.print("[yellow]No trades logged yet.[/]")
        raise typer.Exit()
    start_dt = datetime.fromisoformat(start_date) if start_date else None
    end_dt = (
        datetime.fromisoformat(end_date) + timedelta(days=1) if end_date else None
    )
    filtered = apply_filters(trades, ticker, trade_type, start_dt, end_dt)
    print_table(filtered, title="Trade Log")
    total = sum(trade.get("pnl", 0.0) for trade in filtered)
    console.print(f"[bold]Total PnL:[/] {format_currency(total)}")
    if export_csv:
        export_to_csv(filtered, export_csv)
    if export_json:
        export_to_json(filtered, export_json)


@app.command()
def search(
    query: str = typer.Option(..., "-q", "--query", help="Keyword to search notes"),
    winners: bool = typer.Option(False, "--winners", help="Show only winning trades"),
    losers: bool = typer.Option(False, "--losers", help="Show only losing trades"),
    min_pnl: float | None = typer.Option(None, "--min-pnl", help="Minimum PnL"),
    max_pnl: float | None = typer.Option(None, "--max-pnl", help="Maximum PnL"),
) -> None:
    trades = load_trades()
    if not trades:
        console.print("[yellow]No trades logged yet.[/]")
        raise typer.Exit()
    normalized_query = query.lower()
    results = [trade for trade in trades if normalized_query in trade.get("notes", "").lower()]
    if winners and losers:
        typer.echo("Cannot filter for both winners and losers simultaneously.")
        raise typer.Exit(code=1)
    if winners:
        results = [trade for trade in results if trade.get("pnl", 0.0) > 0]
    if losers:
        results = [trade for trade in results if trade.get("pnl", 0.0) < 0]
    if min_pnl is not None:
        results = [trade for trade in results if trade.get("pnl", 0.0) >= min_pnl]
    if max_pnl is not None:
        results = [trade for trade in results if trade.get("pnl", 0.0) <= max_pnl]
    if not results:
        console.print("[yellow]No trades matched your search criteria.[/]")
        raise typer.Exit()
    print_table(results, title="Search Results")


@app.command()
def stats() -> None:
    trades = load_trades()
    if not trades:
        console.print("[yellow]No trades logged yet.[/]")
        raise typer.Exit()
    total_pnl = sum(trade.get("pnl", 0.0) for trade in trades)
    winners = [trade for trade in trades if trade.get("pnl", 0.0) > 0]
    losers = [trade for trade in trades if trade.get("pnl", 0.0) < 0]
    win_rate = len(winners) / len(trades) * 100 if trades else 0
    avg_win = sum(trade.get("pnl", 0.0) for trade in winners) / len(winners) if winners else 0
    avg_loss = sum(trade.get("pnl", 0.0) for trade in losers) / len(losers) if losers else 0

    panel_text = (
        f"Total PnL: [bold]{format_currency(total_pnl)}[/]\n"
        f"Win rate: [bold]{win_rate:.1f}%[/]\n"
        f"Average win: [bold]{format_currency(avg_win)}[/]\n"
        f"Average loss: [bold]{format_currency(avg_loss)}[/]"
    )
    console.print(Panel(panel_text, title="Overview", expand=False))

    breakdown: dict[str, dict[str, float | int]] = defaultdict(lambda: {"count": 0, "total_pnl": 0.0, "wins": 0})
    for trade in trades:
        ticker = trade.get("ticker", "UNKNOWN")
        bucket = breakdown[ticker]
        bucket["count"] += 1
        bucket["total_pnl"] += trade.get("pnl", 0.0)
        if trade.get("pnl", 0.0) > 0:
            bucket["wins"] += 1

    breakdown_table = Table(title="By Ticker")
    breakdown_table.add_column("Ticker")
    breakdown_table.add_column("Trades", justify="right")
    breakdown_table.add_column("Win rate", justify="right")
    breakdown_table.add_column("Total PnL", justify="right")
    breakdown_table.add_column("Avg PnL", justify="right")

    for ticker, data in sorted(breakdown.items()):
        count = data["count"]
        total = data["total_pnl"]
        wins = data["wins"]
        win_pct = wins / count * 100 if count else 0
        avg = total / count if count else 0
        breakdown_table.add_row(
            ticker,
            str(count),
            f"{win_pct:.1f}%",
            format_currency(total),
            format_currency(avg),
        )
    console.print(breakdown_table)


if __name__ == "__main__":
    app()
