# -*- coding: utf-8 -*-
"""备份记录管理：存储于 %APPDATA% 下 WWMI_MOD面板助手/history.json"""

import json
import os
import time

APP_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "WWMI_MOD面板助手")
HISTORY_FILE = os.path.join(APP_DIR, "history.json")
SETTINGS_FILE = os.path.join(APP_DIR, "settings.json")


def _ensure_dir():
    if not os.path.isdir(APP_DIR):
        os.makedirs(APP_DIR)


def _load():
    _ensure_dir()
    if not os.path.isfile(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []


def _save(records):
    _ensure_dir()
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def add_record(mod_path, mod_name, ini_path, bak_path, method, button_count, toggle_key, key_summary=""):
    rec = {
        "mod_path": mod_path,
        "mod_name": mod_name,
        "ini_path": ini_path,
        "bak_path": bak_path,
        "method": method,
        "button_count": button_count,
        "toggle_key": toggle_key,
        "key_summary": key_summary,
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "ts": time.time(),
    }
    records = _load()
    records = [r for r in records if r.get("mod_path") != mod_path]
    records.append(rec)
    _save(records)
    return rec


def get_records():
    return _load()


def remove_record(mod_path):
    records = _load()
    records = [r for r in records if r.get("mod_path") != mod_path]
    _save(records)


def clear_records():
    _save([])


def get_settings():
    _ensure_dir()
    if not os.path.isfile(SETTINGS_FILE):
        return {"lang": "zh"}
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            d = json.load(f)
            return d if isinstance(d, dict) else {"lang": "zh"}
    except Exception:
        return {"lang": "zh"}


def save_settings(settings):
    _ensure_dir()
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)
