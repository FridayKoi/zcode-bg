---
description: 查看 ZCode 背景主题与补丁状态（只读，不改动任何文件）
---

运行 `python "${ZCODE_PLUGIN_ROOT}/scripts/bg_patch.py" detect`，
把 JSON 结果翻译成大白话告诉用户：

- 补丁是否启用（app.asar.disabled 存在 = 背景主题生效中）
- 解包目录是否存在、壁纸 CSS 是否就位
- ZCode 是否正在运行
- 状态条插件注入是否保留在解包目录中（共存检查）
- 有哪些日期备份可用
