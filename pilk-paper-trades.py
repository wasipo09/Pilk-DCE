#!/usr/bin/env python3
"""Pilk Paper Trading Tracker for Options"""

import json
import sys
from datetime import datetime
from pathlib import Path

TRADES_FILE = Path.home() / ".openclaw/workspace/pilk-paper-trades.json"


def load_trades():
    if not TRADES_FILE.exists():
        return {"version": "1.0", "trades": [], "summary": {
            "total_trades": 0, "winning_trades": 0, "losing_trades": 0,
            "win_rate": 0.0, "total_profit_loss": 0.0, "avg_profit_loss": 0.0,
            "max_profit": 0.0, "max_loss": 0.0, "current_positions": []
        }}
    
    with open(TRADES_FILE, 'r') as f:
        return json.load(f)


def save_trades(data):
    with open(TRADES_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def add_trade(contract_type, strike, expiry, entry_price, size, edge, ml_score, rationale=""):
    """Add a new paper trade"""
    data = load_trades()
    
    trade_id = len(data["trades"]) + 1
    trade = {
        "id": trade_id,
        "contract": f"BTC-{expiry.replace('-', '')}-{strike}-{'C' if contract_type.upper() == 'CALL' else 'P'}",
        "contract_type": contract_type.upper(),
        "strike": strike,
        "expiry": expiry,
        "entry_price": entry_price,
        "exit_price": None,
        "size": size,
        "edge": edge,
        "ml_score": ml_score,
        "entry_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "exit_time": None,
        "profit_loss": None,
        "status": "OPEN",
        "rationale": rationale,
        "hedge_history": []
    }
    
    data["trades"].append(trade)
    data["summary"]["total_trades"] += 1
    data["summary"]["current_positions"].append(trade_id)
    
    save_trades(data)
    print(f"✅ Paper trade #{trade_id} opened: {trade['contract']}")
    return trade_id


def close_trade(trade_id, exit_price):
    """Close a paper trade and calculate P&L"""
    data = load_trades()
    
    trade = next((t for t in data["trades"] if t["id"] == trade_id), None)
    if not trade:
        print(f"❌ Trade #{trade_id} not found")
        return
    
    if trade["status"] == "CLOSED":
        print(f"⚠️  Trade #{trade_id} already closed")
        return
    
    # Calculate P&L (simplified: (exit - entry) * size)
    trade["exit_price"] = exit_price
    trade["exit_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    trade["status"] = "CLOSED"
    
    contract_type = trade["contract_type"]
    if contract_type == "CALL":
        trade["profit_loss"] = (exit_price - trade["entry_price"]) * trade["size"]
    else:  # PUT
        trade["profit_loss"] = (trade["entry_price"] - exit_price) * trade["size"]
    
    # Update summary
    summary = data["summary"]
    summary["current_positions"].remove(trade_id)
    summary["total_profit_loss"] += trade["profit_loss"]
    
    if trade["profit_loss"] > 0:
        summary["winning_trades"] += 1
        summary["max_profit"] = max(summary["max_profit"], trade["profit_loss"])
    elif trade["profit_loss"] < 0:
        summary["losing_trades"] += 1
        summary["max_loss"] = min(summary["max_loss"], trade["profit_loss"])
    
    summary["win_rate"] = (summary["winning_trades"] / summary["total_trades"]) * 100
    summary["avg_profit_loss"] = summary["total_profit_loss"] / summary["total_trades"]
    
    save_trades(data)
    
    result = "WIN" if trade["profit_loss"] > 0 else "LOSS"
    print(f"✅ Paper trade #{trade_id} closed: {trade['contract']} | P&L: ${trade['profit_loss']:.2f} ({result})")
    return trade["profit_loss"]


def list_trades(show_all=False):
    """List all paper trades"""
    data = load_trades()
    print(f"\n📊 Pilk Paper Trading — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 70)
    
    if show_all:
        for trade in data["trades"]:
            status_emoji = "🟢" if trade["status"] == "OPEN" else "🔴"
            print(f"\n{status_emoji} Trade #{trade['id']}: {trade['contract']}")
            print(f"   Type: {trade['contract_type']} | Strike: ${trade['strike']:,.0f}")
            print(f"   Entry: ${trade['entry_price']:.2f} | Exit: ${trade['exit_price'] if trade['exit_price'] else 'OPEN'}")
            print(f"   Size: {trade['size']} BTC | Edge: {trade['edge']:.2%} | ML: {trade['ml_score']:.2f}")
            print(f"   Status: {trade['status']} | P&L: ${trade['profit_loss'] if trade['profit_loss'] else '--'}")
            print(f"   Entry: {trade['entry_time']}")
    else:
        open_trades = [t for t in data["trades"] if t["status"] == "OPEN"]
        if not open_trades:
            print("\n✅ No open paper trades")
        else:
            print(f"\n🟢 Open Paper Trades: {len(open_trades)}")
            for trade in open_trades:
                print(f"\n  #{trade['id']}: {trade['contract']}")
                print(f"  Entry: ${trade['entry_price']:.2f} | Edge: {trade['edge']:.1f}% | ML: {trade['ml_score']:.2f}")
                print(f"  Size: {trade['size']} BTC | Entry: {trade['entry_time']}")
    
    # Summary
    print(f"\n{'=' * 70}")
    s = data["summary"]
    print(f"📈 Total Trades: {s['total_trades']} | Win Rate: {s['win_rate']:.1f}%")
    print(f"💰 Total P&L: ${s['total_profit_loss']:.2f} | Avg: ${s['avg_profit_loss']:.2f}/trade")
    print(f"🏆 Max Win: ${s['max_profit']:.2f} | Max Loss: ${s['max_loss']:.2f}")
    print(f"🟢 Current Positions: {len(s['current_positions'])}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        list_trades()
        sys.exit(0)
    
    cmd = sys.argv[1].lower()
    
    if cmd == "open":
        if len(sys.argv) < 8:
            print("Usage: open CALL/PUT STRIKE EXPIRY ENTRY_SIZE EDGE ML_SCORE [RATIONALE]")
            print("Example: open CALL 71000 2026-02-16 5 0.1 64.35 0.40 'Bullish momentum'")
            sys.exit(1)
        contract_type = sys.argv[2]
        strike = float(sys.argv[3])
        expiry = sys.argv[4]
        entry_price = float(sys.argv[5])
        size = float(sys.argv[6])
        edge = float(sys.argv[7])
        ml_score = float(sys.argv[8])
        rationale = sys.argv[9] if len(sys.argv) > 9 else ""
        add_trade(contract_type, strike, expiry, entry_price, size, edge, ml_score, rationale)
    
    elif cmd == "close":
        if len(sys.argv) < 4:
            print("Usage: close TRADE_ID EXIT_PRICE")
            print("Example: close 1 7.50")
            sys.exit(1)
        trade_id = int(sys.argv[2])
        exit_price = float(sys.argv[3])
        close_trade(trade_id, exit_price)
    
    elif cmd == "list":
        list_trades(show_all="--all" in sys.argv)
    
    else:
        print(f"Unknown command: {cmd}")
        print("Commands: open, close, list [--all]")
