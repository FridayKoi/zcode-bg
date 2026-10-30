#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SessionStart 钩子：客户端更新后自动恢复主题（v0.11.1）。

判定：resources 下同时存在 app.asar 与 app.asar.disabled。
动作：生成 restore.cmd（等待退出 → apply → 自删锁），再用 explorer.exe 拉起，
      使窗口脱离 ZCode 的进程树，退出 ZCode 时不会被一起杀掉。
限流：锁文件 5 分钟内只弹一次；恢复脚本结束后自行删除锁。
任何异常都静默处理，不影响会话。
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "zcode-bg"
LOCK = BASE / "auto-apply.lock"
CMD = BASE / "restore.cmd"


def main():
    try:
        sys.stdin.read()
    except Exception:
        pass

    out = {"suppressOutput": True}
    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        import bg_patch as bp

        asar = bp.resolve_asar(None)
        stale = bool(asar and asar.exists() and asar.with_name("app.asar.disabled").exists())
        if not stale:
            print(json.dumps(out, ensure_ascii=False))
            return

        fresh = False
        try:
            if LOCK.exists():
                fresh = (time.time() - LOCK.stat().st_mtime) < 300
        except Exception:
            fresh = False

        spawned = False
        if not fresh:
            try:
                BASE.mkdir(parents=True, exist_ok=True)
                script = ROOT / "scripts" / "bg_patch.py"
                CMD.write_text(
                    "@echo off\r\n"
                    "chcp 65001 >nul\r\n"
                    "echo zcode-bg restore: waiting for ZCode to exit...\r\n"
                    f'python "{script}" --asar "{asar}" apply --wait --preset balanced\r\n'
                    "del /q \"%LOCALAPPDATA%\\zcode-bg\\auto-apply.lock\" 2>nul\r\n"
                    "echo.\r\n"
                    "pause\r\n",
                    encoding="utf-8")
                LOCK.write_text(str(time.time()), encoding="utf-8")
                # 通过资源管理器启动：脱离 ZCode 进程树，退出时不会被杀
                subprocess.Popen(["explorer.exe", str(CMD)])
                spawned = True
            except Exception:
                try:
                    subprocess.Popen(
                        [sys.executable, str(ROOT / "scripts" / "bg_patch.py"),
                         "--asar", str(asar), "apply", "--wait"],
                        creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0))
                    spawned = True
                except Exception:
                    pass

        if spawned:
            msg = ("zcode-bg：检测到 ZCode 客户端已更新，主题注入已失效。"
                   "已自动打开恢复窗口——请完全退出 ZCode，窗口会自动完成恢复，"
                   "之后重新打开即可（壁纸和参数都会保留）。")
        else:
            msg = ("zcode-bg：检测到 ZCode 客户端已更新，主题注入已失效。"
                   "请完全退出 ZCode 后运行 /bg-apply 恢复。")
        out["systemMessage"] = msg
        out["hookSpecificOutput"] = {"hookEventName": "SessionStart", "additionalContext": msg}
    except Exception:
        pass
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
