#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""zcode-bg：ZCode 桌面端壁纸与半透明主题补丁工具。

机制（借鉴 zcode-background-diy，MIT License）：
  Electron 启动时优先加载 resources/app.asar，其次才加载 resources/app/ 目录。
  应用 = 解包 asar 到 app/ → 在解包目录注入壁纸与 CSS → 把 app.asar 改名为 app.asar.disabled。
  回滚 = 把 app.asar.disabled 改名回来。本工具从不改写 app.asar 的内容。

子命令：
  detect    只读检查当前状态
  apply     应用壁纸主题（要求 ZCode 已完全退出）
  rollback  还原 app.asar（要求 ZCode 已完全退出）

本机默认安装路径为自定义目录，若移动了 ZCode，用 --asar 指定新位置的
resources/app.asar 即可。路径解析顺序：--asar 参数 → ZCODE_ASAR 环境变量 →
插件根目录 config.json 的 asar_path → 常见安装位置 → 运行中的 ZCode 进程。
所有改动都可以用 rollback 一键还原。
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# ---------- 固定配置 ----------
ASAR_NPX_PKG = "@electron/asar@4.3.1"          # 解包工具固定版本，避免 npx 每次浮动
PLUGIN_DIR = Path(__file__).resolve().parent.parent   # 插件根目录
CONFIG_FILE = PLUGIN_DIR / "config.json"       # 可选：{"asar_path": "..."}
IMG_EXTS = {"jpg", "jpeg", "png", "webp", "gif", "bmp"}


def _asar_candidates():
    """按优先级生成候选路径：环境变量 → 插件配置 → 常见安装位置 → 运行中进程。"""
    out, seen = [], set()

    def add(p):
        try:
            p = Path(p)
        except Exception:
            return
        key = str(p).lower()
        if key not in seen:
            seen.add(key)
            out.append(p)

    env = os.environ.get("ZCODE_ASAR")
    if env:
        add(env)
    try:
        cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        if cfg.get("asar_path"):
            add(cfg["asar_path"])
    except Exception:
        pass
    la = os.environ.get("LOCALAPPDATA")
    pf = os.environ.get("ProgramFiles")
    if la:
        add(Path(la) / "Programs" / "ZCode" / "resources" / "app.asar")
    if pf:
        add(Path(pf) / "ZCode" / "resources" / "app.asar")
    for letter in "CDEFGH":
        add(Path(f"{letter}:/ZCode/resources/app.asar"))
        add(Path(f"{letter}:/Program Files/ZCode/resources/app.asar"))
        add(Path(f"{letter}:/App tools/ZCode/resources/app.asar"))
    try:  # Windows：按运行中进程的 exe 位置定位（最准）
        r = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "(Get-Process ZCode -ErrorAction SilentlyContinue | Select-Object -First 1).Path"],
            capture_output=True, timeout=6)
        exe = (r.stdout or b"").decode("utf-8", errors="ignore").strip()
        if exe:
            add(Path(exe).parent / "resources" / "app.asar")
    except Exception:
        pass
    return out


def resolve_asar(explicit: str | None = None) -> Path | None:
    if explicit:
        p = Path(explicit)
        return p if (p.exists() or p.with_name(p.name + ".disabled").exists()) else None
    for cand in _asar_candidates():
        try:
            # 补丁启用时 app.asar 会改名为 app.asar.disabled，两者都算有效安装
            if cand.exists() or cand.with_name(cand.name + ".disabled").exists():
                return (cand.resolve() if cand.exists() else cand)
        except Exception:
            continue
    return None

# ---------- 预设（v0.7：色调分离架构） ----------
# 令牌只写"rgba(色调, alpha滑杆)"：色调由主题决定（深色=暗灰、浅色=亮白），
# 滑杆通过 --zcode-bg-a-* 调 alpha，深浅模式都自动可读。
PRESETS = {
    "subtle":    {"background": .55, "card": .68, "sidebar": .62, "menu": .72,
                  "input": .75, "surface": .60, "overlay": .16},
    "balanced":  {"background": .42, "card": .55, "sidebar": .50, "menu": .60,
                  "input": .62, "surface": .48, "overlay": .10},
    "immersive": {"background": .28, "card": .40, "sidebar": .34, "menu": .45,
                  "input": .52, "surface": .34, "overlay": .06},
}
# 每令牌独立色调：深色模式恢复原底色观感；浅色模式用白色系保证深色文字可读
TINTS = {
    "dark":  {"background": "22, 22, 22", "card": "43, 43, 43", "sidebar": "30, 30, 32",
              "menu": "43, 43, 43", "input": "43, 43, 43", "surface": "13, 13, 13"},
    "light": {"background": "250, 250, 252", "card": "255, 255, 255", "sidebar": "248, 248, 250",
              "menu": "255, 255, 255", "input": "255, 255, 255", "surface": "255, 255, 255"},
}


def build_css(ext: str, preset: str, overrides: dict | None = None) -> str:
    a = dict(PRESETS[preset])
    for k, v in (overrides or {}).items():   # 手动微调覆盖（0~0.95）
        if k in a:
            a[k] = round(max(0.0, min(0.95, v)), 2)

    def tok(name: str) -> str:
        return f"rgba(var(--zcode-bg-tint-{name}), var(--zcode-bg-a-{name}, {a[name]}))"

    tint_dark = "\n".join(f"  --zcode-bg-tint-{k}: {v};" for k, v in TINTS["dark"].items())
    tint_dark += "\n  --zcode-bg-overlay-tint: 0, 0, 0;\n  --zcode-bg-overlay-add: 0;"
    tint_light = "\n".join(f"  --zcode-bg-tint-{k}: {v};" for k, v in TINTS["light"].items())
    tint_light += "\n  --zcode-bg-overlay-tint: 255, 255, 255;\n  --zcode-bg-overlay-add: .15;"

    return f"""/* zcode-bg 生成的主题 CSS v0.8（preset={preset}，壁纸=zcode-bg.{ext}）
 * 色调分离：每令牌有独立的深/浅色调，滑杆只调 alpha（--zcode-bg-a-*）。
 */

html {{
  background: url("./zcode-bg.{ext}") center / cover no-repeat fixed !important;
  background-color: #151515 !important;
}}

html, body, #root, #app, .app, body > div:first-of-type {{
  background-color: transparent !important;
}}

html, .dark, .theme-zai-dark {{
{tint_dark}
}}

html:not(.dark):not(.theme-zai-dark) {{
{tint_light}
}}

html {{
  --color-background: {tok("background")} !important;
  --color-background-alt: {tok("background")} !important;
  --color-background-win-alt: {tok("background")} !important;
  --color-card: {tok("card")} !important;
  --color-card-selected: {tok("card")} !important;
  --color-sidebar: {tok("sidebar")} !important;
  --color-header: {tok("background")} !important;
  --color-panel: {tok("background")} !important;
  --color-menu: {tok("menu")} !important;
  --color-popover: {tok("menu")} !important;
  --color-input: {tok("input")} !important;
  --color-input-focused: {tok("input")} !important;
  --color-surface: {tok("surface")} !important;
  --color-neutral-950: {tok("sidebar")} !important;
  --color-neutral-900: {tok("background")} !important;
  --color-border: rgba(128, 128, 138, .22) !important;
  --color-border-hover: rgba(128, 128, 138, .34) !important;
  --color-hover: rgba(128, 128, 138, .14) !important;
  --color-surface-hover: rgba(128, 128, 138, .14) !important;
  --zcode-bg-sidebar: {a["sidebar"]};
  --zcode-bg-overlay: {a["overlay"]};
}}

body::before {{
  content: "";
  position: fixed;
  inset: 0;
  pointer-events: none;
  background: rgba(var(--zcode-bg-overlay-tint, 0, 0, 0),
    calc(var(--zcode-bg-overlay, {a["overlay"]}) + var(--zcode-bg-overlay-add, 0)));
  z-index: -1;
}}
"""


# ---------- 热更新引擎：每 2 秒重载 zcode-bg.css，改动免重启生效 ----------
HOT_SNIPPET = (
    '<script id="zcode-bg-hot">\n'
    "(function(){\n"
    "  var link = document.querySelector('link[href*=\"zcode-bg.css\"]');\n"
    "  if (!link) return;\n"
    "  setInterval(function(){ link.setAttribute('href', './zcode-bg.css?v=' + Date.now()); }, 2000);\n"
    "})();\n"
    "</script>"
)

STATE = Path(__file__).resolve().parent / "state.json"


def load_state() -> dict:
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_state(s: dict):
    STATE.write_text(json.dumps(s, ensure_ascii=False, indent=2), encoding="utf-8")


def renderer_dir(asar_arg):
    asar, resources, app = paths(asar_arg)
    renderer = app / "out" / "renderer"
    if not (app / "package.json").exists() or not (renderer / "index.html").exists():
        die("未找到解包目录或渲染层。请先执行 apply 启用补丁")
    return renderer


def regen_css(renderer: Path, state: dict):
    css = build_css(state.get("wallpaper_ext", "jpg"),
                    state.get("preset", "balanced"),
                    state.get("overrides"))
    (renderer / "zcode-bg.css").write_text(css, encoding="utf-8")


def hot_engine(a):
    """把 CSS 自动重载脚本与设置面板装进解包目录（幂等，重启一次后生效）。"""
    renderer = renderer_dir(a.asar)
    index = renderer / "index.html"
    html = index.read_text(encoding="utf-8", errors="replace")
    changed = False
    if 'id="zcode-bg-hot"' not in html:
        html = html.replace("</head>", HOT_SNIPPET + "\n  </head>", 1)
        changed = True
    panel_src = Path(__file__).resolve().parent.parent / "assets" / "zcode-bg-panel.js"
    if panel_src.exists():
        shutil.copy2(panel_src, renderer / "zcode-bg-panel.js")
        if "zcode-bg-panel.js" not in html:
            html = html.replace("</head>",
                '    <script defer src="./zcode-bg-panel.js"></script>\n  </head>', 1)
            changed = True
        print("设置面板已就位（右上角 ⚙ 按钮）")
    else:
        print(f"[提示] 找不到面板文件 {panel_src}，本次只装了 CSS 热重载")
    if changed:
        index.write_text(html, encoding="utf-8")
    if not changed and panel_src.exists():
        print("热更新引擎与面板此前已安装，无需重复")
    else:
        print("重启一次 ZCode 后：CSS 改动约 2 秒生效，⚙ 面板可实时调参（localStorage 记忆）")


def hot_preset(a):
    if a.name not in PRESETS:
        die(f"preset 只能是 {', '.join(PRESETS)}")
    renderer = renderer_dir(a.asar)
    s = load_state()
    s["preset"] = a.name
    save_state(s)
    regen_css(renderer, s)
    print(f"已切换 preset -> {a.name}（热更新引擎就位时约 2 秒内生效）")


def hot_wallpaper(a):
    renderer = renderer_dir(a.asar)
    src = Path(a.path).resolve()
    if not src.exists():
        die(f"图片不存在：{src}")
    ext = src.suffix.lower().lstrip(".")
    if ext not in IMG_EXTS:
        die(f"不支持的图片格式 .{ext}")
    s = load_state()
    old_ext = s.get("wallpaper_ext", "jpg")
    shutil.copy2(src, renderer / f"zcode-bg.{ext}")
    if ext != old_ext:   # 清理旧格式壁纸，避免残留
        old = renderer / f"zcode-bg.{old_ext}"
        if old.exists():
            old.unlink()
    s["wallpaper_ext"] = ext
    save_state(s)
    regen_css(renderer, s)
    print(f"壁纸已切换为 {src.name}（热更新引擎就位时约 2 秒内生效）")


def hot_alpha(a):
    renderer = renderer_dir(a.asar)
    s = load_state()
    ov = s.get("overrides", {})
    if a.reset:
        ov = {}
    else:
        for item in a.kv:
            if "=" not in item:
                die(f"格式应为 键=数值，例如 panel=0.5；收到：{item}")
            k, v = item.split("=", 1)
            try:
                ov[k.strip()] = float(v)
            except ValueError:
                die(f"数值不合法：{item}")
    s["overrides"] = ov
    save_state(s)
    regen_css(renderer, s)
    if ov:
        print("当前微调覆盖：" + ", ".join(f"{k}={v}" for k, v in sorted(ov.items())))
    else:
        print("已清除全部微调，回到预设值")
    print("可调键：background(工作区底), card, sidebar(侧栏独立底色), menu, input, surface, overlay")


def zcode_running() -> bool:
    # tasklist 在中文 Windows 输出 GBK，按字节接收后宽容解码，避免静默误判
    r = subprocess.run(["tasklist", "/FI", "IMAGENAME eq ZCode.exe"],
                       capture_output=True)
    out = (r.stdout or b"").decode("gbk", errors="ignore")
    return "ZCode.exe" in out


def statusbar_injected(app: Path):
    """检查解包目录里是否保留了状态条的注入（共存验证）。"""
    try:
        pkg = json.loads((app / "package.json").read_text(encoding="utf-8"))
        main_file = app / pkg["main"]
        text = main_file.read_text(encoding="utf-8", errors="replace")
        return ("inject-main" in text) or ("zusage" in text)
    except Exception:
        return None


def paths(asar_arg: str | None):
    asar = resolve_asar(asar_arg)
    if asar is None:
        die("未找到 ZCode 安装位置。请用 --asar 指定 resources/app.asar 的路径，"
            "或在插件根目录的 config.json 写入 {\"asar_path\": \"...\"}，"
            "或设置环境变量 ZCODE_ASAR")
    resources = asar.parent
    return asar, resources, resources / "app"


def die(msg: str):
    print(f"[失败] {msg}")
    sys.exit(1)


def npx_exe() -> str:
    found = shutil.which("npx") or shutil.which("npx.cmd")
    if not found:
        die("需要 Node.js 的 npx 来解包 asar（本机已装 node，请检查 PATH）")
    return found


# ---------- 子命令 ----------
def cmd_detect(a):
    asar, resources, app = paths(a.asar)
    renderer = app / "out" / "renderer"
    state = {
        "asar_path": str(asar),
        "asar_exists": asar.exists(),
        "patch_enabled(app.asar.disabled)": asar.with_name("app.asar.disabled").exists(),
        "unpacked_app_present": (app / "package.json").exists(),
        "renderer_index_present": (renderer / "index.html").exists(),
        "bg_css_present": (renderer / "zcode-bg.css").exists(),
        "zcode_running": zcode_running(),
        "statusbar_injected_in_unpacked": statusbar_injected(app) if (app / "package.json").exists() else None,
        "backups": sorted(x.name for x in resources.glob("app.asar.backup.*")),
    }
    print(json.dumps(state, ensure_ascii=False, indent=2))


def cmd_apply(a):
    asar, resources, app = paths(a.asar)
    disabled = asar.with_name("app.asar.disabled")
    renderer = app / "out" / "renderer"
    index = renderer / "index.html"

    if zcode_running():
        die("ZCode 正在运行。请先完全退出（托盘右键退出），再执行本命令")
    if disabled.exists():
        die("补丁已启用（app.asar.disabled 已存在）。如需换主题/换图，请先 rollback 再 apply")
    if not asar.exists():
        die(f"找不到 {asar}。ZCode 换了安装位置的话，用 --asar 指定新的 resources/app.asar")
    wallpaper = Path(a.wallpaper).resolve()
    if not wallpaper.exists():
        die(f"壁纸文件不存在：{wallpaper}")
    ext = wallpaper.suffix.lower().lstrip(".")
    if ext not in IMG_EXTS:
        die(f"不支持的图片格式 .{ext}，可用：{', '.join(sorted(IMG_EXTS))}")
    if a.preset not in PRESETS:
        die(f"preset 只能是 {', '.join(PRESETS)}")

    # 1) 备份原 asar（按日期，同日不重复备份）
    bak = resources / f"app.asar.backup.{date.today():%Y%m%d}"
    if not bak.exists():
        shutil.copy2(asar, bak)
        print(f"[1/5] 已备份原 asar -> {bak.name}")
    else:
        print(f"[1/5] 今日备份已存在，跳过（{bak.name}）")

    # 2) 解包（总是重新解包，保证与当前客户端版本同步；状态条注入行会原样保留）
    if app.exists():
        shutil.rmtree(app)
    npx = npx_exe()
    r = subprocess.run([npx, "--yes", ASAR_NPX_PKG, "extract", str(asar), str(app)],
                       capture_output=True)
    err = (r.stderr or b"").decode("utf-8", errors="ignore")
    if r.returncode != 0 or not index.exists():
        die(f"解包失败（exit={r.returncode}）或渲染层结构不符：{err[-300:]}")
    print(f"[2/5] 已解包 asar -> {app}（含状态条注入：{statusbar_injected(app)}）")

    # 3) 壁纸放进渲染层目录，CSS 用相对路径引用（规避协议/CSP 问题）
    shutil.copy2(wallpaper, renderer / f"zcode-bg.{ext}")
    print(f"[3/5] 壁纸已就位 -> renderer/zcode-bg.{ext}")

    # 4) 写 CSS（--css 指定自定义样式时用之，否则按预设生成）
    css_target = renderer / "zcode-bg.css"
    if a.css:
        shutil.copy2(Path(a.css).resolve(), css_target)
    else:
        css_target.write_text(build_css(ext, a.preset), encoding="utf-8")
    print(f"[4/5] CSS 已写入（{'自定义' if a.css else 'preset=' + a.preset}）")

    # 5) 在 index.html 注入样式表链接与热更新引擎，然后停用 asar 让解包目录生效
    html = index.read_text(encoding="utf-8", errors="replace")
    changed = False
    if 'href="./zcode-bg.css"' not in html:
        html = html.replace("</head>", '    <link rel="stylesheet" href="./zcode-bg.css">\n  </head>', 1)
        changed = True
    if 'id="zcode-bg-hot"' not in html:
        html = html.replace("</head>", HOT_SNIPPET + "\n  </head>", 1)
        changed = True
    panel_src = Path(__file__).resolve().parent.parent / "assets" / "zcode-bg-panel.js"
    if panel_src.exists():
        shutil.copy2(panel_src, renderer / "zcode-bg-panel.js")
        if "zcode-bg-panel.js" not in html:
            html = html.replace("</head>",
                '    <script defer src="./zcode-bg-panel.js"></script>\n  </head>', 1)
            changed = True
    if changed:
        index.write_text(html, encoding="utf-8")
    asar.rename(disabled)
    save_state({"wallpaper_ext": ext, "preset": a.preset, "overrides": {}})
    print(f"[5/5] 完成：app.asar 已停用，解包目录生效（含热更新引擎）")
    print("现在可以启动 ZCode 查看效果；换图/调参用 hot 子命令免重启，rollback 随时还原。")


def cmd_rollback(a):
    asar, resources, app = paths(a.asar)
    disabled = asar.with_name("app.asar.disabled")
    if zcode_running():
        die("ZCode 正在运行。请先完全退出（托盘右键退出），再执行本命令")
    if not disabled.exists():
        die("没有找到 app.asar.disabled，说明当前没有启用的背景补丁")
    disabled.rename(asar)
    print(f"已还原：app.asar.disabled -> app.asar")
    print(f"解包目录 {app} 保留未动（不影响运行，下次 apply 会重新解包覆盖）")


def main():
    ap = argparse.ArgumentParser(description="zcode-bg 背景主题补丁工具")
    ap.add_argument("--asar", help="resources/app.asar 的路径（默认本机安装位置）")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("detect", help="只读检查状态")
    aply = sub.add_parser("apply", help="应用壁纸主题")
    aply.add_argument("--wallpaper", required=True, help="壁纸图片路径")
    aply.add_argument("--preset", default="balanced",
                      choices=list(PRESETS), help="透明度预设档位")
    aply.add_argument("--css", help="使用自定义 CSS 替代预设生成")
    sub.add_parser("rollback", help="还原 app.asar")
    hot = sub.add_parser("hot", help="免重启的实时调整（需先装热更新引擎并重启过一次）")
    hot_sub = hot.add_subparsers(dest="hotcmd", required=True)
    hot_sub.add_parser("engine", help="把热更新引擎注入 index.html").set_defaults(func=hot_engine)
    hp = hot_sub.add_parser("preset", help="切换透明度档位")
    hp.add_argument("--name", required=True, choices=list(PRESETS))
    hp.set_defaults(func=hot_preset)
    hw = hot_sub.add_parser("wallpaper", help="热切换壁纸图片")
    hw.add_argument("--path", required=True)
    hw.set_defaults(func=hot_wallpaper)
    ha = hot_sub.add_parser("alpha", help="微调单个透明度，如 panel=0.5；--reset 清除")
    ha.add_argument("kv", nargs="*", help="键=数值，可多个；键见 COLORS 与 overlay")
    ha.add_argument("--reset", action="store_true")
    ha.set_defaults(func=hot_alpha)
    a = ap.parse_args()
    if a.cmd == "hot":
        a.func(a)
    else:
        {"detect": cmd_detect, "apply": cmd_apply, "rollback": cmd_rollback}[a.cmd](a)


if __name__ == "__main__":
    main()
