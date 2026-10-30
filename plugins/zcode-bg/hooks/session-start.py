#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SessionStart 钩子：客户端更新后自动恢复主题。

判定：resources 下同时存在 app.asar 与 app.asar.disabled（ZCode 自动更新后的典型状态）。
动作：弹出一个可见的恢复窗口（apply --wait），用户完全退出 ZCode 后自动完成
      “归档旧遗留 → 解包新 asar → 注入主题 → 停用 asar”，重开即恢复。
      （面板启动后会用自己的 localStorage 壁纸覆盖默认壁纸，自定义壁纸不丢。）
限流：10 分钟内只弹一次（锁文件放在 %LOCALAPPDATA%/zcode-bg/auto-apply.lock）。
任何异常都静默处理，不影响会话。
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCK = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "zcode-bg" / "auto-apply.lock"


def main():
    # 协议要求：消费 stdin
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
                fresh = (time.time() - LOCK.stat().st_mtime) < 600
        except Exception:
            fresh = False

        spawned = False
        if not fresh:
            try:
                LOCK.parent.mkdir(parents=True, exist_ok=True)
                LOCK.write_text(str(time.time()), encoding="utf-8")
                subprocess.Popen(
                    [sys.executable, str(ROOT / "scripts" / "bg_patch.py"),
                     "--asar", str(asar), "apply", "--wait"],
                    creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0))
                spawned = True
            except Exception:
                pass

        if spawned:
            msg = ("zcode-bg：检测到 ZCode 客户端已更新，主题注入已失效。"
                   "已自动弹出恢复窗口——请完全退出 ZCode，窗口会自动完成恢复，"
                   "之后重新打开即可（你的壁纸和参数都会保留）。")
        else:
            msg = ("zcode-bg：检测到 ZCode 客户端已更新，主题注入已失效。"
                   "请完全退出 ZCode 后运行 /bg-apply 恢复；"
                   "若已有恢复窗口在等待，直接退出即可。")
        out["systemMessage"] = msg
        out["hookSpecificOutput"] = {"hookEventName": "SessionStart", "additionalContext": msg}
    except Exception:
        pass
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
