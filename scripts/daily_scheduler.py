#!/usr/bin/env python3
import os, sys, json, csv, time, random, subprocess
from pathlib import Path
from datetime import datetime, timedelta

ROOT = Path(__file__).resolve().parents[1]
STATE_DIR = ROOT / ".state"
STATE_DIR.mkdir(parents=True, exist_ok=True)
STATE_PATH = STATE_DIR / "daily_state.json"

def load_json(path, default):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return default

def save_json(path, obj):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(obj, indent=2), encoding="utf-8")

def load_config(cfg_path: Path):
    cfg = load_json(cfg_path, {})
    cfg.setdefault("daily_runs", 20)
    cfg.setdefault("window", {"start": "09:00", "end": "23:00", "jitter_seconds": 300})
    cfg.setdefault("packs_dir", "packs")
    cfg.setdefault("content_dir", "content")
    cfg.setdefault("manifest_path", "manifests/packs_manifest.csv")
    cfg.setdefault("run_pipeline_path", "run_pipeline.py")
    cfg.setdefault("python_path", "")
    cfg.setdefault("auto_repair_cta", True)
    cfg.setdefault("fallback_cta_default", "CTA_PRIMARY: Check out this product")
    cfg.setdefault("allow_repeat_packs_per_day", False)
    cfg.setdefault("max_retries_per_pack", 1)
    cfg.setdefault("log_dir", "logs")
    cfg.setdefault("log_prefix", "scheduler")
    cfg.setdefault("min_gap_seconds", 60)
    cfg.setdefault("tts_voice", "Samantha")
    return cfg

def parse_hhmm(today: datetime, hhmm: str) -> datetime:
    hh, mm = hhmm.split(":")
    return today.replace(hour=int(hh), minute=int(mm), second=0, microsecond=0)

def clamp(dt, start, end):
    return max(start, min(dt, end))

def build_daily_schedule(today: datetime, start_hhmm: str, end_hhmm: str, n: int, jitter_s: int):
    start = parse_hhmm(today, start_hhmm)
    end = parse_hhmm(today, end_hhmm)
    if end <= start:
        end = end + timedelta(days=1)
    total = (end - start).total_seconds()
    if n <= 0:
        return []
    step = total / n
    slots = []
    rnd = random.Random()
    rnd.seed(int(start.timestamp()) // 86400)
    for i in range(n):
        base = start + timedelta(seconds=i * step + step / 2.0)
        jitter = rnd.uniform(-jitter_s, jitter_s) if jitter_s > 0 else 0
        t = base + timedelta(seconds=jitter)
        slots.append(clamp(t, start, end))
    slots.sort()
    return slots

def load_manifest(manifest_path: Path):
    if not manifest_path.exists():
        return []
    packs = []
    with manifest_path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("enabled", "1") in ("1", "true", "True", "yes", "YES"):
                packs.append(row["pack_id"])
    return packs

def next_pack(packs, state, allow_repeat):
    used = set(state.get("used_today", []))
    idx = state.get("round_robin_idx", 0)
    if not packs:
        return None
    for _ in range(len(packs)):
        p = packs[idx % len(packs)]
        idx += 1
        if allow_repeat or p not in used:
            state["round_robin_idx"] = idx
            used.add(p)
            state["used_today"] = list(used)
            return p
    return None

def ensure_logs(cfg):
    log_dir = ROOT / cfg["log_dir"]
    log_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    return log_dir / f"{cfg['log_prefix']}_{today}.log"

def log_line(path: Path, text: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with path.open("a", encoding="utf-8") as f:
        f.write(f"[{ts}] {text}\n")

def run_once(cfg, pack_id, log_path):
    py = cfg["python_path"] or sys.executable
    env = os.environ.copy()
    env["PACKS_DIR"] = cfg["packs_dir"]
    env["CONTENT_DIR"] = cfg["content_dir"]
    env["AUTO_REPAIR_CTA"] = "1" if cfg["auto_repair_cta"] else "0"
    env["FALLBACK_CTA"] = cfg["fallback_cta_default"]
    env["TTS_VOICE"] = cfg.get("tts_voice", "Samantha")
    cmd = [py, cfg["run_pipeline_path"], pack_id]
    start = datetime.now()
    log_line(log_path, f"START pack={pack_id} cmd={' '.join(cmd)}")
    rc = subprocess.call(cmd, cwd=str(ROOT), env=env)
    dur = (datetime.now() - start).total_seconds()
    status = "OK" if rc == 0 else f"FAIL(rc={rc})"
    log_line(log_path, f"END   pack={pack_id} status={status} duration_s={int(dur)}")
    return rc

def sleep_until(target_dt, min_gap_s):
    now = datetime.now()
    if target_dt <= now:
        return
    gap = (target_dt - now).total_seconds()
    while gap > 0:
        s = min(gap, max(5, min_gap_s))
        time.sleep(s)
        gap -= s

def rollover_if_needed(state, today):
    today_key = today.strftime("%Y-%m-%d")
    if state.get("today_key") != today_key:
        state.clear()
        state["today_key"] = today_key
        state["used_today"] = []
        state["round_robin_idx"] = 0
        state["schedule"] = []
        save_json(STATE_PATH, state)

def main():
    cfg_path = ROOT / "config" / "scheduler.config.json"
    if len(sys.argv) > 1 and sys.argv[1] in ("-c", "--config"):
        cfg_path = Path(sys.argv[2]).resolve()
    cfg = load_config(cfg_path)
    log_path = ensure_logs(cfg)
    while True:
        today = datetime.now()
        state = load_json(STATE_PATH, {})
        rollover_if_needed(state, today)
        if not state.get("schedule"):
            slots = build_daily_schedule(
                today,
                cfg["window"]["start"],
                cfg["window"]["end"],
                cfg["daily_runs"],
                cfg["window"].get("jitter_seconds", 0),
            )
            state["schedule"] = [dt.isoformat() for dt in slots]
            state["next_slot_idx"] = 0
            save_json(STATE_PATH, state)
            log_line(log_path, f"SCHEDULE {len(slots)} slots from {cfg['window']['start']} to {cfg['window']['end']}")
        slots = [datetime.fromisoformat(s) for s in state["schedule"]]
        i = state.get("next_slot_idx", 0)
        if i >= len(slots):
            tomorrow = today + timedelta(days=1)
            next_start = parse_hhmm(tomorrow, cfg["window"]["start"])
            log_line(log_path, "DAY COMPLETE sleeping until next window.")
            sleep_until(next_start, cfg["min_gap_seconds"])
            continue
        target = slots[i]
        sleep_until(target, cfg["min_gap_seconds"])
        packs = load_manifest(ROOT / cfg["manifest_path"])
        if not packs:
            log_line(log_path, "WARN no enabled packs in manifest; skipping slot.")
            state["next_slot_idx"] = i + 1
            save_json(STATE_PATH, state)
            continue
        pack = next_pack(packs, state, cfg["allow_repeat_packs_per_day"])
        if pack is None:
            log_line(log_path, "INFO no eligible packs this slot; skipping.")
            state["next_slot_idx"] = i + 1
            save_json(STATE_PATH, state)
            continue
        rc = run_once(cfg, pack, log_path)
        if rc != 0 and cfg["max_retries_per_pack"] > 0:
            log_line(log_path, f"RETRY scheduling for pack={pack}")
            rc = run_once(cfg, pack, log_path)
        state["next_slot_idx"] = i + 1
        save_json(STATE_PATH, state)
        time.sleep(cfg["min_gap_seconds"])

if __name__ == "__main__":
    main()
