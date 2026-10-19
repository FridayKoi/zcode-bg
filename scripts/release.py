#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""打包发布：zip（含仓库根 marketplace.json）+ sha256。"""
import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugins" / "zcode-bg"
DIST = ROOT / "dist"


def main():
    meta = json.loads((PLUGIN / ".zcode-plugin" / "plugin.json").read_text(encoding="utf-8"))
    ver = meta.get("version", "0.0.0")
    DIST.mkdir(exist_ok=True)
    out = DIST / f"zcode-bg-v{ver}.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(ROOT / "marketplace.json", "marketplace.json")
        for f in PLUGIN.rglob("*"):
            if not f.is_file():
                continue
            if "__pycache__" in f.parts or f.suffix == ".pyc":
                continue
            if f.name in ("config.json", "state.json"):
                continue
            z.write(f, f.relative_to(ROOT))
    sha = hashlib.sha256(out.read_bytes()).hexdigest()
    print(f"artifact: {out.relative_to(ROOT)}  ({out.stat().st_size} bytes)")
    print(f"sha256:   {sha}")
    print()
    print("发布提示：把 zip 作为 GitHub Release 资产上传，并在 #releases 分支的")
    print("marketplace.json 中把插件 source 指向该 zip 的下载地址（附加 sha256 字段）。")


if __name__ == "__main__":
    main()
