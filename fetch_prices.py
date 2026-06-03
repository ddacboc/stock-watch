#!/usr/bin/env python3
"""
3시간마다 GitHub Actions가 실행하는 가격 수집 스크립트.
- config.json 에서 fetch:true 인 티커만 Finnhub 무료 API로 현재가를 받는다.
- data.json 에 종목별 history([timestamp, price])를 누적한다. (과거데이터 API 불필요)
- 표준 라이브러리만 사용 → pip 설치 없이 Actions에서 바로 실행.

환경변수 FINNHUB_KEY 에 무료 API 키가 들어 있어야 한다 (GitHub Secret).
"""
import json, os, sys, time, urllib.request, urllib.parse
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(HERE, "config.json")
DATA = os.path.join(HERE, "data.json")
API = "https://finnhub.io/api/v1/quote"

def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default

def get_quote(symbol, token):
    qs = urllib.parse.urlencode({"symbol": symbol, "token": token})
    req = urllib.request.Request(API + "?" + qs, headers={"User-Agent": "watchlist/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        d = json.load(r)
    price = d.get("c")  # current price
    if price is None or price == 0:
        return None
    return round(float(price), 4)

def main():
    token = os.environ.get("FINNHUB_KEY", "").strip()
    if not token:
        print("ERROR: FINNHUB_KEY 환경변수가 없습니다.", file=sys.stderr)
        sys.exit(1)

    cfg = load_json(CONFIG, {"themes": [], "historyCap": 720})
    cap = int(cfg.get("historyCap", 720))
    data = load_json(DATA, {"updated": None, "prices": {}})
    prices = data.get("prices", {})

    # config의 모든 fetch:true 티커를 중복 없이 모음
    tickers = []
    for th in cfg.get("themes", []):
        for row in th.get("rows", []):
            if row.get("fetch") and row["t"] not in tickers:
                tickers.append(row["t"])

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    ok, fail = 0, 0
    for t in tickers:
        entry = prices.get(t, {"price": None, "history": [], "status": "n/a"})
        try:
            p = get_quote(t, token)
            if p is None:
                entry["status"] = "n/a"
                fail += 1
            else:
                entry["price"] = p
                entry["status"] = "ok"
                hist = entry.get("history", [])
                hist.append([now, p])
                entry["history"] = hist[-cap:]   # 최근 N개만 유지
                ok += 1
        except Exception as e:
            entry["status"] = "error"
            print(f"  {t}: {e}", file=sys.stderr)
            fail += 1
        prices[t] = entry
        time.sleep(1.1)  # 무료 티어 호출 제한 여유

    data["prices"] = prices
    data["updated"] = now
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print(f"done: {ok} ok, {fail} failed, updated {now}")

if __name__ == "__main__":
    main()
