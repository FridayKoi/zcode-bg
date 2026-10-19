---
description: 免重启热切换背景壁纸图片
argument-hint: [图片完整路径]
---

运行 `python "${ZCODE_PLUGIN_ROOT}/scripts/bg_patch.py" hot wallpaper --path "$ARGUMENTS"`
（参数为空时向用户要图片路径）。
支持 jpg/jpeg/png/webp/gif/bmp。成功后告知约 2 秒生效。
