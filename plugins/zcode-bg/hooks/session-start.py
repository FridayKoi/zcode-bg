#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SessionStart 钩子：检测客户端更新导致的主题失效，提醒用户运行 /bg-apply。

判定：resources 下同时存在 app.asar 与 app.asar.disabled ——
这是 ZCode 自动更新后的典型状态（新 asar 已就位，旧的补丁 asar 残留）。
任何异常都静默处理，绝不输出非 JSON 内容、绝不影响会话。
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    # 协议要求：消费 stdin（内容不用）
    try:
        sys.stdin.read()
    except Exception:
        pass

    out = {"suppressOutput": True}
    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        import bg_patch as bp
        asar = bp.resolve_asar(None)
        if asar and asar.exists() and asar.with_name("app.asar.disabled").exists():
            msg = ("zcode-bg 提醒：检测到 ZCode 客户端已更新，背景主题注入已失效。"
                   "请在对话框输入 /bg-apply，按弹出的进度窗口提示完全退出 ZCode，"
                   "窗口会自动完成恢复，之后重新打开即可。")
            out["systemMessage"] = msg
            out["hookSpecificOutput"] = {
                "hookEventName": "SessionStart",
                "additionalContext": msg,
            }
    except Exception:
        pass
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
