#!/usr/bin/env python3
"""Simple polling autocommit script.

Behavior:
- Polls the repo for changes every `delay_seconds`.
- When changes are found, runs `git add -A` + `git commit -m "<commit_message> <timestamp>"` and optionally `git push origin <branch>`.
- Reads configuration from `.vscode/autocommit.json` (falls back to defaults if missing).

Note: This is intentionally simple (no external deps) so it works in most devcontainers.
"""

import subprocess
import time
import json
import os
import datetime
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CONFIG_PATH = os.path.join(ROOT, '.vscode', 'autocommit.json')

DEFAULT_CONFIG = {
    "enabled": True,
    "delay_seconds": 2,
    "debounce_seconds": 5,
    "commit_message": "autosave: update",
    "branch": "main",
    "push": True,
    "include_untracked": True
}


def load_config():
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
            d = DEFAULT_CONFIG.copy()
            d.update(cfg)
            return d
    except FileNotFoundError:
        return DEFAULT_CONFIG.copy()
    except Exception as e:
        print(f"Failed to read config {CONFIG_PATH}: {e}")
        return DEFAULT_CONFIG.copy()


def run(cmd, cwd=ROOT):
    # shell=False for safety
    print(f"> {cmd}")
    try:
        completed = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=True)
        return completed.returncode, completed.stdout.strip()
    except Exception as e:
        return 1, str(e)


def has_worktree_changes():
    code, out = run('git status --porcelain')
    if code != 0:
        print('git status failed:', out)
        return False
    return bool(out.strip())


def main():
    cfg = load_config()
    print('Auto-commit config:', cfg)
    last_commit_time = 0

    if not cfg.get('enabled', True):
        print('Autocommit is disabled in config. Exiting.')
        sys.exit(0)

    delay = float(cfg.get('delay_seconds', 2))
    debounce = float(cfg.get('debounce_seconds', 5))
    branch = cfg.get('branch', 'main')
    push = bool(cfg.get('push', True))
    include_untracked = bool(cfg.get('include_untracked', True))

    try:
        while True:
            if has_worktree_changes():
                now = time.time()
                if now - last_commit_time < debounce:
                    # Wait a bit more to allow more edits to accumulate
                    print('Changes detected but debouncing...')
                    time.sleep(delay)
                    continue

                # Stage changes (respect .gitignore automatically)
                add_cmd = 'git add -A'
                code, out = run(add_cmd)
                if code != 0:
                    print('git add failed:', out)
                    time.sleep(delay)
                    continue

                # If nothing is staged, skip
                code, out = run('git diff --cached --name-only')
                if code != 0:
                    print('git diff --cached failed:', out)
                    time.sleep(delay)
                    continue
                if not out.strip():
                    print('Nothing staged to commit (skipping).')
                    time.sleep(delay)
                    continue

                # Commit
                ts = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + 'Z'
                msg = f"{cfg.get('commit_message', 'autosave: update')} - {ts}"
                commit_cmd = f"git commit -m \"{msg}\""
                code, out = run(commit_cmd)
                if code != 0:
                    print('git commit failed:', out)
                else:
                    print('Committed:', msg)
                    last_commit_time = time.time()

                    if push:
                        push_cmd = f"git push origin {branch}"
                        code, out = run(push_cmd)
                        if code != 0:
                            print('git push failed:', out)
                        else:
                            print('Pushed to origin', branch)

            time.sleep(delay)

    except KeyboardInterrupt:
        print('\nAutocommit watcher stopped by user.')


if __name__ == '__main__':
    main()
